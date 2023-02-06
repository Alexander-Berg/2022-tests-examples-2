import pytest

from tests_bank_wallet import common


@pytest.fixture
def _mock_core_statement(mockserver):
    class Context:
        def __init__(self):
            self.params_list = []
            self.params = {}

        def set_params(self, params):
            self.params = params

        def set_params_list(self, params_list):
            self.params_list = params_list

    context = Context()

    def make_trx(params):
        trx = {
            'transaction_id': '1',
            'status': 'CLEAR',
            'type': 'PURCHASE',
            'direction': 'DEBIT',
            'timestamp': '2018-02-01T12:08:48+00:00',
            'merchant': {},
            'money': {'amount': '100', 'currency': 'RUB'},
            'plus_debit': {'amount': '0', 'currency': 'RUB'},
            'plus_credit': {'amount': '0.12', 'currency': 'RUB'},
            'fees': [],
        }

        if params.get('type'):
            trx['type'] = params.get('type')
        if params.get('mcc'):
            trx['merchant']['merchant_category_code'] = params.get('mcc')
        if params.get('merchant_name'):
            trx['merchant']['merchant_name'] = params.get('merchant_name')
        if params.get('type', '') == 'C2C_BY_PHONE':
            trx['merchant'] = {
                'merchant_name': '',
                'merchant_country': '',
                'merchant_category_code': '',
            }
            trx['c2c-details'] = {
                'phone': '+79123456789',
                'bank-id': '100000000004',
                'name': 'Иван Иванович А',
                'operation-code': 'A2053112902642010000057BD2157589',
            }
            if not params.get('bank_image', False):
                trx['c2c-details']['bank-id'] = '100000000001'
        elif params.get('type', '') == 'CARD2ACCOUNT':
            if params.get('c2a_details', False):
                trx['c2a_details'] = {}
                if params.get('bank-id', '') == 'correct':
                    trx['c2a_details'] = {'bank-id': '100000000004'}
                elif params.get('bank-id', '') == 'incorrect':
                    trx['c2a_details'] = {'bank-id': '100000000001'}

        return trx

    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/info/get',
    )
    def _mock_get_transaction(request):
        return make_trx(context.params)

    @mockserver.json_handler(
        '/bank-core-statement/v1/transactions/grouped-by-status/get',
    )
    def _mock_get_transactions(request):
        trxs = list()
        for params in context.params_list:
            trxs.append(make_trx(params))

        return {'status_groups': trxs}

    return context


async def test_all_params(taxi_bank_wallet, _mock_core_statement):
    _mock_core_statement.set_params(
        {'merchant_name': 'YANDEX_EDA', 'mcc': '4321', 'type': 'PURCHASE'},
    )

    params = {'transaction_id': '1'}
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info',
        headers=common.get_headers(),
        json=params,
    )
    assert response.status_code == 200
    assert response.json()['base_info']['image'] == 'YANDEX_EDA_url'


async def test_only_type(taxi_bank_wallet, _mock_core_statement):
    for trx_type in ('PURCHASE', 'REFUND'):
        _mock_core_statement.set_params({'type': trx_type})
        response = await taxi_bank_wallet.post(
            '/v1/wallet/v1/transaction/get_info',
            headers=common.get_headers(),
            json={'transaction_id': '1'},
        )
        assert response.status_code == 200
        assert (
            response.json()['base_info']['image'] == trx_type.lower() + '_url'
        )


async def test_mcc_type(taxi_bank_wallet, _mock_core_statement):
    _mock_core_statement.set_params({'mcc': '4321', 'type': 'PURCHASE'})
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info',
        headers=common.get_headers(),
        json={'transaction_id': '1'},
    )
    assert response.status_code == 200
    assert response.json()['base_info']['image'] == '4321_url'


async def test_transfer_image(taxi_bank_wallet, _mock_core_statement):
    _mock_core_statement.set_params(
        {'type': 'C2C_BY_PHONE', 'bank_image': True},
    )
    params = {'transaction_id': '1'}
    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/transaction/get_info',
        headers=common.get_headers(),
        json=params,
    )

    assert response.status_code == 200
    assert response.json()['base_info'].get('image') == 'tinkoff_url'


async def test_trx_list_images(taxi_bank_wallet, _mock_core_statement):
    _mock_core_statement.set_params_list(
        [
            {'type': 'C2C_BY_PHONE'},
            {'type': 'C2C_BY_PHONE', 'bank_image': True},
            {'type': 'CARD2ACCOUNT'},
            {'type': 'CARD2ACCOUNT', 'c2a_details': True},
            {
                'type': 'CARD2ACCOUNT',
                'c2a_details': True,
                'bank-id': 'correct',
            },
            {
                'type': 'CARD2ACCOUNT',
                'c2a_details': True,
                'bank-id': 'incorrect',
            },
            {'merchant_name': 'YANDEX_EDA', 'mcc': '4321'},
            {'mcc': '4321', 'type': 'REFUND'},
            {'mcc': 'unknown mcc'},
        ],
    )

    response = await taxi_bank_wallet.post(
        '/v1/wallet/v1/get_transactions',
        headers=common.get_headers(),
        json={},
    )

    assert response.status_code == 200
    json = response.json()
    image_urls = tuple(map(lambda trx: trx.get('image'), json['transactions']))

    assert image_urls == (
        'transfer_out_url',
        'tinkoff_url',
        'topup_url',
        'topup_url',
        'tinkoff_url',
        'topup_url',
        'YANDEX_EDA_url',
        '4321_url',
        'purchase_url',
    )
