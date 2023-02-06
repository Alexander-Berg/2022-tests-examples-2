# coding=utf-8
import logging

from formencode.validators import Int
from passport.backend.qa.test_user_service.tus_api.backend import (
    get_passport_environment_for_response,
    get_uids_with_tags,
)
from passport.backend.qa.test_user_service.tus_api.exceptions import TusConsumerAccessDenied
from passport.backend.qa.test_user_service.tus_api.idm_backend import check_access_to_consumer
from passport.backend.qa.test_user_service.tus_api.settings import DEFAULT_TUS_CONSUMER
from passport.backend.qa.test_user_service.tus_api.validators import (
    EnvValidator,
    TusConsumer,
)
from passport.backend.qa.test_user_service.tus_api.views.base import Schema
from passport.backend.qa.test_user_service.tus_api.views.tus.tus_base import TusBaseView


log = logging.getLogger(__name__)


class ListAccountsForm(Schema):
    tus_consumer = TusConsumer(not_empty=True, strip=True)
    env = EnvValidator(not_empty=True, if_missing='TEST', strip=True)
    offset = Int(min=0, not_empty=True, if_missing=0)


class ListAccounts(TusBaseView):
    form = ListAccountsForm

    def process_request(self):
        self.check_access()
        tus_consumer = self.form_values['tus_consumer']
        if tus_consumer == DEFAULT_TUS_CONSUMER:
            raise TusConsumerAccessDenied(
                'It is forbidden to call /1/list_accounts/ with common consumer\'{consumer}\'.'
                'To create new consumer use /1/create_tus_consumer/'.format(consumer=DEFAULT_TUS_CONSUMER)
            )
        env = self.form_values['env']

        uids = get_uids_with_tags(
            consumer_name=tus_consumer,
            client_login=self.requester_info['login'],
            offset=self.form_values['offset'],
            env=env,
        )

        self.response_values = {
            'status': 'ok',
            'uids': uids,
            'passport_environment': get_passport_environment_for_response(env),
        }

    def check_access(self):
        check_access_to_consumer(self.requester_info['login'], self.form_values['tus_consumer'])
        self.yasm_logger.log(
            client_login=self.requester_info['login'],
            tus_consumer=self.form_values['tus_consumer'],
        )


__all__ = (
    'ListAccounts',
)
