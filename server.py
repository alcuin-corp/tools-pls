import pyodbc
from os.path import join as pj, basename


class Server:
    def __init__(self, data_source: str, install_path: str, server_id: str = None, user_id: str = None,
                 password: str = None):
        self.data_source = data_source
        self.user_id = user_id or 'sa'
        self.password = password or 'P@ssw0rd'
        self.server_id = server_id or data_source
        self.install_path = install_path
        self.backup_directory = pj(install_path, 'Backup')
        self.data_directory = pj(install_path, 'DATA')

    def build_connection_string(self, database=None, user_id=None, password=None):
        return f'DRIVER={{ODBC Driver 13 for SQL Server}};SERVER={self.data_source};' \
               f'DATABASE={database or "master"};UID={user_id or "sa"};PWD={password or "P@ssw0rd"}'

    def open_connexion(self, auto_commit=True):
        cnx = pyodbc.connect(self.build_connection_string(), autocommit=auto_commit)
        return cnx

    def run(self, query):
        cnx = self.open_connexion()
        cur = cnx.cursor()
        try:
            cur.execute(query)
            while cur.nextset():
                pass
        finally:
            cur.close()
            cnx.close()

    def get_dbname(self, backup_file_name):
        cnx = self.open_connexion()
        cur = cnx.cursor()
        row = cur.execute(f"RESTORE HEADERONLY FROM DISK = '{pj(self.backup_directory, backup_file_name)}'").fetchone()
        return row.DatabaseName

    def get_filelist(self, backup_file_name):
        cnx = self.open_connexion()
        cur = cnx.cursor()
        file_list = cur.execute(f"RESTORE FILELISTONLY FROM DISK = '{pj(self.backup_directory, backup_file_name)}'")
        arr = []
        for item in file_list:
            arr.append({
                'logical': item.LogicalName,
                'physical': item.PhysicalName
            })
        return arr

    def build_move_clauses(self, backup_file_name):
        return ','.join(
            [f"MOVE N'{name['logical']}' TO N'{pj(self.data_directory, basename(name['physical']))}'" for name in
             self.get_filelist(backup_file_name)])

    def restore(self, backup_file_name):
        db_name = self.get_dbname(backup_file_name)
        cnx = self.open_connexion()
        cur = cnx.cursor()
        switched_to_single_mode = False
        try:
            result = cur.execute(f"""
                SELECT COUNT(*) FROM sys.databases
                WHERE name = '{db_name}'
                AND state != 6
                AND user_access_desc = 'MULTI_USER'            
            """).fetchone()
            if result[0] > 0:
                cur.execute(f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;")
                switched_to_single_mode = True
        finally:
            cur.close()
            cnx.close()

        move_clauses = self.build_move_clauses(backup_file_name)
        self.run(
            f"RESTORE DATABASE [{db_name}]"
            f" FROM  DISK = N'{pj(self.backup_directory, backup_file_name)}'"
            f" WITH FILE = 1, {move_clauses}, NOUNLOAD, REPLACE, RECOVERY, STATS = 25;")

        if switched_to_single_mode:
            self.run(f"ALTER DATABASE [{db_name}] SET MULTI_USER;")

    def backup(self, backup_file_name):
        files = self.get_filelist(backup_file_name)[0]
        db_name = self.get_dbname(backup_file_name)
        name = pj(self.backup_directory, basename(files['physical']) + '-Full Database Backup')
        self.run(
            f"BACKUP DATABASE [{db_name}]"
            f" TO DISK = N'{pj(self.backup_directory, backup_file_name)}'"
            f" WITH NOFORMAT, INIT, NAME = N'{name}', SKIP, NOREWIND;")
