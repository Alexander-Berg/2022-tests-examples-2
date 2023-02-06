import pytest

REDIS_TTL = 60 * 60
PARTNER_PATTERN = 'partner:places:{}'
PARTNER_ROLE_PATTERN = 'partner:roles:{}'


def make_vendor_success_response(restaurants):
    return {
        'isSuccess': True,
        'payload': {
            'id': 7,
            'restaurants': restaurants,
            'isFastFood': True,
            'timezone': 'Europe/Moscow',
            'roles': [
                {'id': 3, 'title': 'Оператор', 'role': 'ROLE_OPERATOR'},
                {'id': 4, 'title': 'Управляющий', 'role': 'ROLE_MANAGER'},
            ],
            'firstLoginAt': '2020-08-28T15:11:25+03:00',
        },
    }


def decode_members(redis_set):
    return {int(entry.decode('utf-8')) for entry in redis_set}


@pytest.mark.parametrize(
    'restaurants,place_ids,status_code,forbidden_places',
    [
        pytest.param([1, 2, 3, 4], [1, 2], 200, [], id='allowed'),
        pytest.param(
            [1, 2, 3, 4], [10, 20], 403, [10, 20], id='all_forbidden',
        ),
        pytest.param([1, 2, 3, 4], [1, 3, 20], 403, [20], id='one_forbidden'),
    ],
)
@pytest.mark.config(
    EATS_RESTAPP_AUTHORIZER_PLACE_REDIS_SETTINGS={
        'place_access_key_ttl': REDIS_TTL,
    },
)
async def test_check_access_no_cached_data(
        taxi_eats_restapp_authorizer,
        mockserver,
        redis_store,
        restaurants,
        place_ids,
        status_code,
        forbidden_places,
):
    partner_id = 111

    @mockserver.json_handler(f'/eats-vendor/api/v1/server/users/{partner_id}')
    def mock_vendor(request):
        return mockserver.make_response(
            status=200, json=make_vendor_success_response(restaurants),
        )

    response = await taxi_eats_restapp_authorizer.post(
        '/place-access/check',
        json={'partner_id': partner_id, 'place_ids': place_ids},
    )

    assert mock_vendor.times_called == 1

    assert response.status_code == status_code
    if status_code == 403:
        assert set(response.json()['place_ids']) == set(forbidden_places)

    partner_key = PARTNER_PATTERN.format(partner_id)
    assert redis_store.ttl(partner_key) == REDIS_TTL
    assert decode_members(redis_store.smembers(partner_key)) == set(
        restaurants,
    )


@pytest.mark.parametrize(
    'place_ids,status_code,forbidden_places',
    [
        pytest.param([1], 200, [], id='allowed'),
        pytest.param([1, 4, 10, 20], 403, [4, 10], id='forbidden'),
    ],
)
@pytest.mark.redis_store(
    ['sadd', 'partner:places:111', '1', '2', '20', '30'],
    ['expire', 'partner:places:111', REDIS_TTL],
)
async def test_check_access_data_in_cache(
        taxi_eats_restapp_authorizer,
        mockserver,
        place_ids,
        status_code,
        forbidden_places,
):
    partner_id = 111

    @mockserver.json_handler(f'/eats-vendor/api/v1/server/users/{partner_id}')
    def mock_vendor(request):
        pass

    response = await taxi_eats_restapp_authorizer.post(
        '/place-access/check',
        json={'partner_id': partner_id, 'place_ids': place_ids},
    )

    assert mock_vendor.times_called == 0

    assert response.status_code == status_code
    if status_code == 403:
        assert set(response.json()['place_ids']) == set(forbidden_places)


@pytest.mark.parametrize(
    'restaurants,place_ids,status_code,forbidden_places',
    [
        pytest.param([1, 2, 3, 4], [1, 2], 200, [], id='allowed'),
        pytest.param([1, 2, 3, 4], [1, 3, 20], 403, [20], id='forbidden'),
    ],
)
@pytest.mark.config(
    EATS_RESTAPP_AUTHORIZER_PLACE_REDIS_SETTINGS={
        'place_access_key_ttl': REDIS_TTL,
    },
)
async def test_check_access_sequential(
        taxi_eats_restapp_authorizer,
        mockserver,
        redis_store,
        restaurants,
        place_ids,
        status_code,
        forbidden_places,
):
    partner_id = 111

    @mockserver.json_handler(f'/eats-vendor/api/v1/server/users/{partner_id}')
    def mock_vendor(request):
        return mockserver.make_response(
            status=200, json=make_vendor_success_response(restaurants),
        )

    for _ in range(5):
        response = await taxi_eats_restapp_authorizer.post(
            '/place-access/check',
            json={'partner_id': partner_id, 'place_ids': place_ids},
        )

        assert response.status_code == status_code
        if status_code == 403:
            assert set(response.json()['place_ids']) == set(forbidden_places)

    assert mock_vendor.times_called == 1

    partner_key = PARTNER_PATTERN.format(partner_id)
    assert redis_store.ttl(partner_key) == REDIS_TTL
    assert decode_members(redis_store.smembers(partner_key)) == set(
        restaurants,
    )


async def test_reset_present_key(taxi_eats_restapp_authorizer, redis_store):
    partner_ids = [111, 112]
    restaurants = [['1', '2', '20', '30'], ['10', '21']]
    roles = [['ROLE_OPERATOR'], ['ROLE_MANAGER']]

    for partner, places in zip(partner_ids, restaurants):
        redis_store.sadd(PARTNER_PATTERN.format(partner), *places)

    for partner, functions in zip(partner_ids, roles):
        redis_store.sadd(PARTNER_ROLE_PATTERN.format(partner), *functions)

    response = await taxi_eats_restapp_authorizer.post(
        '/place-access/reset', json={'partner_id': partner_ids[0]},
    )

    assert response.status_code == 200

    assert not redis_store.exists(PARTNER_PATTERN.format(partner_ids[0]))
    assert redis_store.exists(PARTNER_PATTERN.format(partner_ids[1]))

    assert not redis_store.exists(PARTNER_ROLE_PATTERN.format(partner_ids[0]))
    assert redis_store.exists(PARTNER_ROLE_PATTERN.format(partner_ids[1]))


@pytest.mark.redis_store(
    ['sadd', 'partner:places:111', '1', '2', '20', '30'],
    ['sadd', 'partner:places:112', '10', '21'],
)
async def test_reset_missing_key(taxi_eats_restapp_authorizer, redis_store):
    partner_id = 1

    response = await taxi_eats_restapp_authorizer.post(
        '/place-access/reset', json={'partner_id': partner_id},
    )

    assert response.status_code == 200
