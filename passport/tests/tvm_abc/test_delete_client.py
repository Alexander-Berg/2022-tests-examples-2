# -*- coding: utf-8 -*-
from django.urls import reverse_lazy
from nose.tools import (
    assert_raises,
    ok_,
)
from passport.backend.oauth.core.db.eav import EntityNotFoundError
from passport.backend.oauth.tvm_api.tvm_api.db.tvm_client import TVMClient

from .base import (
    BaseTvmAbcTestcaseWithUserTicket,
    CommonRoleTests,
    CommonUserTicketTests,
)


class DeleteClientTestcase(BaseTvmAbcTestcaseWithUserTicket, CommonUserTicketTests, CommonRoleTests):
    default_url = reverse_lazy('tvm_abc_delete_client')
    http_method = 'POST'

    def default_params(self):
        return dict(
            super(DeleteClientTestcase, self).default_params(),
            client_id=self.test_client.id,
        )

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)

        with assert_raises(EntityNotFoundError):
            TVMClient.by_id(self.test_client.id)

        # Но в БД приложение должно остаться
        ok_(TVMClient.by_id(self.test_client.id, allow_deleted=True))

    def test_client_not_found(self):
        rv = self.make_request(client_id=42)
        self.assert_status_error(rv, ['client.not_found'])
