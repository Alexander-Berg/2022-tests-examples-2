# -*- coding: utf-8 -*-
from passport.backend.qa.test_user_service.tus_api.views.tus.bind_phone import BindPhone
from passport.backend.qa.test_user_service.tus_api.views.tus.create_account.portal import CreateAccountPortal
from passport.backend.qa.test_user_service.tus_api.views.tus.create_consumer import CreateTusConsumer
from passport.backend.qa.test_user_service.tus_api.views.tus.get_account import GetAccount
from passport.backend.qa.test_user_service.tus_api.views.tus.list_accounts import ListAccounts
from passport.backend.qa.test_user_service.tus_api.views.tus.ping import ping
from passport.backend.qa.test_user_service.tus_api.views.tus.remove_account import RemoveAccount
from passport.backend.qa.test_user_service.tus_api.views.tus.save_account import SaveAccount
from passport.backend.qa.test_user_service.tus_api.views.tus.unlock_account import UnlockAccount


__all__ = [
    'BindPhone',
    'CreateAccountPortal',
    'CreateTusConsumer',
    'GetAccount',
    'ping',
    'RemoveAccount',
    'SaveAccount',
    'UnlockAccount',
    'ListAccounts',
]
