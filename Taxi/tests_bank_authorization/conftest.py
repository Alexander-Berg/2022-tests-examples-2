import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_authorization_plugins import *  # noqa: F403 F401
from testsuite.utils import http

from tests_bank_authorization import common

try:
    import library.python.resource  # noqa: F401
    _IS_ARCADIA = True
except ImportError:
    _IS_ARCADIA = False

if _IS_ARCADIA:
    import logging
    import dataclasses

    @pytest.fixture(autouse=True)
    async def service_logs(taxi_bank_authorization):
        levels = {
            'INFO': logging.INFO,
            'DEBUG': logging.DEBUG,
            'ERROR': logging.ERROR,
            'WARNING': logging.WARNING,
            'CRITICAL': logging.CRITICAL,
        }

        # Each log record is captured as a dictionary,
        # so we need to turn it back into a string
        def serialize_tskv(row):
            # these two will only lead to data duplication
            skip = {'timestamp', 'level'}

            # reorder keys so that 'text' is always in front
            keys = list(row.keys())
            keys.remove('text')
            keys.insert(0, 'text')

            return '\t'.join([f'{k}={row[k]}' for k in keys if k not in skip])

        async with taxi_bank_authorization.capture_logs() as capture:
            # This hack tricks the client into thinking that
            # caches still need to be invalidated on the first call
            # so as not to break tests that depend on this behaviour
            # pylint: disable=protected-access
            taxi_bank_authorization._client._state_manager._state = (
                dataclasses.replace(
                    # pylint: disable=protected-access
                    taxi_bank_authorization._client._state_manager._state,
                    caches_invalidated=False,
                )
            )

            @capture.subscribe()
            # pylint: disable=unused-variable
            def log(**row):
                logging.log(
                    levels.get(row['level'], logging.DEBUG),
                    serialize_tskv(row),
                )

            yield capture


@pytest.fixture
def risk_mock(mockserver):
    class Context:
        def __init__(self):
            self.risk_calculation_handler = None
            self.http_status_code = 200
            self.response = {
                'resolution': 'ALLOW',
                'action': [],
                'context_id': 'context_id',
            }

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler('/bank-risk/risk/calculation/otp_verify')
    def _risk_calculation_handler(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.risk_calculation_handler = _risk_calculation_handler
    return context


@pytest.fixture
def access_control_mock(mockserver):
    class Context:
        def __init__(self):
            self.apply_policies_handler = None
            self.http_status_code = 200
            self.handler_path = None

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/bank-access-control/access-control-internal/v1/apply-policies',
    )
    def _apply_policies_handler(request):
        assert request.method == 'POST'
        context.handler_path = request.json['resource_attributes'][
            'handler_path'
        ]
        decision = (
            'PERMIT'
            if request.json['subject_attributes']['jwt'] == 'allow'
            else 'DENY'
        )
        return mockserver.make_response(
            status=context.http_status_code, json={'decision': decision},
        )

    context.apply_policies_handler = _apply_policies_handler
    return context


@pytest.fixture
def core_faster_payments_mock(mockserver):
    class Context:
        def __init__(self):
            self.http_status_code = 200
            self.set_as_default_handler = None
            self.set_as_default_confirm_handler = None

        def set_status(self, status):
            self.http_status_code = status

    context = Context()

    @mockserver.json_handler(
        '/bank-core-faster-payments/v1/connect/setAsDefault',
    )
    def _mock_set_as_default(request: http.Request):
        assert request.method == 'POST'
        if request.headers['X-Yandex-BUID'] != common.FPS_BANK_UID:
            return mockserver.make_response(status=404)
        return {'request_id': common.FPS_REQUEST_ID}

    @mockserver.json_handler(
        '/bank-core-faster-payments/v1/connect/setAsDefault/confirm',
    )
    def _mock_set_as_default_confirm(request: http.Request):
        assert request.method == 'POST'
        if context.http_status_code != 200:
            return mockserver.make_response(status=context.http_status_code)
        if request.headers['X-Yandex-BUID'] != common.FPS_BANK_UID:
            return mockserver.make_response(status=404)
        if request.json['request_id'] != common.FPS_REQUEST_ID:
            return mockserver.make_response(status=404)
        if request.json['confirmation_code'] == '888888':
            return mockserver.make_response(
                status=200, json={'is_confirmed': True},
            )
        return mockserver.make_response(
            status=200, json={'is_confirmed': False},
        )

    context.set_as_default_handler = _mock_set_as_default
    context.set_as_default_confirm_handler = _mock_set_as_default_confirm
    return context


@pytest.fixture
def phone_number_mock(mockserver):
    class Context:
        def __init__(self):
            self.phones = {
                common.BANK_UID1: common.PHONE_NUMBER1,
                common.BANK_UID2: common.PHONE_NUMBER2,
            }

    context = Context()

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_number',
    )
    def _mock_phone_number(request: http.Request):
        if request.json['buid'] in context.phones:
            return {'phone': context.phones[request.json['buid']]}
        return mockserver.make_response(
            json={'code': 'NotFound', 'message': 'buid not found'},
            status_code=404,
        )

    return context
