# -*- coding: utf-8 -*-
import logging

from formencode import validators
from passport.backend.qa.test_user_service.tus_api.backend import (
    get_passport_environment_for_response,
    save_account_to_db,
)
from passport.backend.qa.test_user_service.tus_api.common.blackbox.blackbox import (
    check_uid_matches_login,
    get_login_by_uid,
    get_uid_by_login,
    validate_password_for_login,
)
from passport.backend.qa.test_user_service.tus_api.common.kolmogor.kolmogor_utils import get_kolmogor
from passport.backend.qa.test_user_service.tus_api.exceptions import InvalidRequestError
from passport.backend.qa.test_user_service.tus_api.fillers import _generate_uid_for_external_account
from passport.backend.qa.test_user_service.tus_api.idm_backend import check_access_to_consumer
from passport.backend.qa.test_user_service.tus_api.settings import DEFAULT_TUS_CONSUMER
from passport.backend.qa.test_user_service.tus_api.validators import (
    EnvValidator,
    TagsValidator,
    TusConsumer,
    WeakLoginValidator,
    WeakUidValidator,
)
from passport.backend.qa.test_user_service.tus_api.views.base import Schema
from passport.backend.qa.test_user_service.tus_api.views.tus.tus_base import TusBaseView


log = logging.getLogger(__name__)


class SaveAccountForm(Schema):
    uid = WeakUidValidator(if_missing='')
    login = WeakLoginValidator(not_empty=True, if_missing='', strip=True)
    password = validators.String(not_empty=True, strip=True)
    tags = TagsValidator()
    tus_consumer = TusConsumer(not_empty=True, if_missing=DEFAULT_TUS_CONSUMER, strip=True)
    env = EnvValidator(not_empty=True, if_missing='TEST', strip=True)


class SaveAccount(TusBaseView):
    form = SaveAccountForm

    @staticmethod
    def validate_uid_login(uid, login, client_ip, env):
        is_external_env = env == 'EXTERNAL'
        if uid and len(login) > 0:
            check_uid_matches_login(uid, login, client_ip, env)
        elif uid:
            login = get_login_by_uid(uid, client_ip, env)
        elif len(login) > 0:
            if is_external_env:
                uid = _generate_uid_for_external_account()
            else:
                uid = get_uid_by_login(login, client_ip, env)
        else:
            if is_external_env:
                raise InvalidRequestError('Request in EXTERNAL environment must have login')
            else:
                raise InvalidRequestError('Request must have one of two fields: login or uid')
        return uid, login

    def process_request(self):
        self.check_access()
        env = self.form_values['env']
        tags = self.form_values.get('tags', [])
        is_external_env = env == 'EXTERNAL'

        uid = self.form_values['uid'] if not is_external_env else ''
        login = self.form_values['login']
        password = self.form_values['password']

        uid, login = self.validate_uid_login(uid, login, self.client_ip, env)
        get_kolmogor().increment_requests_counter('save_account', [str(uid)])

        if env != 'EXTERNAL':
            validate_password_for_login(login, password, self.client_ip, env)

        account_data = {
            'uid': uid,
            'login': login,
            'password': password,
        }

        is_saved = save_account_to_db(
            uid=uid,
            login=login,
            password=password,
            tags=tags,
            delete_at=None,
            tus_consumer=self.form_values['tus_consumer'],
            env=env
        )

        self.response_values = {
            'status': 'ok',
            'account': account_data,
            'saved': is_saved,
            'passport_environment': get_passport_environment_for_response(env),
        }

    def check_access(self):
        check_access_to_consumer(self.requester_info['login'], self.form_values['tus_consumer'])
        self.yasm_logger.log(
            client_login=self.requester_info['login'],
            tus_consumer=self.form_values['tus_consumer'],
        )


__all__ = (
    'SaveAccount',
)
