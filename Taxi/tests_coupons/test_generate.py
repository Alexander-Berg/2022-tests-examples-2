import pytest

from tests_coupons import util

TANKER_ARGS = [
    {'key': 'friend_count', 'value': '5'},
    {'key': 'some_key', 'value': 'some_value'},
]

DEFAULT_REASON = {
    'default_value': 'За всё хорошее',
    'tanker_key': 'referral_promocode.reward.promocode.reason',
    'tanker_args': [
        {'key': 'friend_count', 'value': '5'},
        {'key': 'some_key', 'value': 'some_value'},
    ],
}

# Generated via `tvmknife unittest service -s 2001716 -d 2001716`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IggItJZ6ELSWeg'
    ':Ub6VhOZcj0V93-TSypyEqqwxTUs7uaaeb46PA'
    'HNiMnAuNrGXVbuR9wSfKvjTM_7defPpjqsiGf'
    'xeZLUdjcM8pVxLeXC-cE5O62YmXLyQawXU5IKB'
    'NFna0ZbvepJ69NeXag1hfSiqCXYi6Ih_v39fEjO8MWeSGGNsThNX9Ze9k1s'
)


@pytest.mark.parametrize(
    'body,expected_status_code',
    [
        pytest.param(
            {'series_id': 'series_id_0', 'token': 'idempotency_key_0'},
            400,
            id='missing_phone_id_and_yandex_uid',
        ),
        pytest.param(
            {
                'series_id': 'series_id_0',
                'token': 'idempotency_key_0',
                'phone_id': '133700000000000000000000',
                'yandex_uid': 'yandex_uid_0',
                'application_name': 'iphone',
            },
            200,
            id='generate_for_phone_id_and_yandex_uid',
        ),
        pytest.param(
            {
                'series_id': 'series_id_0',
                'token': 'idempotency_key_0',
                'yandex_uid': 'yandex_uid_0',
            },
            # TODO: should be 400, https://st.yandex-team.ru/TAXIBACKEND-32324
            200,
            id='yandex_uid_without_application_name',
        ),
        pytest.param(
            {
                'series_id': 'series_id_0',
                'token': 'idempotency_key_0',
                'phone_id': '133700000000000000000000',
            },
            200,
            id='generate_for_phone_id',
        ),
        pytest.param(
            {
                'series_id': 'series_id_0',
                'token': 'idempotency_key_0',
                'yandex_uid': 'yandex_uid_0',
                'application_name': 'iphone',
            },
            200,
            id='generate_for_yandex_uid_and_application_name',
        ),
    ],
)
async def test_request_parsing(taxi_coupons, body, expected_status_code):
    """
    This test is intended to check that the data is parsed correctly.
    """
    response = await taxi_coupons.post('/internal/generate', body)
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    'series_id, expected_code',
    [
        pytest.param('series_id_0', 200, id='correct_series'),
        pytest.param('series_id_42', 400, id='missing_series'),
        pytest.param('series_id_2', 400, id='not_unique_series'),
        pytest.param('series_id_3', 400, id='series_without_value'),
        pytest.param('0123456789abcde', 400, id='long_series_name'),
    ],
)
async def test_series_checks(taxi_coupons, series_id, expected_code):
    """
    This test is intended to check that promocode series checked correctly.
    """
    body = {
        'series_id': series_id,
        'token': 'idempotency_key_0',
        'phone_id': '133700000000000000000000',
        'yandex_uid': 'yandex_uid_0',
        'application_name': 'iphone',
    }
    response = await taxi_coupons.post('/internal/generate', body)
    assert response.status_code == expected_code


@pytest.mark.parametrize(
    'expected_reason',
    [
        pytest.param(None, id='No reason'),
        pytest.param(DEFAULT_REASON, id='No tanker_args'),
        pytest.param(
            {**DEFAULT_REASON, **{'tanker_args': TANKER_ARGS}},
            id='Standard reason',
        ),
    ],
)
async def test_generate_for_yandex_uid(taxi_coupons, mongodb, expected_reason):
    """
    This test sends 2 requests for yandex_uid-type generation
    with the same idempotency token and checks that proper
    docs in databases 'promocodes' and 'user_coupons' were created
    """
    # existing document in mocked database 'db_promocode_series.json'
    series_doc = {
        '_id': 'series_id_0',
        'clear_text': True,
        'is_unique': True,
        'value': 150,
    }

    body = {
        'series_id': series_doc['_id'],
        'token': 'idempotency_key_0',
        'yandex_uid': 'yandex_uid_0',
        'application_name': 'iphone',
        'reason': expected_reason,
        'reason_type': 'referral_reward',
    }

    responses = []

    for _ in (0, 1):
        response = await taxi_coupons.post('/internal/generate', body)
        assert response.status_code == 200
        assert 'promocode' in response.json()
        responses.append(response)

    bodies = [resp.json() for resp in responses]
    assert bodies[0] == bodies[1]  # idempotency check

    # check that proper promocodes doc was created
    code = bodies[0]['promocode']
    promocodes = list(mongodb.promocodes.find({'code': code}))
    assert len(promocodes) == 1
    promocode = promocodes[0]
    assert promocode['generate_token'] == body['token']
    assert promocode['series_id'] == body['series_id']
    assert promocode['value'] == series_doc['value']

    if expected_reason:
        assert promocode.get('reason') == {
            **expected_reason,
            'reason_type': 'referral_reward',
        }
    else:
        assert 'reason' not in promocode

    # check that proper user_coupons doc was created
    user_coupons = list(
        mongodb.user_coupons.find(
            {'yandex_uid': body['yandex_uid'], 'brand_name': 'yataxi'},
        ),
    )
    assert len(user_coupons) == 1
    user_coupon = user_coupons[0]
    assert len(user_coupon['promocodes']) == 1
    promocodes = user_coupon['promocodes'][0]
    assert promocodes['code'] == code


