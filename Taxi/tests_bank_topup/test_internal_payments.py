import pytest


def get_body():
    return {'limit': 10, 'buid': 'bank_uid', 'locale': 'ru'}


def get_pending_payments_status(payments):
    actual_payments = []
    for payment in payments:
        actual_payments.append(
            [
                payment['payment']['payment_info']['payment_id'],
                payment['payment']['status'],
            ],
        )
    return actual_payments


async def test_ok(taxi_bank_topup):
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_pending_payments', json=get_body(),
    )

    expected_payment_status = [
        ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa12', 'PROCESSING'],
        ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa11', 'PROCESSING'],
        ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa10', 'PROCESSING'],
        ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa04', 'PROCESSING'],
        ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa03', 'PROCESSING'],
        ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02', 'PROCESSING'],
        ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01', 'PROCESSING'],
    ]

    json = response.json()
    assert response.status_code == 200
    assert (
        get_pending_payments_status(json['payments'])
        == expected_payment_status
    )
    assert all(
        payment['payment']['payment_info']['image'] == 'image_url'
        for payment in json['payments']
    )


async def test_pagination(taxi_bank_topup):
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_pending_payments/', json=get_body(),
    )
    full = response.json()['payments']
    assert len(full) == 7

    for page_size in range(1, 7):
        paginated = []
        internal_page_size = page_size
        body = get_body()
        body['limit'] = internal_page_size
        response = await taxi_bank_topup.post(
            '/topup-internal/v1/get_pending_payments/', json=body,
        )
        assert response.status_code == 200
        page = response.json()['payments']
        while page:
            assert len(page) <= internal_page_size
            paginated.extend(page)
            internal_page_size += 1
            body = get_body()
            body['cursor_key'] = page[-1]['cursor_key']
            body['limit'] = internal_page_size
            response = await taxi_bank_topup.post(
                '/topup-internal/v1/get_pending_payments/', json=body,
            )
            assert response.status_code == 200
            page = response.json()['payments']
        assert full == paginated


async def test_nothing(taxi_bank_topup):
    body = get_body()
    body['buid'] = 'wrong_uid'
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_pending_payments/', json=body,
    )
    json = response.json()
    assert response.status_code == 200
    assert not json['payments']


async def test_no_succeeded_status(taxi_bank_topup):
    body = get_body()
    body['buid'] = 'bank_uid_succeeded'
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_pending_payments/', json=body,
    )
    json = response.json()
    assert response.status_code == 200
    assert len(json['payments']) == 1
    assert json['payments'][0]['payment']['status'] == 'PROCESSING'


@pytest.mark.parametrize(
    'locale, topup',
    [('en', 'Top up'), ('ru', 'Пополнение'), ('unknown', 'Пополнение')],
)
async def test_tanker_locales(
        taxi_bank_topup, locale, topup, pgsql, taxi_config,
):
    body = get_body()
    body['locale'] = locale
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_pending_payments/', json=body,
    )
    payment = response.json()['payments'][0]['payment']
    assert payment['payment_info']['name'] == topup


async def test_pagination_shift(taxi_bank_topup):
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_pending_payments/', json=get_body(),
    )
    full = response.json()['payments']
    assert len(full) == 7

    for shift in range(1, 7):
        cursor_key = None
        paginated = []
        while True:
            body = get_body()
            if cursor_key:
                body['cursor_key'] = cursor_key
            response = await taxi_bank_topup.post(
                '/topup-internal/v1/get_pending_payments/', json=body,
            )
            assert response.status_code == 200
            payments = response.json()['payments']
            assert len(payments) <= 7
            if not payments:
                break
            last = min(shift, len(payments))
            paginated.extend(payments[:last])
            cursor_key = paginated[-1].get('cursor_key')
        assert full == paginated


async def test_filter_by_agreement_ok(taxi_bank_topup, pgsql):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'update bank_topup.payments '
        'set wallet_id = NULL, public_agreement_id = \'agreement_id\' '
        'where payment_id in %s ',
        (
            (
                'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa11',
                'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa06',
                'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa04',
                'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02',
                'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01',
                'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa00',
            ),
        ),
    )
    body = get_body()
    body['agreement_id'] = 'agreement_id'
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_pending_payments', json=body,
    )

    expected_payment_status = [
        ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa11', 'PROCESSING'],
        ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa04', 'PROCESSING'],
        ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02', 'PROCESSING'],
        ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01', 'PROCESSING'],
    ]

    json = response.json()
    assert response.status_code == 200
    assert (
        get_pending_payments_status(json['payments'])
        == expected_payment_status
    )


async def test_filter_by_agreement_id_no_payments(taxi_bank_topup):
    body = get_body()
    body['agreement_id'] = 'agreement_id'
    response = await taxi_bank_topup.post(
        '/topup-internal/v1/get_pending_payments', json=body,
    )
    json = response.json()
    assert response.status_code == 200
    assert not json['payments']
