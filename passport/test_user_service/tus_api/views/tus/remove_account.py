# -*- coding: utf-8 -*-
import logging

from passport.backend.qa.test_user_service.tus_api.backend import (
    check_access_to_account,
    remove_user_from_tus_db,
)
from passport.backend.qa.test_user_service.tus_api.exceptions import RemoveAccountFailedError
from passport.backend.qa.test_user_service.tus_api.idm_backend import check_access_to_consumer
from passport.backend.qa.test_user_service.tus_api.settings import DEFAULT_TUS_CONSUMER
from passport.backend.qa.test_user_service.tus_api.validators import (
    EnvValidator,
    TusConsumer,
    WeakUidValidator,
)
from passport.backend.qa.test_user_service.tus_api.views.base import Schema
from passport.backend.qa.test_user_service.tus_api.views.tus.tus_base import TusBaseView


log = logging.getLogger(__name__)


class RemoveAccountForm(Schema):
    uid = WeakUidValidator()
    tus_consumer = TusConsumer(not_empty=True, if_missing=DEFAULT_TUS_CONSUMER, strip=True)
    env = EnvValidator(not_empty=True, if_missing='TEST', strip=True)


class RemoveAccount(TusBaseView):
    form = RemoveAccountForm

    def process_request(self):
        self.check_access()

        env = self.form_values['env']
        uid = self.form_values['uid']
        tus_consumer = self.form_values['tus_consumer']

        if not remove_user_from_tus_db(uid, tus_consumer, env):
            raise RemoveAccountFailedError('Failed to remove account with uid %s' % uid)
        self.response_values = {
            'status': 'ok'
        }

    def check_access(self):
        tus_consumer = self.form_values['tus_consumer']
        check_access_to_consumer(self.requester_info['login'], tus_consumer)
        check_access_to_account(self.form_values['uid'], tus_consumer, self.form_values['env'])
        self.yasm_logger.log(
            client_login=self.requester_info['login'],
            tus_consumer=tus_consumer,
        )


__all__ = (
    'RemoveAccount',
)