@pytest.mark.now('2019-03-01T12:00:00+0300')
@pytest.mark.parametrize('series_id', ['series_id_0', 'SERIES_id_0'])
async def test_generate_for_phone_id(taxi_coupons, mongodb, series_id):
    """
    This test sends 2 requests for phone_id-type generation
    with the same idempotency token and checks that proper
    doc in database 'promocodes' was created
    """
    series_doc = mongodb.promocode_series.find_one(series_id.lower())
    assert series_doc

    body = {
        'token': 'idempotency_key_0',
        'series_id': series_id,
        'phone_id': '133700000000000000000000',
        'application_name': 'iphone',
    }

    responses = []

    for _ in (0, 1):
        response = await taxi_coupons.post('/internal/generate', body)
        assert response.status_code == 200
        resp_body = response.json()
        assert 'promocode' in resp_body
        assert len(resp_body['promocode']) == 20
        responses.append(response)

    bodies = [resp.json() for resp in responses]
    assert bodies[0] == bodies[1]  # idempotency check

    # check that proper promocodes doc was created
    code = bodies[0]['promocode']
    promocodes = list(mongodb.promocodes.find({'code': code}))
    assert len(promocodes) == 1
    # promocodes are case-insensitive
    assert code == code.lower()

    promocode = promocodes[0]
    assert promocode['generate_token'] == body['token']
    assert promocode['series_id'] == body['series_id'].lower()
    assert promocode['value'] == series_doc['value']
    assert str(promocode['phone_id']) == body['phone_id']
    assert promocode['updated_at'] == util.utc_datetime_from_str(
        '2019-03-01T12:00:00+03:00',
    )


