from server import Server
from subprocess import call

class Migrator:
    def __init__(self, server: Server, migrator_exe: str, migration_dll: str):
        self.server = server
        self.migrator_exe = migrator_exe
        self.migration_dll = migration_dll

    def migrate(self, db: str):
        call(f'{self.migrator_exe} SqlServer2005Dialect "Database={db};Data Source={self.server.name};User Id=sa;Password=P@ssw0rd;" {self.migration_dll}')
