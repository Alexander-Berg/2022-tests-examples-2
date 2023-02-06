import random
import string


class Account(object):

    def __init__(self, uid, login, password, firstname=None, lastname=None, country=None, language=None,
                 locked_until=None):
        self.uid = uid
        self.login = login
        self.password = password
        self.firstname = firstname
        self.lastname = lastname
        self.country = country
        self.language = language
        self.locked_until = locked_until

    def __eq__(self, other):
        is_type_eq = type(other) == type(self)
        is_uid_eq = self.uid == other.uid
        is_login_eq = self.login == other.login
        is_pass_eq = self.password == other.password
        if not is_type_eq:
            return False
        if is_uid_eq and is_login_eq and is_pass_eq:
            return True
        return False


def get_account_from_response(response):
    return Account(**response)


def get_exist_account_in_test():
    return Account(
        uid='4038895344',
        login='yandex-team-37493-63331',
        password='xPwD.sh5F'
    )


def get_exist_account_in_prod():
    return Account(
        uid='1048515902',
        login='yandex-team-60280-30120',
        password='T7gf.R3M5'
    )


def _random_numeric(n_digits):
    return ''.join(random.choice(string.digits) for _ in range(n_digits))


def generate_login():
    return 'yandex-team-{0}.{1}'.format(_random_numeric(5), _random_numeric(5))


def get_passport_environment_for_env(env):
    env = env.upper()
    if env == 'TEST':
        return 'testing'
    elif env == 'PROD':
        return 'production'
    else:
        raise KeyError('Unknown environment')