@pytest.mark.config(TVM_ENABLED=True)
async def test_metrics_exist(taxi_coupons, taxi_coupons_monitor):
    body = {
        'token': 'idempotency_key_0',
        'series_id': 'series_id_0',
        'phone_id': '133700000000000000000000',
        'application_name': 'iphone',
        'reason_type': 'referral_reward',
        'service': 'taxi',
    }
    response = await taxi_coupons.post(
        '/internal/generate',
        headers={'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 200

    metrics_name = 'generate-statistics'
    metrics = await taxi_coupons_monitor.get_metrics(metrics_name)
    value = metrics[metrics_name]
    assert (
        'referral_reward'
        in value['generated']['coupons']['taxi']['series_id_0']
    )


@pytest.mark.parametrize(
    'value,expected_status_code,expected_data',
    [
        pytest.param(
            None,
            400,
            {
                'code': 'BadRequest',
                'message': 'Value is required for volatile series',
            },
            id='missing_request_value',
        ),
        pytest.param(
            200,
            400,
            {
                'code': 'BadRequest',
                'message': (
                    'Request value \'200.0\' is greater than series '
                    'value \'150.0\''
                ),
            },
            id='big_request_value',
        ),
        pytest.param(150, 200, None, id='value_is_150'),
        pytest.param(100, 200, None, id='value_is_100'),
        pytest.param(42, 200, None, id='value_is_float'),
    ],
)
async def test_generate_of_volatile_series(
        taxi_coupons, mongodb, value, expected_status_code, expected_data,
):
    body = {
        'series_id': 'series_id_1',
        'token': 'idempotency_key_0',
        'yandex_uid': 'yandex_uid_0',
    }
    if value is not None:
        body['value'] = value
    response = await taxi_coupons.post('/internal/generate', body)
    assert response.status_code == expected_status_code
    data = response.json()
    if expected_data is not None:
        assert data == expected_data
    if expected_status_code == 200 and value is not None:
        doc = mongodb.promocodes.find_one({'code': data['promocode']})
        assert doc
        assert doc['value'] == value


@pytest.mark.now('2019-03-01T12:00:00+0300')
@pytest.mark.parametrize(
    'expire_at,expected_status_code',
    [
        pytest.param(
            '2019-03-01T11:00:00+03:00', 400, id='expire_at less than now',
        ),
        pytest.param(
            '2019-03-01T12:00:00+03:00', 400, id='expire_at equals to now',
        ),
        pytest.param(
            '2019-03-01T13:00:00+03:00', 200, id='expire_at more than now',
        ),
    ],
)
async def test_generate_with_expire_at(
        taxi_coupons, mongodb, expire_at, expected_status_code,
):
    body = {
        'series_id': 'series_id_0',
        'token': 'idempotency_key_0',
        'yandex_uid': 'yandex_uid_0',
        'expire_at': expire_at,
    }
    response = await taxi_coupons.post('/internal/generate', body)
    assert response.status_code == expected_status_code
    data = response.json()
    if response.status_code == 200:
        doc = mongodb.promocodes.find_one({'code': data['promocode']})
        assert doc
        assert doc['expire_at'] == util.utc_datetime_from_str(expire_at)


@pytest.mark.now('2019-03-01T12:00:00+0300')
@pytest.mark.parametrize(
    'series, expected_params',
    [
        (
            'series_id_4',
            {
                'currency_code': 'RUB',
                'expire_at': '2019-03-01T10:00:00+00:00',
                'value': 150,
                'value_numeric': '150',
            },
        ),
        (
            'series_id_5',
            {
                'currency_code': 'RUB',
                'expire_at': '2019-03-01T10:00:00+00:00',
                'limit': 1000.0,
                'percent': 20,
                'value': 1000,
                'value_numeric': '1000',
            },
        ),
        (
            'series_id_6',
            {
                'currency_code': 'RUB',
                'expire_at': '2019-03-01T10:00:00+00:00',
                'limit': 1000.0,
                'percent': 20,
                'value': 1000,
                'series_meta': {'business_type': 'discount'},
                'value_numeric': '1000',
            },
        ),
    ],
)
async def test_generate_additional_params(
        taxi_coupons, mongodb, series, expected_params,
):
    expire_at = '2019-03-01T13:00:00+03:00'
    body = {
        'series_id': series,
        'token': 'idempotency_key_0',
        'yandex_uid': 'yandex_uid_0',
        'expire_at': expire_at,
    }
    response = await taxi_coupons.post('/internal/generate', body)
    assert response.status_code == 200
    data = response.json()
    assert mongodb.promocodes.find_one({'code': data['promocode']})
    promocode_params = data['promocode_params']
    assert promocode_params == expected_params


@pytest.mark.now('2019-03-01T12:00:00+0300')
@pytest.mark.parametrize(
    'brands, series, yandex_uid',
    [
        (
            [
                'eats',
                'yataxi',
                'eats',
                'yataxi',
                'turboapp',
                'turboapp',
                'yataxi',
            ],
            'series_id_6',
            '4085180751',
        ),
    ],
)
async def test_insert_promocodes_to_user_coupons_for_different_brands(
        taxi_coupons, mongodb, brands, series, yandex_uid,
):
    requests = []
    for i, brand in enumerate(brands):
        requests.append(
            {
                'series_id': series,
                'yandex_uid': yandex_uid,
                'token': f'idemp_token_{i}',
                'brand_name': brand,
            },
        )

    for body in requests:
        response = await taxi_coupons.post('/internal/generate', body)
        assert response.status_code == 200

    for brand in brands:
        user_coupons = mongodb.user_coupons.find_one(
            {'yandex_uid': yandex_uid, 'brand_name': brand},
        )
        assert len(
            [promo['code'] for promo in user_coupons['promocodes']],
        ) == brands.count(brand)
        assert brand == user_coupons['brand_name']


@pytest.mark.parametrize(
    'value, value_numeric, expected_status_code',
    [
        pytest.param(150, '115.5', 200),
        pytest.param(100, '115', 200),
        pytest.param(None, '115.5', 200),
    ],
)
async def test_generate_with_value_numeric(
        taxi_coupons, mongodb, value, value_numeric, expected_status_code,
):
    body = {
        'series_id': 'series_id_1',
        'token': 'idempotency_key_0',
        'yandex_uid': 'yandex_uid_0',
        'value_numeric': value_numeric,
    }
    if value is not None:
        body['value'] = value
    response = await taxi_coupons.post('/internal/generate', body)
    assert response.status_code == expected_status_code
    data = response.json()
    assert data['promocode_params']['value'] == int(float(value_numeric))
    assert data['promocode_params']['value_numeric'] == value_numeric

    doc = mongodb.promocodes.find_one({'code': data['promocode']})
    assert doc
    assert doc['value'] == float(value_numeric)
