# -*- coding: utf-8 -*-
import logging

from formencode import validators
from passport.backend.qa.test_user_service.tus_api.backend import (
    get_passport_environment_for_response,
    save_account_to_db,
)
from passport.backend.qa.test_user_service.tus_api.common.kolmogor.kolmogor_utils import get_kolmogor
from passport.backend.qa.test_user_service.tus_api.common.passport.passport_api import call_account_registration
from passport.backend.qa.test_user_service.tus_api.exceptions import PassportRegistrationError
from passport.backend.qa.test_user_service.tus_api.fillers import fill_missing_account_data
from passport.backend.qa.test_user_service.tus_api.idm_backend import check_access_to_consumer
from passport.backend.qa.test_user_service.tus_api.settings import DEFAULT_TUS_CONSUMER
from passport.backend.qa.test_user_service.tus_api.validators import (
    DeleteAfter,
    EnvValidator,
    TagsValidator,
    TestLogin,
    TusConsumer,
)
from passport.backend.qa.test_user_service.tus_api.views.base import Schema
from passport.backend.qa.test_user_service.tus_api.views.tus.tus_base import TusBaseView


log = logging.getLogger(__name__)


class CreateAccountPortalForm(Schema):
    login = TestLogin(not_empty=True, if_missing='', strip=True)
    password = validators.String(not_empty=True, if_missing='', strip=True)
    firstname = validators.String(not_empty=True, if_missing='', strip=True)
    lastname = validators.String(not_empty=True, if_missing='', strip=True)
    language = validators.String(not_empty=True, if_missing='', strip=True)
    country = validators.String(not_empty=True, if_missing='', strip=True)
    tags = TagsValidator()
    tus_consumer = TusConsumer(not_empty=True, if_missing=DEFAULT_TUS_CONSUMER, strip=True)
    env = EnvValidator(not_empty=True, if_missing='TEST', allowed_environments=['TEST', 'PROD'], strip=True)
    delete_after = DeleteAfter(not_empty=True, if_missing=None, strip=True)
    # TODO: параметр для привязки телефона


class CreateAccountPortal(TusBaseView):
    form = CreateAccountPortalForm

    def process_request(self):
        self.check_access()

        env = self.form_values['env']
        tus_consumer = self.form_values['tus_consumer']
        tags = self.form_values.get('tags', [])

        if 'delete_after' in self.form_values:
            delete_at = self.form_values['delete_after'].replace(microsecond=0).timestamp()
        else:
            delete_at = None

        get_kolmogor().increment_requests_counter('create_account', ['#total', tus_consumer])

        account_data = {
            'login': self.form_values['login'],
            'password': self.form_values['password'],
            'firstname': self.form_values['firstname'],
            'lastname': self.form_values['lastname'],
            'language': self.form_values['language'],
            'country': self.form_values['country'],
        }
        # is_login_defined_by_user = self.form_values['login'] is not ''
        fill_missing_account_data(account_data)
        account_data['delete_at'] = delete_at

        registration_errors = call_account_registration(account_data, env)
        if registration_errors:
            # if not is_login_defined_by_user and 'login.notavailable' in registration_errors:
            # TODO: retry with other login
            raise PassportRegistrationError(error_description=registration_errors)

        is_saved = save_account_to_db(
            account_data['uid'], account_data['login'], account_data['password'], delete_at,
            tags, tus_consumer, env
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
    'CreateAccountPortal',
)
