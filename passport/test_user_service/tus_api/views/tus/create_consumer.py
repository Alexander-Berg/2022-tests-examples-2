# coding=utf-8
import logging

from passport.backend.qa.test_user_service.tus_api.common.idm import (
    add_new_consumer_to_idm,
    give_role_for_user,
)
from passport.backend.qa.test_user_service.tus_api.common.idm.idm_settings import admin_role_name
from passport.backend.qa.test_user_service.tus_api.exceptions import CreateTusConsumerError
from passport.backend.qa.test_user_service.tus_api.idm_backend import (
    bind_client_to_consumer,
    create_new_tus_consumer,
)
from passport.backend.qa.test_user_service.tus_api.validators import TusConsumer
from passport.backend.qa.test_user_service.tus_api.views.base import Schema
from passport.backend.qa.test_user_service.tus_api.views.tus.tus_base import TusBaseView


log = logging.getLogger(__name__)


class CreateTusConsumerForm(Schema):
    tus_consumer = TusConsumer(not_empty=True, strip=True)


class CreateTusConsumer(TusBaseView):
    form = CreateTusConsumerForm

    def process_request(self):
        login = self.requester_info['login']
        tus_consumer = self.form_values['tus_consumer']

        self.yasm_logger.log(
            client_login=self.requester_info['login'],
            tus_consumer=self.form_values['tus_consumer'],
        )

        create_new_tus_consumer(tus_consumer)
        _, message_type, message_value = bind_client_to_consumer(login, tus_consumer, admin_role_name)

        try:
            add_new_consumer_to_idm(tus_consumer, login)
            give_role_for_user(login, tus_consumer, admin_role_name)
        except Exception as e:
            log.error(e)
            raise CreateTusConsumerError(
                'The consumer was not created in idm. Please contact us: tus-dev@yandex-team.ru'
            )

        self.response_values = {
            message_type: message_value,
        }


__all__ = (
    'CreateTusConsumer',
)
