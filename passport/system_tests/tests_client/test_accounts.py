def account_with_different_password(env):
    """Аккаунт, пароль которого поменялся после сохранения в TUS. Новый пароль: simple123456"""
    account_uid = None
    if env == 'TEST':
        account_uid = '4039095074'
    elif env == 'PROD':
        account_uid = '1050393589'
    return account_uid


def deleted_account(env):
    """Аккаунт, который был удалён после сохранения в TUS"""
    account_uid = None
    if env == 'TEST':
        account_uid = '4039095100'
    elif env == 'PROD':
        account_uid = '1050399553'
    return account_uid


def account_from_other_consumer(env):
    """Аккаунт, к которому нет доступа. Сохранён в consumer=tus-tests-other с токеномм аккаунта robot-yateam-4-tests@"""
    account_uid = None
    if env == 'TEST':
        account_uid = '4039095172'
    elif env == 'PROD':
        account_uid = '1050452504'
    return account_uid
