import typing
from unittest.mock import patch, Mock

from django.conf import settings
from django.test import SimpleTestCase
from django.test import override_settings
from django_yauth.authentication_mechanisms.tvm.request import TvmServiceRequest

from l3agent.auth import TVMServicePermission
from l3agent.exceptions import Forbidden

UNKNOWN_TVM_SERVICE_ID = -1


class MockUser(TvmServiceRequest):
    # noinspection PyMissingConstructor
    def __init__(self, tvm_client_id):
        self.src = tvm_client_id

    @property
    def service_ticket(self):
        return self


class MockRequest:
    def __init__(self, user):
        self._user = user
        self._internal_request = Mock()

    @property
    def yauser(self):
        return self._user

    @property
    def _request(self):
        return self._internal_request


@override_settings(BALANCER_AGENTS_TVM_ID=123)
class TVMServiceTicketAuthenticationTest(SimpleTestCase):
    def test_agent_tvm_auth_success(self):
        request = typing.cast("rest_framework.request.Request", MockRequest(MockUser(settings.BALANCER_AGENTS_TVM_ID)))
        result = TVMServicePermission().has_permission(request, Mock())
        self.assertTrue(result)

    def test_agent_tvm_auth_failed(self):
        request = typing.cast("rest_framework.request.Request", MockRequest(MockUser(UNKNOWN_TVM_SERVICE_ID)))
        result = TVMServicePermission().has_permission(request, Mock())
        self.assertFalse(result)

    @patch("l3agent.auth.TVMServicePermission.auth_is_disabled", Mock(return_value=True))
    def test_agent_tvm_auth_disable(self):
        result = TVMServicePermission().has_permission(Mock(), Mock())
        self.assertEqual(result, True)

    def test_agent_tvm_auth_exception(self):
        with self.assertRaises(Forbidden):
            request = typing.cast("rest_framework.request.Request", MockRequest(None))
            TVMServicePermission().has_permission(request, Mock())
