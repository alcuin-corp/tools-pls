from subprocess import call


class Migrator:
    def __init__(self, migrator_exe: str, migration_dll: str):
        self.migrator_exe = migrator_exe
        self.migration_dll = migration_dll

    def migrate(self, datasource: str, db_name: str):
        call(
            f'{self.migrator_exe} SqlServer2005Dialect "Database={db_name};Data Source={datasource};'
            f'User Id=sa;Password=P@ssw0rd;" {self.migration_dll}')
