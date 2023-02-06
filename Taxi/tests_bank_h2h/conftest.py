import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_h2h_plugins import *  # noqa: F403 F401

from tests_bank_h2h import common

try:
    import library.python.resource  # noqa: F401

    _IS_ARCADIA = True
except ImportError:
    _IS_ARCADIA = False

if _IS_ARCADIA:
    import logging
    import dataclasses

    @pytest.fixture(autouse=True)
    async def service_logs(taxi_bank_h2h):
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

        async with taxi_bank_h2h.capture_logs() as capture:
            # This hack tricks the client into thinking that
            # caches still need to be invalidated on the first call
            # so as not to break tests that depend on this behaviour
            # pylint: disable=protected-access
            taxi_bank_h2h._client._state_manager._state = dataclasses.replace(
                # pylint: disable=protected-access
                taxi_bank_h2h._client._state_manager._state,
                caches_invalidated=False,
            )

            @capture.subscribe()
            # pylint: disable=unused-variable
            def log(**row):
                logging.log(
                    levels.get(row['level'], logging.DEBUG),
                    serialize_tskv(row),
                )

            yield capture


@pytest.fixture()
def bank_core_tps(mockserver):
    class Context:
        def __init__(self):
            self.document_execute_handler = None
            self.document_execute_request = None
            self.document_status_get_handler = None

    context = Context()

    def success_response():
        return {
            'sender': common.SENDER,
            'sender_reference': common.DOCUMENT_ID,
            'document_id': 'some_javist_id',
            'instructions': [
                {
                    'instruction_id': '1',
                    'status': common.STATUS_NEW,
                    'requested_debit_money': {
                        'amount': '1234.56',
                        'currency': 'RUB',
                    },
                },
                {
                    'instruction_id': '2',
                    'status': common.STATUS_FAILED,
                    'requested_debit_money': {
                        'amount': '234.56',
                        'currency': 'USD',
                    },
                },
            ],
        }

    @mockserver.json_handler('/bank-core-tps/v2/document/internal')
    def _document_execute(request):
        assert request.method == 'POST'
        context.document_execute_request = request.json
        return success_response()

    @mockserver.json_handler(
        '/bank-core-tps/v2/document/status/by-reference/get',
    )
    def _document_status_get(request):
        assert request.method == 'POST'
        response = success_response()
        response['instructions'][0]['status'] = common.STATUS_FINISHED
        response['instructions'][0]['actual_debit_money'] = {
            'amount': '1234.56',
            'currency': 'RUB',
        }
        return response

    context.document_execute_handler = _document_execute
    context.document_status_get_handler = _document_status_get

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
def s3_mock(mockserver):
    class Context:
        def __init__(self):
            self.s3_handle = None

    context = Context()

    @mockserver.handler(r'/s3-host', prefix=True)
    def _mock_s3(request):
        assert request.path == '/s3-host/file_name'
        return mockserver.make_response('file_content', status=200)

    context.s3_handle = _mock_s3

    return context
