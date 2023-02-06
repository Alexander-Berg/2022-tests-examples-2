# coding=utf-8
import logging

from passport.backend.core.utils.decorators import cached_property
from passport.backend.qa.test_user_service.tus_api.tvm import validate_service_ticket
from passport.backend.qa.test_user_service.tus_api.views.base import BaseView
from passport.backend.qa.test_user_service.tus_api.views.headers import (
    HEADER_IDM_X_REQ_ID,
    HEADER_SERVICE_TICKET,
)


log = logging.getLogger(__name__)


class IdmBaseView(BaseView):

    @property
    def idm_request_id(self):
        req_id = self.headers.get(HEADER_IDM_X_REQ_ID.name)
        return req_id

    @cached_property
    def service_ticket(self):
        return self.headers.get(HEADER_SERVICE_TICKET.name)

    expected_headers = [HEADER_SERVICE_TICKET]

    def check_headers(self):
        super(IdmBaseView, self).check_headers()
        log.debug('IDM-req-id: {req_id}'.format(req_id=self.idm_request_id))
        validate_service_ticket(self.service_ticket)
