from subprocess import call
import logger
import pyodbc

class Server(logger.Logger):
    def __init__(self, server_id: str, data_source: str, backup_directory: str, user_id: str=None, password: str=None):
        self.server_id = server_id
        self.user_id = user_id or 'sa'
        self.password = password or 'P@ssw0rd'
        self.data_source = data_source
        self.backup_directory = backup_directory

    def build_connection_string(self, database=None, user_id=None, password=None):
        return f'DRIVER={{ODBC Driver 13 for SQL Server}};SERVER={self.data_source};DATABASE={database or "master"};UID={user_id or "sa"};PWD={password or "P@ssw0rd"}'

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

    def restore(self, db_name, backup_file_name):
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
                self.ok('Database is on multi-user, switch to single user...')
                cur.execute(f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;")
                switched_to_single_mode = True
        except:
            self.error('Switch to multi-user failed.')
        finally:
            cur.close()
            cnx.close()

        self.run(f"RESTORE DATABASE [{db_name}] FROM  DISK = N'{self.backup_directory}/{backup_file_name}' WITH FILE = 1, NOUNLOAD, REPLACE, RECOVERY, STATS = 25;")
        self.ok('Restored successfully...')

        if switched_to_single_mode:
            self.run(f"ALTER DATABASE [{db_name}] SET MULTI_USER;")
            self.ok('Switch back to multi user state...')

    def backup(self, db_name, backup_file_name):
        self.run(f"BACKUP DATABASE [{db_name}] TO  DISK = N'{self.backup_directory}/{backup_file_name}' WITH NOFORMAT, INIT, NAME = N'{self.backup_directory}\\{db_name}-Full Database Backup', SKIP, NOREWIND;")
