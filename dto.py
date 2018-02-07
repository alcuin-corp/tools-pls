class Target:
    def __init__(self, db_name: str, backup_file_name: str):
        self.backup_file_name = backup_file_name
        self.db_name = db_name

class Tenant:
    def __init__(self, name: str, public_target: Target, config_target: Target):
        self.name = name
        self.public_target = public_target
        self.config_target = config_target