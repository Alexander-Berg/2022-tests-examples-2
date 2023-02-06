import pytest

import common

HEADERS = {'X-Api-Key': 'yandex_taxi'}

BASE_URL = (
    'https://m.taxi.taxi.tst.yandex.ru/webview/'
    'maas-mock?source=pay&payment_id='
)


@pytest.fixture(name='custom_services')
def _mock_services(taxi_maas, mockserver):
    @mockserver.json_handler('/maas/vtb/v1/sub/reserve')
    async def _mock_maas_vtb_v1_sub_reserve(request):
        return {
            'price': 10050,
            'service_sub_id': 'maas_sub_id',
            'service_tariff_id': 'maas_tariff_id',
            'sub_duration': 30,
            'trip': {'count': 10, 'single': -1, 'total': -1, 'type': 'COUNT'},
            'reserve_time': '2021-08-20T18:44:44Z',
        }

    @mockserver.json_handler('/maas/vtb/v1/sub/activate')
    async def _mock_maas_vtb_v1_sub_activate(request):
        return {'activate_time': '2021-08-20T18:45:44Z'}

    @mockserver.json_handler('/maas/vtb/v1/sub/cancel')
    async def _mock_maas_vtb_v1_sub_cancel(request):
        return {'cancel_time': '2021-08-20T18:45:44Z'}


async def test_user_register(taxi_maas):
    request = {'phone': '71234567890'}
    response = await taxi_maas.post(
        '/api/0.1/user/register', headers=HEADERS, json=request,
    )

    assert response.status == 200
    assert response.json() == {
        'maas_user_id': 'e200883de0776be51cf24654cc0c53b084648dc3',
    }


@pytest.mark.config(MAAS_TARIFFS=common.get_maas_tariffs())
@pytest.mark.parametrize(
    'idmp_token, payment_method_type, expected_status',
    (
        ('idmp_token_1', 'CARD', 'initiated'),
        ('idmp_token_2', 'APAY', 'success'),
    ),
)
@pytest.mark.pgsql('maas', files=['users.sql'])
async def test_subscription_pay_start(
        taxi_maas,
        load_json,
        custom_services,
        pgsql,
        idmp_token,
        payment_method_type,
        expected_status,
):
    request = load_json('pay_start_base_request.json')
    request['payment']['payment_method'] = payment_method_type
    request['payment']['tran_id'] = idmp_token
    response = await taxi_maas.post(
        '/api/0.1/subscription/pay/start', headers=HEADERS, json=request,
    )
    assert response.status == 200

    payment_id = f'payment_id_{idmp_token}'
    cursor = pgsql['maas'].cursor()
    cursor.execute(
        f'SELECT * FROM maas.payments WHERE payment_id = \'{payment_id}\'',
    )
    row = cursor.fetchone()
    assert row[0] == idmp_token
    assert row[1] == payment_id
    assert row[3] == expected_status


@pytest.mark.pgsql('maas', files=['payments.sql'])
@pytest.mark.parametrize(
    'payment_id, expected_status',
    (
        ('initiated', 'CREATED'),
        ('success', 'SUCCESS'),
        pytest.param(
            'success',
            'PROCESSING',
            marks=pytest.mark.config(
                MAAS_MOCK_VTB_SETTINGS={'paying_status_ttl': 36000000},
            ),
        ),
        ('canceled', 'CANCELED'),
        ('failed', 'ERROR'),
        pytest.param(
            'failed',
            'PROCESSING',
            marks=pytest.mark.config(
                MAAS_MOCK_VTB_SETTINGS={'paying_status_ttl': 36000000},
            ),
        ),
    ),
)
async def test_subscription_pay_status(taxi_maas, payment_id, expected_status):
    response = await taxi_maas.post(
        '/api/0.1/subscription/pay/status',
        headers=HEADERS,
        json={'payment_id': payment_id},
    )

    assert response.status == 200
    body = response.json()
    assert body['payment']['auth']['status']['status'] == expected_status
    if expected_status == 'CREATED':
        assert body['payment']['url'] == f'{BASE_URL}{payment_id}'


@pytest.mark.pgsql('maas', files=['payments.sql', 'subscriptions.sql'])
async def test_mock_set_pay_status(taxi_maas, custom_services):
    payment_id = 'payment_id_initiated'
    response = await taxi_maas.post(
        '/api/0.1/subscription/pay/status',
        headers=HEADERS,
        json={'payment_id': payment_id},
    )

    body = response.json()
    assert body['payment']['auth']['status']['status'] == 'CREATED'

    response = await taxi_maas.post(
        '/mock/set/pay/status',
        headers=HEADERS,
        json={'payment_id': payment_id, 'status': 'success'},
    )

    assert response.status == 200

    response = await taxi_maas.post(
        '/api/0.1/subscription/pay/status',
        headers=HEADERS,
        json={'payment_id': payment_id},
    )

    body = response.json()
    assert body['payment']['auth']['status']['status'] == 'SUCCESS'
