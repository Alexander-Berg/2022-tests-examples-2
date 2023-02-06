# coding=utf-8
import logging

from formencode import validators
from passport.backend.qa.test_user_service.tus_api.idm_backend import unbind_consumer_from_client
from passport.backend.qa.test_user_service.tus_api.validators import IdmRoleValidator
from passport.backend.qa.test_user_service.tus_api.views.base import Schema
from passport.backend.qa.test_user_service.tus_api.views.idm.idm_base import IdmBaseView


log = logging.getLogger(__name__)


class IdmRemoveRoleForm(Schema):
    login = validators.String(not_empty=True, strip=True)
    role = IdmRoleValidator(not_empty=True, strip=True)
    fired = validators.String(not_empty=True, if_missing='0', strip=True)


class IdmRemoveRole(IdmBaseView):
    form = IdmRemoveRoleForm

    @property
    def fired(self):
        return self.form_values['fired']

    def process_request(self):
        login = self.form_values['login']
        consumer = self.form_values['role']['tus_consumer']
        role = self.form_values['role']['role']
        response_code, message_type, message_value = unbind_consumer_from_client(consumer, role, login, int(self.fired))
        self.response_values = {
            'code': response_code,
            message_type: message_value,
        }


__all__ = (
    'IdmRemoveRole',
)
