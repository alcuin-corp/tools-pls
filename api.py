from dto import Tenant, Target
from context import Context
from log import log

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