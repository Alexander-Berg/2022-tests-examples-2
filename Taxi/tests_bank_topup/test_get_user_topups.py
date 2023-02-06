async def test_ok(taxi_bank_topup):
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_user_topups', json={'buid': 'bank_uid'},
    )
    assert response.status_code == 200
    json = response.json()
    assert len(json['payments']) == 10
    assert 'cursor' not in json


async def test_400(taxi_bank_topup):
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_user_topups', json={'buid': ''},
    )
    assert response.status_code == 400
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_user_topups', json={},
    )
    assert response.status_code == 400


async def test_no_topups(taxi_bank_topup):
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_user_topups', json={'buid': 'not_found'},
    )
    assert response.status_code == 200
    json = response.json()
    assert json['payments'] == []
    assert 'cursor' not in json


async def test_paging(taxi_bank_topup):
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_user_topups',
        json={'buid': 'bank_uid', 'page_size': 1},
    )
    assert response.status_code == 200
    json = response.json()
    assert len(json['payments']) == 1
    assert 'cursor' in json

    payment = json['payments'][0]
    assert payment['amount'] == '109'
    assert payment['bank_uid'] == 'bank_uid'
    assert 'created_at' in payment
    assert payment['currency'] == 'RUB'
    assert payment['cursor_key'] == 10
    assert (
        payment['idempotency_token'] == 'e1c503af-bf18-4b0a-872b-bc007e6b4d29'
    )
    assert 'payment_id' in payment
    assert payment['purchase_token'] == 'token10'
    assert payment['status'] == 'CREATED'
    assert 'updated_at' in payment
    assert payment['wallet_id'] == 'wallet_id'
    assert payment['yandex_uid'] == 'yandex_uid'
