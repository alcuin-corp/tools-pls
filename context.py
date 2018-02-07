from dto import Target, Tenant
from migrator import Migrator
from server import Server

class Context:
    def __init__(self, config: str):
        self.config = config
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