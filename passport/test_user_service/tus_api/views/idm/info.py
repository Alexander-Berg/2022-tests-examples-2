# coding=utf-8
import logging

from passport.backend.qa.test_user_service.tus_api.idm_backend import build_tus_consumers_list
from passport.backend.qa.test_user_service.tus_api.views.idm.idm_base import IdmBaseView


log = logging.getLogger(__name__)


class IdmInfo(IdmBaseView):

    def _build_response(self):
        consumers_data = build_tus_consumers_list()
        return {
            'code': 0,
            'roles': {
                'slug': 'tus_consumer',
                'name': 'tus_consumer',
                'values': consumers_data
            }
        }

    def process_request(self):
        # Пример ответа на запрос см .response_examples/info.json
        self.response_values = self._build_response()


__all__ = (
    'IdmInfo',
)
