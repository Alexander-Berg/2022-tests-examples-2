# -*- coding: utf-8 -*-
import logging

from passport.backend.qa.test_user_service.tus_api.backend import (
    get_tus_consumer_by_account_uid,
    unlock_account,
)
from passport.backend.qa.test_user_service.tus_api.exceptions import UnlockAccountFailedError
from passport.backend.qa.test_user_service.tus_api.idm_backend import check_access_to_consumer
from passport.backend.qa.test_user_service.tus_api.validators import (
    EnvValidator,
    WeakUidValidator,
)
from passport.backend.qa.test_user_service.tus_api.views.base import Schema
from passport.backend.qa.test_user_service.tus_api.views.tus.tus_base import TusBaseView


log = logging.getLogger(__name__)


class UnlockAccountForm(Schema):
    uid = WeakUidValidator()
    env = EnvValidator(not_empty=True, if_missing='TEST', strip=True)


class UnlockAccount(TusBaseView):
    form = UnlockAccountForm

    def process_request(self):
        self.check_access()

        uid = self.form_values['uid']

        if not unlock_account(uid, self.form_values['env']):
            raise UnlockAccountFailedError('Unable to unlock account with uid %s' % uid)
        self.response_values = {
            'status': 'ok'
        }

    def check_access(self):
        tus_consumer = get_tus_consumer_by_account_uid(self.form_values['uid'], self.form_values['env'])
        check_access_to_consumer(self.requester_info['login'], tus_consumer)
        self.yasm_logger.log(
            client_login=self.requester_info['login'],
            tus_consumer=tus_consumer,
        )


__all__ = (
    'UnlockAccount',
)
