class Target:
    def __init__(self, db_name: str, backup_filename: str, server_id: str, target_type: str):
        self.db_name = db_name
        self.target_type = target_type
        self.server_id = server_id
        self.backup_filename = backup_filename
