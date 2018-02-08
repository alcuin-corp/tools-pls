from target import Target

class Tenant:
    def __init__(self, tenant_id: str, name: str, targets: list):
        self.tenant_id = tenant_id
        self.name = name
        self.targets = targets
