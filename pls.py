import json
import argparse
import os
from subprocess import call

class Target:
    def __init__(self, db_name: str, backup_file_name: str):
        self.backup_file_name = backup_file_name
        self.db_name = db_name

class Tenant:
    def __init__(self, name: str, public_target: Target, config_target: Target):
        self.name = name
        self.public_target = public_target
        self.config_target = config_target

class Server:
    def __init__(self, name: str, backup_directory: str):
        self.name = name
        self.backup_directory = backup_directory

    def sqlcmd(self, query: str):
        call(f'sqlcmd -S {self.name} -Q "{query}"')

    def restore(self, db_name, backup_file_name):
        self.sqlcmd(f"ALTER DATABASE [{db_name}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE")
        self.sqlcmd(f"RESTORE DATABASE [{db_name}] FROM  DISK = N'{self.backup_directory}\\{backup_file_name}' WITH  FILE = 1,  NOUNLOAD,  REPLACE,  STATS = 25")
        self.sqlcmd(f"ALTER DATABASE [{db_name}] SET MULTI_USER")

    def backup(self, db_name, backup_file_name):
        self.sqlcmd(f"BACKUP DATABASE [{db_name}] TO  DISK = N'{self.backup_directory}\\{backup_file_name}' WITH NOFORMAT, INIT, NAME = N'{self.backup_directory}\\{db_name}-Full Database Backup', SKIP, NOREWIND;")

class Migrator:
    def __init__(self, server: Server, migrator_exe: str, migration_dll: str):
        self.server = server
        self.migrator_exe = migrator_exe
        self.migration_dll = migration_dll

    def migrate(self, db: str):
        call(f'{self.migrator_exe} SqlServer2005Dialect "Database={db};Data Source={self.server.name};User Id=sa;Password=P@ssw0rd;" {self.migration_dll}')

class Context:
    def __init__(self, filename: str):
        f = open(filename)
        self.config = json.load(f)
        self.tenants = []

        def build_target(dic):
            return Target(dic["db"], dic["backup"])

        def build_tenant(dic):
            return Tenant(
                dic["name"],
                build_target(dic["public"]),
                build_target(dic["config"]),                
            )

        for tenant in self.config["tenants"]:
            self.tenants.append(build_tenant(tenant))
        
        self.server = Server(
            self.config["server"],
            self.config["backup_directory"])

        self.config_migrator = Migrator(
            self.server,
            self.config["migrator_exe"],
            self.config["config_migration_dll"])
        
        self.public_migrator = Migrator(
            self.server,
            self.config["migrator_exe"],
            self.config["public_migration_dll"])

class bcolors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'

def color(text: str, color) -> str:
    return f'{color}{text}{bcolors.ENDC}'
def blue(text: str) -> str:
    return color(text, bcolors.BLUE)
def yellow(text: str) -> str:
    return color(text, bcolors.YELLOW)
def green(text: str) -> str:
    return color(text, bcolors.GREEN)

def log(message):
    def log_decorate(func):
        def func_wrapper(self, tenant):
            line = '-----------------------------------'
            print('\n' + line + '[[ ' + message + ' => ' + green(tenant.name) + ' ]]' + line)
            func(self, tenant)
        return func_wrapper
    return log_decorate

class Api(Context):

    @log('Migration started')
    def migrate_tenant(self, tenant: Tenant):
        self.config_migrator.migrate(tenant.config_target.db_name)
        self.public_migrator.migrate(tenant.public_target.db_name)
    
    def migrate(self):
        for tenant in self.tenants:
            self.migrate_tenant(tenant)

    def restore_target(self, target: Target):
        self.server.restore(target.db_name, target.backup_file_name)

    @log('Restore started')
    def restore_tenant(self, tenant: Tenant):
        self.restore_target(tenant.config_target)
        self.restore_target(tenant.public_target)
    
    def restore(self):
        for tenant in self.tenants:
            self.restore_tenant(tenant)

    def backup_target(self, target: Target):
        self.server.backup(target.db_name, target.backup_file_name)
    
    @log('Backup started')
    def backup_tenant(self, tenant: Tenant):
        self.backup_target(tenant.config_target)
        self.backup_target(tenant.public_target)
    
    def backup(self):
        for tenant in self.tenants:
            self.backup_tenant(tenant)
     
parser = argparse.ArgumentParser(description='PLS: Powerfull Lannister Script v2, manages applications.')
parser.add_argument('-c', '--config', help="Uses a specific config file (will be config.json by default).")

parser.add_argument('-m', '--migrate', action="store_true", help="Migrate the databases.")
parser.add_argument('-r', '--restore', action="store_true", help="Restore the databases from the backups.")
parser.add_argument('-b', '--backup', action="store_true", help="Creates new backups from the databases.")
parser.add_argument('-a', '--all', action="store_true", help="Executes all tasks.")

args = parser.parse_args()

path = args.config or "config.json"

if os.path.exists(path):
    api = Api(path)
    if args.restore or args.all:
        api.restore()
    if args.migrate or args.all:
        api.migrate()
    if args.backup or args.all:
        api.backup()    
else:
    print('Config file not found.')