from server import Server
import copy

class Tenant:
    def __init__(self, tenant_id: str, targets: list, name:str=None):
        self.name = name
        self.tenant_id = tenant_id
        self.targets = targets

def set_appname(server_provider, tenant: Tenant):
    if tenant.name:
        config_target = next((t for t in tenant.targets if t.target_type == 'config'), None)
        server = server_provider(config_target.server_id)
        if not config_target:
            raise Exception('Tenant has no config target!')
        
        server.run(
            f"UPDATE [{config_target.db_name}].dbo.Application "
            f"SET name = '{tenant.name}'")
