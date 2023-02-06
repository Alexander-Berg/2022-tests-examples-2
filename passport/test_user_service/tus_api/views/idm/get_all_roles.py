# coding=utf-8
import logging

from passport.backend.qa.test_user_service.tus_api.idm_backend import build_tus_users_list
from passport.backend.qa.test_user_service.tus_api.views.idm.idm_base import IdmBaseView


log = logging.getLogger(__name__)


class IdmGetAllRoles(IdmBaseView):

    def _build_response(self):
        tus_users = build_tus_users_list()
        return {
            'code': 0,
            'users': tus_users
        }

    def process_request(self):
        self.response_values = self._build_response()


__all__ = (
    'IdmGetAllRoles',
)
