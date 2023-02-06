import pytest

HEADERS = {'X-Api-Key': 'yandex_taxi'}

BASE_URL = (
    'https://m.taxi.taxi.tst.yandex.ru/webview/'
    'maas-mock?source=access-key&payment_id='
)


@pytest.mark.parametrize(
    'payment_method, expected_hash_key',
    (('APAY', 'applepay'), ('GPAY', 'googlepay'), ('CARD', 'prvs_method')),
)
@pytest.mark.pgsql('maas', files=['users.sql'])
async def test_user_key(
        load_json, taxi_maas, pgsql, payment_method, expected_hash_key,
):
    request = load_json('user_key_request.json')
    request['pay_data']['payment_method'] = payment_method
    if payment_method == 'CARD':
        request['pay_data'].pop('payment_token')
    response = await taxi_maas.post(
        '/api/0.1/user/key', headers=HEADERS, json=request,
    )

    assert response.status == 200
    body = response.json()
    payment_id = 'change_key_id_idempotency'
    assert body['payment_id'] == payment_id

    cursor = pgsql['maas'].cursor()
    cursor.execute(
        f'SELECT * FROM maas.payments WHERE payment_id = \'{payment_id}\'',
    )
    row = cursor.fetchone()
    assert row[0] == 'idempotency'
    assert row[1] == payment_id

    if payment_method == 'CARD':
        assert row[3] == 'initiated'
        assert row[5] == f'{BASE_URL}{payment_id}'
    else:
        assert row[3] == 'success'

    cursor = pgsql['maas'].cursor()
    cursor.execute(
        f'SELECT * FROM maas.users WHERE maas_user_id = \'maas_user_id\'',
    )
    row = cursor.fetchone()
    db_access_key_hash = row[3]
    assert db_access_key_hash == expected_hash_key


@pytest.mark.pgsql('maas', files=['payments.sql'])
@pytest.mark.parametrize(
    'payment_id, expected_status',
    (
        ('change_key_id_success', 'SUCCESS'),
        pytest.param(
            'change_key_id_success',
            'PROCESSING',
            marks=pytest.mark.config(
                MAAS_MOCK_VTB_SETTINGS={'paying_status_ttl': 36000000},
            ),
        ),
        ('change_key_id_canceled', 'CANCELED'),
        ('change_key_id_failed', 'ERROR'),
        pytest.param(
            'change_key_id_failed',
            'PROCESSING',
            marks=pytest.mark.config(
                MAAS_MOCK_VTB_SETTINGS={'paying_status_ttl': 36000000},
            ),
        ),
    ),
)
async def test_pay_status(taxi_maas, payment_id, expected_status):
    response = await taxi_maas.post(
        '/api/0.1/pay/status',
        headers=HEADERS,
        json={'payment_id': payment_id},
    )

    assert response.status == 200
    body = response.json()
    assert body['payment']['auth']['status']['status'] == expected_status


@pytest.mark.pgsql('maas', files=['payments.sql', 'users.sql'])
async def test_mock_set_pay_status(taxi_maas):
    payment_id = 'change_key_id_initiated'

    response = await taxi_maas.post(
        '/mock/set/pay/status',
        headers=HEADERS,
        json={'payment_id': payment_id, 'status': 'success'},
    )

    assert response.status == 200

    response = await taxi_maas.post(
        '/api/0.1/pay/status',
        headers=HEADERS,
        json={'payment_id': payment_id},
    )

    body = response.json()
    assert body['payment']['auth']['status']['status'] == 'SUCCESS'
