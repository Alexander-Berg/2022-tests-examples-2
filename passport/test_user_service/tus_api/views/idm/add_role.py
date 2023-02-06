# coding=utf-8
import logging

from formencode import validators
from passport.backend.qa.test_user_service.tus_api.idm_backend import bind_client_to_consumer
from passport.backend.qa.test_user_service.tus_api.validators import IdmRoleValidator
from passport.backend.qa.test_user_service.tus_api.views.base import Schema
from passport.backend.qa.test_user_service.tus_api.views.idm.idm_base import IdmBaseView


log = logging.getLogger(__name__)


class IdmAddRoleForm(Schema):
    login = validators.String(not_empty=True, strip=True)
    role = IdmRoleValidator(not_empty=True, strip=True)


class IdmAddRole(IdmBaseView):
    form = IdmAddRoleForm

    def process_request(self):
        args = {
            'login': self.form_values['login'],
            'consumer_name': self.form_values['role']['tus_consumer'],
            'role': self.form_values['role']['role'],
        }
        response_code, message_type, message_value = bind_client_to_consumer(**args)
        self.response_values = {
            'code': response_code,
            message_type: message_value,
        }


__all__ = (
    'IdmAddRole',
)
