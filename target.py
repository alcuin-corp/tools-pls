class Target:
    def __init__(self, db_name: str, backup_file_name: str, server_id: str, target_type: str):
        self.target_type = target_type
        self.server_id = server_id
        self.backup_file_name = backup_file_name
        self.db_name = db_name