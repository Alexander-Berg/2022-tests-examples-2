# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.oauth.core.test.base_test_data import (
    TEST_ABC_SERVICE_ID,
    TEST_OTHER_ABC_SERVICE_ID,
    TEST_OTHER_UID,
    TEST_UID,
)
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient

from .base import (
    abc_get_service_members_response,
    BaseTvmAbcTestcaseWithUserTicket,
    CommonRoleTests,
    CommonUserTicketTests,
)


class ChangeClientAbcServiceTestcase(BaseTvmAbcTestcaseWithUserTicket, CommonUserTicketTests, CommonRoleTests):
    default_url = reverse_lazy('tvm_abc_change_client_abc_service')
    http_method = 'POST'

    def setUp(self):
        super(ChangeClientAbcServiceTestcase, self).setUp()
        self.fake_abc.set_response_side_effect(
            'get_service_members',
            [
                abc_get_service_members_response(uid=TEST_UID, service_id=TEST_OTHER_ABC_SERVICE_ID),
                abc_get_service_members_response(uid=TEST_OTHER_UID, service_id=TEST_ABC_SERVICE_ID),
            ],
        )

    def default_params(self):
        return dict(
            super(ChangeClientAbcServiceTestcase, self).default_params(),
            client_id=self.test_client.id,
            initiator_uid=TEST_OTHER_UID,
            abc_service_id=TEST_OTHER_ABC_SERVICE_ID,
        )

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)

        client = TVMClient.by_id(self.test_client.id)
        eq_(client.abc_service_id, TEST_OTHER_ABC_SERVICE_ID)

    def test_client_not_found(self):
        rv = self.make_request(client_id=42)
        self.assert_status_error(rv, ['client.not_found'])

    def test_initiator_has_no_role(self):
        self.fake_abc.set_response_side_effect(
            'get_service_members',
            [
                abc_get_service_members_response(
                    uid=TEST_UID,
                    service_id=TEST_OTHER_ABC_SERVICE_ID,
                ),
                abc_get_service_members_response(
                    uid=TEST_OTHER_UID,
                    service_id=TEST_ABC_SERVICE_ID,
                    role_codes=['dishwasher'],
                ),
            ],
        )
        rv = self.make_request()
        self.assert_status_error(rv, ['abc_team.member_required'])

    def test_multiple_roles_ok(self):
        # Оверрайдим тест из микcина: надо настроить ответ для двух аккаунтов
        self.fake_abc.set_response_side_effect(
            'get_service_members',
            [
                abc_get_service_members_response(
                    uid=TEST_UID,
                    service_id=TEST_OTHER_ABC_SERVICE_ID,
                    role_codes=['dishwasher', 'tvm_manager'],
                ),
                abc_get_service_members_response(
                    uid=TEST_OTHER_UID,
                    service_id=TEST_ABC_SERVICE_ID,
                    role_codes=['dishwasher', 'tvm_manager'],
                ),
            ],
        )
        rv = self.make_request()
        self.assert_status_ok(rv)
