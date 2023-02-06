# -*- coding: utf-8 -*-
from passport.backend.qa.test_user_service.tus_api.views.idm import (
    IdmAddRole,
    IdmGetAllRoles,
    IdmInfo,
    IdmRemoveRole,
)
from passport.backend.qa.test_user_service.tus_api.views.tus import (
    BindPhone,
    CreateAccountPortal,
    CreateTusConsumer,
    GetAccount,
    ListAccounts,
    ping,
    RemoveAccount,
    SaveAccount,
    UnlockAccount,
)


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
    'IdmAddRole',
    'IdmGetAllRoles',
    'IdmInfo',
    'IdmRemoveRole',
]
