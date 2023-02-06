import json


class Account(object):

    def __init__(self, uid, login, password, locked_until=None, delete_at=None, env='TEST'):
        self.uid = uid
        self.login = login
        self.password = password
        self.locked_until = locked_until
        self.delete_at = delete_at
        self.env = env

    def __repr__(self):
        return json.dumps(self.__dict__)
