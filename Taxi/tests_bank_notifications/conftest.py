# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from bank_notifications_plugins import *  # noqa: F403 F401

import tests_bank_notifications.defaults as defaults


try:
    import library.python.resource  # noqa: F401
    _IS_ARCADIA = True
except ImportError:
    _IS_ARCADIA = False


if _IS_ARCADIA:
    import logging
    import dataclasses

    @pytest.fixture(autouse=True)
    async def service_logs(taxi_bank_notifications):
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

        async with taxi_bank_notifications.capture_logs() as capture:
            # This hack tricks the client into thinking that
            # caches still need to be invalidated on the first call
            # so as not to break tests that depend on this behaviour
            # pylint: disable=protected-access
            taxi_bank_notifications._client._state_manager._state = (
                dataclasses.replace(
                    # pylint: disable=protected-access
                    taxi_bank_notifications._client._state_manager._state,
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


@pytest.fixture(autouse=True)
def bank_core_statement_mock(mockserver):
    def make_transactions():
        transactions = [
            {
                'transaction_id': '1',  # incoming transfer
                'status': 'CLEAR',
                'type': 'FPS',
                'direction': 'CREDIT',
                'timestamp': '2018-01-28T12:08:46.372+00:00',
                'merchant': {
                    'merchant_id': '96895a6a-f82c-4ac1-ba91-759f1464ee8b',
                    'merchant_name': 'YANDEX_TECH',
                    'merchant_country': 'Russia',
                    'merchant_city': 'Moscow',
                    'merchant_category_code': '4321',
                },
                'money': {'amount': '10000', 'currency': 'RUB'},
                'plus_debit': {'amount': '0', 'currency': 'RUB'},
                'plus_credit': {'amount': '0', 'currency': 'RUB'},
                'fees': [],
            },
        ]
        return transactions

    def make_response_transaction_list(cursor, page_size, transactions_count):
        transactions = make_transactions()
        if transactions_count is not None:
            transactions = transactions[:transactions_count]
        response = {
            'status_groups': [x for x in transactions][: int(page_size)],
        }
        return response

    class Context:
        def __init__(self):
            self.transaction_list_handler = None
            self.need_timeout_exception = False
            self.needed_error_code = None
            self.balance_currency = 'RUB'
            self.transactions_count = None

        def set_transaction_count(self, count):
            self.transactions_count = count

        def set_need_timeout(self, need):
            self.need_timeout_exception = need

    context = Context()

    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/get',
        prefix=True,
    )
    def _mock_get_transaction_list(request):
        if context.need_timeout_exception:
            raise mockserver.TimeoutError()
        if context.needed_error_code:
            return mockserver.make_response(
                status=context.needed_error_code,
                json={'code': '', 'message': ''},
            )
        return make_response_transaction_list(
            request.query.get('cursor'),
            request.query.get('page_size'),
            context.transactions_count,
        )

    context.transaction_list_handler = _mock_get_transaction_list

    return context


@pytest.fixture(autouse=True)
def bank_userinfo_mock(mockserver):
    class Context:
        def __init__(self):
            self.get_buid_info_handler = None
            self.http_status_code = 200

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_buid_info',
    )
    def _get_buid_info_handler(request):
        assert 'buid' in request.json
        buid = request.json.get('buid')
        buid_map = {defaults.BUID: defaults.UID, defaults.BUID2: defaults.UID2}
        assert buid in buid_map
        yandex_uid = buid_map[buid]

        if context.http_status_code == 200:
            return mockserver.make_response(
                status=context.http_status_code,
                json={'buid_info': {'yandex_uid': yandex_uid, 'buid': buid}},
            )
        return mockserver.make_response(
            status=context.http_status_code,
            json={'code': 'error_code', 'message': 'error_message'},
        )

    context.get_buid_info_handler = _get_buid_info_handler
    return context


@pytest.fixture(autouse=True)
def bank_core_client_mock(mockserver):
    class Context:
        def __init__(self):
            self.response = {'auth_level': 'KYC', 'phone_number': '1'}
            self.http_status_code = 200
            self.client_auth_level_handler = None
            self.bad_response_code = None

        def set_response(self, response):
            self.response = response

        def set_auth_level(self, auth_level):
            self.response['auth_level'] = auth_level

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/bank-core-client/v1/client/info/get', prefix=True,
    )
    def _mock_get_client_auth_level(request):
        if context.bad_response_code:
            return mockserver.make_response(
                status=context.bad_response_code,
                json={'code': str(context.bad_response_code), 'message': '-'},
            )
        buid = request.headers['X-Yandex-BUID']
        if buid == 'bad_buid':
            context.http_status_code = 404
            context.response = {
                'code': 'error_code',
                'message': 'error_message',
            }
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.client_auth_level_handler = _mock_get_client_auth_level

    return context


@pytest.fixture(autouse=True)
def bank_applications_mock(mockserver):
    class Context:
        def __init__(self):
            self.response = {'applications': []}
            self.http_status_code = 200
            self.client_processing_apps_handler = None

        def set_response(self, response):
            self.response = response

        def set_http_status_code(self, code):
            self.http_status_code = code

    context = Context()

    @mockserver.json_handler(
        '/bank-applications'
        '/applications-internal/v1/get_processing_applications',
    )
    def _mock_processing_applications(request):
        assert request.method == 'POST'
        if context.http_status_code == 200:
            assert request.json.get('uid') or request.json.get('buid')
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.client_processing_apps_handler = _mock_processing_applications

    return context
