# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=wrong-import-order
from cashbox_integration_plugins import *  # noqa: F403 F401
import pytest


class CloudKassirContext:
    def __init__(self):
        self.post_receipt_handler = None
        self.receipt_status_handler = None
        self.get_receipt_handler = None

        self.credentials_to_data_post = {}
        self.credentials_to_data_get = {}

    def set_data_for_post_receipt(self, credentials, inn, uuid):
        self.credentials_to_data_post[credentials] = (inn, uuid)

    def set_data_for_get_receipt(self, credentials, uuid, is_ready):
        self.credentials_to_data_get[credentials] = (uuid, is_ready)


@pytest.fixture(name='cloud_kassir_service')
def _cloud_kassir_service(mockserver):
    context = CloudKassirContext()

    @mockserver.json_handler('cashbox-cloud-kassir/kkt/receipt')
    def _mock_post_receipt_handler(request):
        inn = request.json['Inn']
        credentials = request.headers['Authorization']

        if credentials not in context.credentials_to_data_post:
            return mockserver.make_response(
                'Unauthorized: Access is denied due to invalid credentials',
                content_type='text/html',
                status=401,
            )

        expected_inn, uuid = context.credentials_to_data_post[credentials]

        if inn != expected_inn:
            return mockserver.make_response(
                json={
                    'Success': False,
                    'Message': f'Компания с ИНН {inn} не найдена',
                    'Model': {'ErrorCode': -1},
                },
                status=200,
            )

        return {
            'Success': True,
            'Message': 'Queued',
            'Model': {'Id': uuid, 'ErrorCode': 0},
        }

    @mockserver.json_handler('cashbox-cloud-kassir/kkt/receipt/status/get')
    def _mock_get_receipt_status_handler(request):
        uuid = request.json['Id']
        credentials = request.headers['Authorization']

        if credentials not in context.credentials_to_data_get:
            return mockserver.make_response(
                'Unauthorized: Access is denied due to invalid credentials',
                content_type='text/html',
                status=401,
            )

        expected_uuid, is_ready = context.credentials_to_data_get[credentials]

        if uuid != expected_uuid:
            return {'Success': True, 'Model': 'NotFound'}

        if not is_ready:
            return {'Success': True, 'Model': 'Queued'}

        return {'Success': True, 'Model': 'Processed'}

    @mockserver.json_handler('cashbox-cloud-kassir/kkt/receipt/get')
    def _mock_get_receipt_handler(request):
        uuid = request.json['Id']
        credentials = request.headers['Authorization']

        if credentials not in context.credentials_to_data_get:
            return mockserver.make_response(
                'Unauthorized: Access is denied due to invalid credentials',
                content_type='text/html',
                status=401,
            )

        expected_uuid, _ = context.credentials_to_data_get[credentials]

        if uuid != expected_uuid:
            return {'Success': False, 'Message': 'Receipt not found'}

        return {
            'Success': True,
            'Model': {
                'Items': [],
                'AdditionalData': {
                    'Id': uuid,
                    'Amount': 250.0,
                    'DateTime': '2019-10-01T10:11:00',
                    'DeviceNumber': '123',
                    'DocumentNumber': '456',
                    'FiscalNumber': '789',
                    'FiscalSign': '123',
                    'Ofd': 'OOO Тест',
                    'OfdReceiptUrl': 'https://demo.ofd.ru/rec/123',
                    'OrganizationInn': '123',
                    'RegNumber': '456',
                    'SessionCheckNumber': '789',
                    'SessionNumber': '000',
                    'Type': '123',
                },
            },
        }

    @mockserver.json_handler('cashbox-cloud-kassir/kkt/get-all')
    def _mock_get_all(request):
        print(request.headers['Authorization'])
        if (
                request.headers['Authorization']
                == 'Basic c3VwZXJfcGFyazpwYXNzdzByZA=='
        ):
            return [
                {
                    'Inn': '0123456789',
                    'DeviceNumber': '1',
                    'FiscalNumber': '1',
                },
            ]
        if (
                request.headers['Authorization']
                == 'Basic c3VwZXJfcGFyazpwYXNzdzByZDI='
        ):
            return []
        return mockserver.make_response(status=401)

    context.post_receipt_handler = _mock_post_receipt_handler
    context.receipt_status_handler = _mock_get_receipt_status_handler
    context.get_receipt_handler = _mock_get_receipt_handler

    return context


@pytest.fixture(name='personal_tins_retrieve')
def _personal_tins_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/tins/retrieve')
    async def mock_callback(request):
        tin_id = request.json['id']
        return {'id': tin_id, 'value': tin_id[:-3]}

    return mock_callback


@pytest.fixture(name='atol_get_token')
def atol_get_token(mockserver):
    @mockserver.json_handler('cashbox-atol/possystem/v4/getToken')
    def _mock_get_token(request):
        return {'timestamp': '11.11.2019 10:00:00', 'token': 'token_1'}

    return _mock_get_token


@pytest.fixture(name='geotracks')
def geotracks(mockserver):
    @mockserver.json_handler('/driver-trackstory/shorttrack')
    def mock_geotracks(request):
        return {'adjusted': []}

    return mock_geotracks


@pytest.fixture(name='fleet_parks')
def fleet_parks(mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def mock_fleet_parks(request):
        if request.json['query']['park']['ids'][0] != 'big_park':
            return {
                'parks': [
                    {
                        'id': request.json['query']['park']['ids'][0],
                        'login': '1',
                        'name': '1',
                        'is_active': True,
                        'city_id': '1',
                        'locale': '1',
                        'is_billing_enabled': True,
                        'is_franchising_enabled': True,
                        'country_id': '1',
                        'demo_mode': False,
                        'geodata': {'lat': 1, 'lon': 1, 'zoom': 1},
                        'driver_partner_source': 'self_assign',
                    },
                ],
            }
        return {
            'parks': [
                {
                    'id': request.json['query']['park']['ids'][0],
                    'login': '1',
                    'name': '1',
                    'is_active': True,
                    'city_id': '1',
                    'locale': '1',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': '1',
                    'demo_mode': False,
                    'geodata': {'lat': 1, 'lon': 1, 'zoom': 1},
                },
            ],
        }

    return mock_fleet_parks
