# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from nose.tools import eq_
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient

from .base import (
    BaseTvmAbcTestcaseWithUserTicket,
    CommonRoleTests,
    CommonUserTicketTests,
)


class EditClientTestcase(BaseTvmAbcTestcaseWithUserTicket, CommonUserTicketTests, CommonRoleTests):
    default_url = reverse_lazy('tvm_abc_edit_client')
    http_method = 'POST'

    def default_params(self):
        return dict(
            super(EditClientTestcase, self).default_params(),
            client_id=self.test_client.id,
            name='Test Test',
        )

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)

        client = TVMClient.by_id(self.test_client.id)
        eq_(client.name, 'Test Test')
        eq_(client.modified, DatetimeNow())

    def test_client_not_found(self):
        rv = self.make_request(client_id=42)
        self.assert_status_error(rv, ['client.not_found'])
