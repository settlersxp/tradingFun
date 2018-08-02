class Database():
    def __init__(self, helper):
        self.db_name = helper.get_config_value('Database', 'dbName')
        self.password = helper.get_config_value('Database', 'password')
        self.user = helper.get_config_value('Database', 'user')
        self.port = helper.get_config_value('Database', 'port')
