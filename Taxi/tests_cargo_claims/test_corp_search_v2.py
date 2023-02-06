import pytest

from . import utils_v2


SEARCH_DEFAULT_REQUEST = {'offset': 0, 'limit': 10}


@pytest.mark.parametrize(
    'handler',
    [
        '/api/integration/v2/claims/search',
        '/api/integration/v2/claims/search/active',
    ],
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
                    '__default__': {
                        'enabled': True,
                        'yt-use-runtime': False,
                        'yt-timeout-ms': 1000,
                        'ttl-days': 3650,
                    },
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
                    '__default__': {
                        'enabled': False,
                        'yt-use-runtime': False,
                        'yt-timeout-ms': 1000,
                        'ttl-days': 3650,
                    },
                },
            ),
        ),
    ],
)
# handlers use common code with v1/claims/search, so test only multipoints
async def test_search_v2(
        taxi_cargo_claims, get_default_headers, state_controller, handler: str,
):
    state_controller.use_create_version('v2')
    request = utils_v2.get_create_request()
    state_controller.handlers().create.request = request
    claim_info = await state_controller.apply(target_status='new')

    claim_id = claim_info.claim_id
    point_ids = utils_v2.get_point_id_to_claim_point_id(
        request, claim_info.claim_full_response,
    )

    expected_claim = utils_v2.get_default_response_v2(claim_id, point_ids)
    if handler == '/api/integration/v2/claims/search':
        expected_claim['initiator_yandex_login'] = 'abacaba'
    expected_response = {'claims': [expected_claim]}

    response = await taxi_cargo_claims.post(
        handler, json=SEARCH_DEFAULT_REQUEST, headers=get_default_headers(),
    )

    assert response.status_code == 200

    json = response.json()
    if 'cursor' in json:
        json.pop('cursor')
    utils_v2.drop_ts(json['claims'])
    assert json == expected_response


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
                    '__default__': {
                        'enabled': True,
                        'yt-use-runtime': False,
                        'yt-timeout-ms': 1000,
                        'ttl-days': 3650,
                    },
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
                    '__default__': {
                        'enabled': False,
                        'yt-use-runtime': False,
                        'yt-timeout-ms': 1000,
                        'ttl-days': 3650,
                    },
                },
            ),
        ),
    ],
)
async def test_dragon_free_performer_lookup(
        taxi_cargo_claims, get_default_headers, create_segment,
):
    await create_segment()

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        json=SEARCH_DEFAULT_REQUEST,
        headers=get_default_headers(),
    )

    searched_claim = next(claim for claim in response.json()['claims'])

    assert searched_claim['available_cancel_state'] == 'free'


async def test_cursor_same_result(
        taxi_cargo_claims,
        state_controller,
        encode_cursor,
        get_default_headers,
):
    await utils_v2.create_claims_for_search(state_controller)

    request_json = {'offset': 0, 'limit': 5}

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        headers=get_default_headers(),
        json=request_json,
    )
    assert response.status_code == 200
    first_response = response.json()

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        headers=get_default_headers(),
        json={'cursor': encode_cursor(request_json)},
    )
    assert response.status_code == 200
    second_response = response.json()

    assert first_response == second_response


async def test_full_response_by_cursors(
        taxi_cargo_claims, state_controller, get_default_headers,
):
    await utils_v2.create_claims_for_search(state_controller)
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        headers=get_default_headers(),
        json={'offset': 0, 'limit': 5},
    )
    assert response.status_code == 200
    expected_claims = response.json()['claims']
    assert len(expected_claims) == 3

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        headers=get_default_headers(),
        json={'offset': 0, 'limit': 1},
    )
    assert response.status_code == 200
    response_json = response.json()
    claims_by_cursor = response_json['claims']
    cursor = response_json['cursor']
    while cursor is not None:
        response = await taxi_cargo_claims.post(
            '/api/integration/v2/claims/search',
            headers=get_default_headers(),
            json={'cursor': cursor},
        )
        assert response.status_code == 200
        response_json = response.json()
        claims_by_cursor += response_json['claims']
        cursor = response_json.get('cursor')
    assert expected_claims == claims_by_cursor


async def test_sdd(
        taxi_cargo_claims,
        get_default_headers,
        get_default_corp_client_id,
        taxi_config,
        create_claim_segment_matched_car_taxi_class,
        taxi_tariff='night',
        display_tariff='same_day_delivery',
):
    taxi_config.set(
        CARGO_SDD_TAXI_TARIFF_SETTINGS={
            'remove_in_tariffs': True,
            'remove_in_admin_tariffs': False,
            'name': taxi_tariff,
            'display_in_corp_cabinet': display_tariff,
        },
    )

    await create_claim_segment_matched_car_taxi_class(
        get_default_corp_client_id, taxi_class='night',
    )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        json=SEARCH_DEFAULT_REQUEST,
        headers=get_default_headers(),
    )

    assert (
        response.json()['claims'][0]['matched_cars'][0]['taxi_class']
        == display_tariff
    )


async def test_phone_validation_search(taxi_cargo_claims, get_default_headers):
    response = await taxi_cargo_claims.post(
        'api/integration/v2/claims/search',
        json={'offset': 0, 'limit': 10, 'phone': 'a2001a'},
        headers=get_default_headers(),
    )

    assert response.status_code == 400


async def test_phone_validation(
        taxi_cargo_claims, mockserver, get_default_headers,
):
    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones_store():
        return mockserver.make_response(
            status=400, json={'code': 'validation-error', 'message': 'error'},
        )

    response = await taxi_cargo_claims.post(
        '/api/integration/v2/claims/search',
        json={'offset': 0, 'limit': 10, 'phone': '+79098887777'},
        headers=get_default_headers(),
    )

    assert response.status_code == 400
