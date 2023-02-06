# coding=utf-8
import logging

from passport.backend.qa.test_user_service.tus_api.backend import (
    get_passport_environment_for_response,
    get_saved_account,
    get_tus_consumer_by_account_uid,
)
from passport.backend.qa.test_user_service.tus_api.common.passport import bind_phone
from passport.backend.qa.test_user_service.tus_api.fillers import generate_fake_phone_in_e164
from passport.backend.qa.test_user_service.tus_api.idm_backend import check_access_to_consumer
from passport.backend.qa.test_user_service.tus_api.validators import (
    EnvValidator,
    TestPhone,
    WeakUidValidator,
)
from passport.backend.qa.test_user_service.tus_api.views.base import Schema
from passport.backend.qa.test_user_service.tus_api.views.tus.tus_base import TusBaseView


log = logging.getLogger(__name__)


class BindPhoneForm(Schema):
    uid = WeakUidValidator()
    phone_number = TestPhone(not_empty=True, if_missing=generate_fake_phone_in_e164(), strip=True)
    env = EnvValidator(not_empty=True, if_missing='TEST', allowed_environments=['TEST', 'PROD'], strip=True)


class BindPhone(TusBaseView):
    form = BindPhoneForm

    def process_request(self):
        self.check_access()

        env = self.form_values['env']
        uid = self.form_values['uid']
        phone_number = self.form_values['phone_number']

        account = get_saved_account(uid, env)

        request_form = {
            'uid': uid,
            'number': phone_number,
            'password': account.password,
            'secure': True,
            'env': env
        }

        bind_phone(**request_form)

        self.response_values = {
            'status': 'ok',
            'phone_number': phone_number,
            'passport_environment': get_passport_environment_for_response(env),
        }

    def check_access(self):
        account_consumer = get_tus_consumer_by_account_uid(self.form_values['uid'], self.form_values['env'])
        check_access_to_consumer(self.requester_info['login'], account_consumer)
        self.yasm_logger.log(
            client_login=self.requester_info['login'],
            tus_consumer=account_consumer,
        )


__all__ = (
    'BindPhone',
)
