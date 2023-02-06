# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from passport.backend.oauth.core.test.utils import iter_eq
from passport.backend.oauth.tvm_api.tvm_api.tvm_abc.utils import client_to_response

from .base import (
    abc_get_service_members_response,
    BaseTvmAbcTestcaseWithUserTicket,
    TEST_OTHER_UID,
)


class ClientInfoTestcase(BaseTvmAbcTestcaseWithUserTicket):
    default_url = reverse_lazy('tvm_abc_client_info')
    http_method = 'GET'

    def default_params(self):
        return dict(
            super(ClientInfoTestcase, self).default_params(),
            client_id=self.test_client.id,
        )

    def expected_response(self, full=False):
        return {
            'status': 'ok',
            'content': [
                client_to_response(self.test_client, full_info=full),
            ],
            'is_viewed_by_owner': full,
        }

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response(full=True),
        )

    def test_client_not_found(self):
        rv = self.make_request(client_id=42)
        self.assert_status_error(rv, ['client.not_found'])

    def test_multiple_roles_ok(self):
        self.fake_abc.set_response_value(
            'get_service_members',
            abc_get_service_members_response(role_codes=['dishwasher', 'tvm_manager']),
        )
        rv = self.make_request()
        self.assert_status_ok(rv)

    def test_role_missing(self):
        self.fake_abc.set_response_value(
            'get_service_members',
            abc_get_service_members_response(role_codes=['copypaster']),
        )
        rv = self.make_request(uid=TEST_OTHER_UID)
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response(),
        )

    def test_no_user_ticket(self):
        rv = self.make_request(headers={'HTTP_HOST': 'oauth.yandex.ru'})
        self.assert_status_ok(rv)
        iter_eq(
            rv,
            self.expected_response(),
        )
