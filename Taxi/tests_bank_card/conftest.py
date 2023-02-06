import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from bank_audit_logger.mock_bank_audit import bank_audit  # noqa: F401
from bank_card_plugins import *  # noqa: F403 F401

from tests_bank_card import common


@pytest.fixture
def core_card_mock(mockserver):
    class Context:
        def __init__(self):
            self.http_status_code = 200
            self.get_by_id_handler = None
            self.list_handler = None
            self.list_by_agreement_handler = None
            self.prepare_apple_data_handler = None
            self.prepare_google_data_handler = None
            self.status_set_handler = None
            self.bind_to_trust_handler = None
            self.cards_list = [
                {
                    'public_card_id': '1',
                    'cardholder_name': 'Anton',
                    'bin': '123123',
                    'last_pan_digits': '54321',
                    'exp_month': 5,
                    'exp_year': 2022,
                    'payment_system': 'VISA',
                    'status': 'ACTIVE',
                    'tokens': [
                        {
                            'reference_id': 'some_token_1',
                            'type': 'GOOGLE_PAY',
                            'suffix': '123',
                        },
                        {
                            'reference_id': 'some_token_2',
                            'type': 'UNDEFINED',
                            'suffix': '123',
                        },
                    ],
                },
                {
                    'public_card_id': '2',
                    'cardholder_name': '',
                    'bin': '321321',
                    'last_pan_digits': '0987',
                    'exp_month': 12,
                    'exp_year': 2093,
                    'payment_system': 'MIR',
                    'status': 'FROZEN',
                    'tokens': [
                        {
                            'reference_id': 'some_token_1',
                            'type': 'APPLE_PAY',
                            'suffix': '123',
                        },
                        {
                            'reference_id': 'some_token_2',
                            'type': 'UNDEFINED',
                            'suffix': '123',
                        },
                    ],
                },
            ]
            self.cards_list_response = {'cards': self.cards_list}
            self.card_info = self.cards_list[0]
            self.prepared_apple_data = {
                'cryptographic_otp': 'otp',
                'ciphertext': 'text',
                'ephemeral_public_key': 'key',
            }
            self.prepared_google_data = {
                'address': {'country_code': '213'},
                'card_network': 'CARD_NETWORK_VISA',
                'token_provider': 'TOKEN_PROVIDER_VISA',
                'last_digits': '1234',
                'opaque_payment_card': 'xxx',
            }
            self.status_set_response = {}
            self.error = {'code': 'error_code', 'message': 'error_message'}

        def set_card_info_field(self, field, value):
            self.card_info[field] = value

        def set_card_info(self, value):
            self.card_info = value

        def set_cards_list(self, value):
            self.cards_list = value
            self.cards_list_response = {'cards': value}

        def set_cards_list_response(self, value):
            self.cards_list_response = value

        def set_prepared_apple_data(self, prepared_apple_data):
            self.prepared_apple_data = prepared_apple_data

        def set_prepared_google_data(self, prepared_google_data):
            self.prepared_google_data = prepared_google_data

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_status_set_response(self, data):
            self.status_set_response = data

    context = Context()

    @mockserver.json_handler('/bank-core-card/v1/card/info/get-by-id')
    def _get_by_id_handler(request):
        assert request.headers['X-Yandex-BUID'] == common.DEFAULT_YANDEX_BUID
        assert (
            request.headers['X-YaBank-SessionUUID']
            == common.DEFAULT_YABANK_SESSION_UUID
        )
        assert 'public_card_id' in request.json
        return mockserver.make_response(
            status=context.http_status_code, json=context.card_info,
        )

    @mockserver.json_handler('/bank-core-card/v1/card/info/list')
    def _list_handler(request):
        assert request.headers['X-Yandex-BUID'] == common.DEFAULT_YANDEX_BUID
        assert (
            request.headers['X-YaBank-SessionUUID']
            == common.DEFAULT_YABANK_SESSION_UUID
        )
        return mockserver.make_response(
            status=context.http_status_code, json=context.cards_list_response,
        )

    @mockserver.json_handler('/bank-core-card/v1/card/info/list-by-agreement')
    def _list_by_agreement_handler(request):
        assert request.headers['X-Yandex-BUID'] == common.DEFAULT_YANDEX_BUID
        assert (
            request.headers['X-YaBank-SessionUUID']
            == common.DEFAULT_YABANK_SESSION_UUID
        )
        assert 'public_agreement_id' in request.json
        return mockserver.make_response(
            status=context.http_status_code, json=context.cards_list_response,
        )

    @mockserver.json_handler('/bank-core-card/v1/card/prepare-apple-data')
    def _prepare_apple_data_handler(request):
        return mockserver.make_response(
            status=context.http_status_code, json=context.prepared_apple_data,
        )

    @mockserver.json_handler('/bank-core-card/v1/card/prepare-google-data')
    def _prepare_google_data_handler(request):
        return mockserver.make_response(
            status=context.http_status_code, json=context.prepared_google_data,
        )

    @mockserver.json_handler('/bank-core-card/v1/card/status/set')
    def _status_set_handler(request):
        return mockserver.make_response(
            status=context.http_status_code, json=context.status_set_response,
        )

    @mockserver.json_handler('/bank-core-card/v1/card/bind-to-trust')
    def _bind_to_trust_handler(request):
        assert request.headers['X-Yandex-BUID'] == common.DEFAULT_YANDEX_BUID
        assert (
            request.headers['X-YaBank-SessionUUID']
            == common.DEFAULT_YABANK_SESSION_UUID
        )
        assert (
            request.headers['X-Idempotency-Token']
            == common.DEFAULT_IDEMPOTENCY_TOKEN
        )
        json_data = request.json
        assert json_data['public_card_id'] == common.CARD_ID
        if context.http_status_code == 200:
            body = {'status': 'PENDING', 'request_id': 'some_procaas_id'}
        else:
            body = context.error
        return mockserver.make_response(
            status=context.http_status_code, json=body,
        )

    context.get_by_id_handler = _get_by_id_handler
    context.prepare_apple_data_handler = _prepare_apple_data_handler
    context.prepare_google_data_handler = _prepare_google_data_handler
    context.list_handler = _list_handler
    context.list_by_agreement_handler = _list_by_agreement_handler
    context.bind_to_trust_handler = _bind_to_trust_handler
    context.status_set_handler = _status_set_handler

    return context


@pytest.fixture(autouse=True)
def bank_risk(mockserver):
    class Context:
        def __init__(self):
            self.risk_calculation_handler = None
            self.http_status_code = 200
            self.response = {
                'resolution': 'ALLOW',
                'action': [],
                'af_decision_id': 'af_decision_id',
            }

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_response(self, resolution, actions):
            self.response = {
                'resolution': resolution,
                'action': actions,
                'af_decision_id': 'af_decision_id',
            }

    context = Context()

    @mockserver.json_handler(
        '/bank-risk/risk/calculation/card_status_change_request',
    )
    def _risk_calculation_handler(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=context.http_status_code, json=context.response,
        )

    context.risk_calculation_handler = _risk_calculation_handler

    return context
