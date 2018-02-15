import pyodbc
from os.path import join, split, splitext

class Server:
    def __init__(self, data_source: str, install_path: str, server_id: str = None, user_id: str = None,
                 password: str = None):
        self.data_source = data_source
        self.user_id = user_id or 'sa'
        self.password = password or 'P@ssw0rd'
        self.server_id = server_id or data_source
        self.install_path = install_path
        self.backup_directory = join(install_path, 'Backup')
        self.data_directory = join(install_path, 'DATA')

    def build_connection_string(self, database=None, user_id=None, password=None):
        return f'DRIVER={{ODBC Driver 13 for SQL Server}};SERVER={self.data_source};' \
               f'DATABASE={database or "master"};UID={user_id or "sa"};PWD={password or "P@ssw0rd"}'

    def open_connexion(self, auto_commit=True):
        cnx = pyodbc.connect(self.build_connection_string(), autocommit=auto_commit)
        return cnx

    def run(self, proc):
        def execute_all_sets(cur):
            while cur.nextset():
                pass
        return self.with_cursor(proc, execute_all_sets)        

    def query_all(self, query):
        return self.with_cursor(query, lambda cur: cur.fetchall())

    def query_one(self, query):
        return self.with_cursor(query, lambda cur: cur.fetchone())

    def with_cursor(self, query, task):
        cnx = self.open_connexion()
        cur = cnx.cursor()
        try:
            cur.execute(query)
            return task(cur)
        finally:
            cur.close()
            cnx.close()                                       

    def backup(self, db_name: str, backup_filename: str):
        self.run(
            f"BACKUP DATABASE [{db_name}] "
            f"TO DISK = N'{join(self.backup_directory, backup_filename)}' "
            f"WITH NOFORMAT, INIT, SKIP, NOREWIND;")

    def is_db_multi_user(self, db_name: str):
        row = self.query_one(
            f"SELECT COUNT(*) FROM sys.databases "
            f"WHERE name = '{db_name}' "
            f"AND state != 6 "
            f"AND user_access_desc = 'MULTI_USER'")
        return row[0] > 0

    def switch_to_single_user_mode(self, db_name: str):
        if self.is_db_multi_user(db_name):
            self.run(f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;")

    def switch_to_multi_user_mode(self, db_name: str):
        if not self.is_db_multi_user(db_name):
            self.run(f"ALTER DATABASE [{db_name}] SET MULTI_USER;")

    def read_filelist_from_backup(self, backup_filename: str):
        for row in self.query_all(
            f"RESTORE FILELISTONLY "
            f"FROM DISK = N'{join(self.backup_directory, backup_filename)}'"):
            yield (row.LogicalName, row.PhysicalName)

    def relocate_logical_files(self, new_name: str, filelist: (str, str)):
        for (logical_name, physical_name) in filelist:
            (_, fname) = split(physical_name)
            (_, fext) = splitext(fname)
            yield (logical_name, join(self.data_directory, new_name + fext))

    def create_move_statements(self, db_name: str, backup_filename: str):
        filelist = self.read_filelist_from_backup(backup_filename)        
        pairs = self.relocate_logical_files(db_name, filelist)
        moves = []
        for (logical, physical) in pairs:
            moves.append(f"MOVE N'{logical}' TO N'{physical}'")
        return ', '.join(moves)
        
    def restore(self, db_name: str, backup_filename: str):
        self.switch_to_single_user_mode(db_name)
        task = (f"RESTORE DATABASE [{db_name}]"
                f" FROM DISK = N'{join(self.backup_directory, backup_filename)}'"
                f" WITH FILE = 1,"
                f" {self.create_move_statements(db_name, backup_filename)},"
                f" NOUNLOAD, REPLACE, RECOVERY, STATS = 25;")
        self.run(task)     
        self.switch_to_multi_user_mode(db_name)
