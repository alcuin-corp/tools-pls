from subprocess import call

class Server:
    def __init__(self, server_id: str, data_source: str, backup_directory: str):
        self.server_id = server_id
        self.data_source = data_source
        self.backup_directory = backup_directory

    def sqlcmd(self, query: str):
        call(f'sqlcmd -S {self.data_source} -Q "{query}"')

    def restore(self, db_name, backup_file_name):
        self.sqlcmd(f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        self.sqlcmd(f"RESTORE DATABASE [{db_name}] FROM  DISK = N'{self.backup_directory}\\{backup_file_name}' WITH  FILE = 1,  NOUNLOAD,  REPLACE,  STATS = 25")
        self.sqlcmd(f"ALTER DATABASE [{db_name}] SET MULTI_USER")

    def backup(self, db_name, backup_file_name):
        self.sqlcmd(f"BACKUP DATABASE [{db_name}] TO  DISK = N'{self.backup_directory}\\{backup_file_name}' WITH NOFORMAT, INIT, NAME = N'{self.backup_directory}\\{db_name}-Full Database Backup', SKIP, NOREWIND;")
