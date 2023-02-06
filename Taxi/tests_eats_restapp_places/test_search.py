# flake8: noqa
# pylint: disable=redefined-outer-name

import pytest

import copy

PARTNER_ID = 1

CORE_PLACES_INFO = {
    1: {
        'id': 1,
        'name': 'name1',
        'available': True,
        'currency': {'code': 'code1', 'sign': 'sign1', 'decimal_places': 1},
        'country_code': 'country_code1',
        'region': {'id': 58, 'slug': 'PENZA'},
        'address': {
            'country': 'country1',
            'city': 'city1',
            'street': 'street1',
            'building': 'building1',
            'full': 'country1 city1 street1 building1',
        },
        'show_shipping_time': True,
        'integration_type': 'native',
        'slug': 'slug1',
        'brand': {'slug': 'slug1', 'business_type': 'business_type_1'},
        'auto_stop_rules_list': [
            {'reason': 90, 'time': 11, 'self_enable_allowed': False},
            {'reason': 91, 'time': 14, 'self_enable_allowed': True},
        ],
    },
    2: {
        'id': 3,
        'name': 'name2',
        'available': True,
        'currency': {'code': 'code2', 'sign': 'sign2', 'decimal_places': 2},
        'country_code': 'country_code2',
        'address': {
            'country': 'country2',
            'city': 'city2',
            'street': 'street2',
            'building': 'building2',
            'full': 'country2 city2 street2 building2',
        },
        'show_shipping_time': True,
        'integration_type': 'native',
        'slug': 'slug2',
        'brand': {'slug': 'slug2', 'business_type': 'business_type_2'},
    },
    3: {
        'id': 5,
        'name': 'name3',
        'available': False,
        'currency': {'code': 'code3', 'sign': 'sign3', 'decimal_places': 3},
        'country_code': 'country_code3',
        'address': {
            'country': 'country3',
            'city': 'city3',
            'street': 'street3',
            'building': 'building3',
            'full': 'country3 city3 street3 building3',
        },
        'show_shipping_time': True,
        'integration_type': 'native',
        'slug': 'slug3',
        'disable_details': {
            'disable_at': '2020-07-28T09:07:12+00:00',
            'available_at': '2020-07-28T09:07:12+00:00',
            'status': 1,
            'reason': 47,
        },
        'brand': {'slug': 'slug3', 'business_type': 'business_type_3'},
        'auto_stop_rules_list': [
            {'reason': 90, 'time': 11, 'self_enable_allowed': False},
            {'reason': 91, 'time': 14, 'self_enable_allowed': True},
        ],
    },
    4: {
        'id': 6,
        'name': 'name4',
        'available': False,
        'currency': {'code': 'code4', 'sign': 'sign4', 'decimal_places': 4},
        'country_code': 'country_code4',
        'address': {
            'country': 'country4',
            'city': 'city4',
            'street': 'street4',
            'building': 'building4',
            'full': 'country4 city4 street4 building4',
        },
        'show_shipping_time': True,
        'integration_type': 'native',
        'slug': 'slug4',
        'disable_details': {
            'disable_at': '2020-07-28T09:07:12+00:00',
            'available_at': '2020-07-28T09:07:12+00:00',
            'status': 1,
            'reason': 47,
        },
        'brand': {'slug': 'slug4', 'business_type': 'business_type_4'},
    },
}

SERVICE_PLACES_INFO = {
    1: {
        'id': 1,
        'name': 'name1',
        'is_available': True,
        'is_switching_on_requested': False,
        'is_plus_enabled': False,
        'currency': {'code': 'code1', 'sign': 'sign1', 'decimal_places': 1},
        'country_code': 'country_code1',
        'region_slug': 'PENZA',
        'address': 'street1, building1, city1, country1',
        'show_shipping_time': True,
        'integration_type': 'native',
        'slug': 'slug1',
        'brand': {'slug': 'slug1', 'business_type': 'business_type_1'},
        'subscription': {
            'is_trial': True,
            'need_alerting_about_finishing_trial': False,
            'tariff_type': 'free',
            'valid_until_iso': '2022-07-27T00:00:00+00:00',
        },
    },
    2: {
        'id': 3,
        'name': 'name2',
        'is_plus_enabled': False,
        'is_available': True,
        'is_switching_on_requested': False,
        'currency': {'code': 'code2', 'sign': 'sign2', 'decimal_places': 2},
        'country_code': 'country_code2',
        'address': 'street2, building2, city2, country2',
        'show_shipping_time': True,
        'integration_type': 'native',
        'slug': 'slug2',
        'brand': {'slug': 'slug2', 'business_type': 'business_type_2'},
        'subscription': {
            'is_trial': True,
            'need_alerting_about_finishing_trial': False,
            'tariff_type': 'business_plus',
            'valid_until_iso': '2022-06-27T00:00:00+00:00',
        },
    },
    3: {
        'id': 5,
        'name': 'name3',
        'is_plus_enabled': False,
        'is_available': False,
        'is_switching_on_requested': True,
        'currency': {'code': 'code3', 'sign': 'sign3', 'decimal_places': 3},
        'country_code': 'country_code3',
        'address': 'street3, building3, city3, country3',
        'show_shipping_time': True,
        'integration_type': 'native',
        'slug': 'slug3',
        'disable_details': {
            'disable_at': '2020-07-28T09:07:12+00:00',
            'available_at': '2020-07-28T09:07:12+00:00',
            'status': 1,
            'reason': 47,
        },
        'brand': {'slug': 'slug3', 'business_type': 'business_type_3'},
        'can_be_enabled': True,
        'subscription': {
            'is_trial': True,
            'need_alerting_about_finishing_trial': False,
            'tariff_type': 'business',
            'valid_until_iso': '2022-05-27T00:00:00+00:00',
        },
    },
    4: {
        'id': 6,
        'name': 'name4',
        'is_available': False,
        'is_switching_on_requested': False,
        'is_plus_enabled': False,
        'currency': {'code': 'code4', 'sign': 'sign4', 'decimal_places': 4},
        'country_code': 'country_code4',
        'address': 'street4, building4, city4, country4',
        'show_shipping_time': True,
        'integration_type': 'native',
        'slug': 'slug4',
        'disable_details': {
            'disable_at': '2020-07-28T09:07:12+00:00',
            'available_at': '2020-07-28T09:07:12+00:00',
            'status': 1,
            'reason': 47,
        },
        'brand': {'slug': 'slug4', 'business_type': 'business_type_4'},
        'can_be_enabled': True,
        'subscription': {
            'is_trial': False,
            'need_alerting_about_finishing_trial': True,
            'tariff_type': 'business_plus',
            'valid_until_iso': '2022-05-26T00:00:00+00:00',
        },
    },
}

TEST_CONFIG_COUNTRIES_WITH_PLUS = ['country_code1', 'country_code4']
PLACE_IDS = [1, 2, 3, 4, 5, 6, 7]


@pytest.fixture
def mock_authorizer_places_list(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/list')
    def _mock_authorizer(request):
        assert request.json == {'partner_id': PARTNER_ID}
        return mockserver.make_response(
            status=200, json={'is_success': True, 'place_ids': PLACE_IDS},
        )


@pytest.fixture
def mock_eats_core_places_info(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/info')
    def _mock_core(request):
        if request.json['place_ids'] == [1, 2]:
            return mockserver.make_response(
                status=200, json={'payload': [CORE_PLACES_INFO[1]]},
            )
        if request.json['place_ids'] == [2, 3]:
            return mockserver.make_response(
                status=200, json={'payload': [CORE_PLACES_INFO[2]]},
            )
        if request.json['place_ids'] == [4, 5]:
            return mockserver.make_response(
                status=200, json={'payload': [CORE_PLACES_INFO[3]]},
            )
        if request.json['place_ids'] == [6, 7]:
            return mockserver.make_response(
                status=200, json={'payload': [CORE_PLACES_INFO[4]]},
            )
        if request.json['place_ids'] == [1, 2, 3, 4]:
            return mockserver.make_response(
                status=200,
                json={'payload': [CORE_PLACES_INFO[1], CORE_PLACES_INFO[2]]},
            )
        if request.json['place_ids'] == [1, 2, 3, 4, 5, 6, 7]:
            return mockserver.make_response(
                status=200,
                json={
                    'payload': [
                        CORE_PLACES_INFO[1],
                        CORE_PLACES_INFO[2],
                        CORE_PLACES_INFO[3],
                        CORE_PLACES_INFO[4],
                    ],
                },
            )
        if request.json['place_ids'] == [7]:
            return mockserver.make_response(status=200, json={'payload': []})
        return mockserver.make_response(
            status=404, json={'code': '', 'message': ''},
        )


@pytest.mark.pgsql(
    'eats_restapp_places', files=['insert_switching_on_requested.sql'],
)
async def test_service_respond_successfully_to_get_places_info_for_ids_from_place_ids_beginnig(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_places_info,
        mock_eats_place_subscriptions,
        pgsql,
):
    service_response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 2, 'cursor': 0},
    )

    sorted_response = {
        'payload': sorted(
            service_response.json()['payload'], key=lambda x: x['id'],
        ),
        'meta': service_response.json()['meta'],
    }

    expected_response = {
        'payload': [SERVICE_PLACES_INFO[1], SERVICE_PLACES_INFO[2]],
        'meta': {'can_fetch_next': True, 'cursor': 3},
    }

    assert service_response.status_code == 200
    assert sorted_response == expected_response


@pytest.mark.pgsql(
    'eats_restapp_places', files=['insert_switching_on_requested.sql'],
)
async def test_service_respond_successfully_to_get_places_info_for_ids_from_place_ids_middle(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_places_info,
        mock_eats_place_subscriptions,
        pgsql,
):
    service_response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 1, 'cursor': 5},
    )

    expected_response = {
        'payload': [SERVICE_PLACES_INFO[4]],
        'meta': {'can_fetch_next': False},
    }

    assert service_response.status_code == 200
    assert service_response.json() == expected_response


@pytest.mark.config(
    EATS_RESTAPP_PLACES_PLUS_ENABLED_COUNTRIES=TEST_CONFIG_COUNTRIES_WITH_PLUS,
)
@pytest.mark.pgsql(
    'eats_restapp_places', files=['insert_switching_on_requested.sql'],
)
async def test_set_plus_enabled_from_config(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_places_info,
        mock_eats_place_subscriptions,
        pgsql,
):
    service_response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 1, 'cursor': 5},
    )

    expected_payload = copy.deepcopy(SERVICE_PLACES_INFO[4])
    expected_payload['is_plus_enabled'] = True
    expected_response = {
        'payload': [expected_payload],
        'meta': {'can_fetch_next': False},
    }

    assert service_response.status_code == 200
    assert service_response.json() == expected_response


@pytest.mark.pgsql(
    'eats_restapp_places', files=['insert_switching_on_requested.sql'],
)
async def test_service_return_places_info_for_ids_from_place_ids_beginnig_for_request_with_empty_cursor(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_places_info,
        mock_eats_place_subscriptions,
        pgsql,
):
    service_response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 2},
    )

    sorted_response = {
        'payload': sorted(
            service_response.json()['payload'], key=lambda x: x['id'],
        ),
        'meta': service_response.json()['meta'],
    }

    expected_response = {
        'payload': [SERVICE_PLACES_INFO[1], SERVICE_PLACES_INFO[2]],
        'meta': {'can_fetch_next': True, 'cursor': 3},
    }

    assert service_response.status_code == 200
    assert sorted_response == expected_response


async def test_service_gives_correct_amount_of_places(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_places_info,
        mock_eats_place_subscriptions,
        pgsql,
):
    number_of_places_received = 0
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 1, 'cursor': 0},
    )
    print(response.json())
    while response.json()['meta']['can_fetch_next']:
        number_of_places_received += len(response.json()['payload'])
        response = await taxi_eats_restapp_places.get(
            '/4.0/restapp-front/places/v1/search',
            headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
            params={'limit': 1, 'cursor': response.json()['meta']['cursor']},
        )
        print(response.json())
    number_of_places_received += len(response.json()['payload'])

    assert number_of_places_received == len(SERVICE_PLACES_INFO)


async def test_service_gives_empty_places_if_core_filtered_all_places(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_places_info,
        mock_eats_place_subscriptions,
        pgsql,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 5, 'cursor': 6},
    )
    expected_response = {'payload': [], 'meta': {'can_fetch_next': False}}

    assert response.json() == expected_response


@pytest.mark.pgsql(
    'eats_restapp_places', files=['insert_switching_on_requested.sql'],
)
async def test_service_gives_all_places(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_places_info,
        mock_eats_place_subscriptions,
        pgsql,
):
    service_response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 10, 'cursor': 0},
    )
    sorted_response = {
        'payload': sorted(
            service_response.json()['payload'], key=lambda x: x['id'],
        ),
        'meta': service_response.json()['meta'],
    }
    expected_response = {
        'payload': [
            SERVICE_PLACES_INFO[1],
            SERVICE_PLACES_INFO[2],
            SERVICE_PLACES_INFO[3],
            SERVICE_PLACES_INFO[4],
        ],
        'meta': {'can_fetch_next': False},
    }

    assert sorted_response == expected_response


async def test_service_respond_400_to_get_places_info_with_invalid_cursor(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_places_info,
        mock_eats_place_subscriptions,
        pgsql,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 3, 'cursor': 7},
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Invalid cursor'}


async def test_service_respond_200_for_partner_with_empty_places_ids(
        taxi_eats_restapp_places, mockserver, pgsql,
):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/list')
    def _mock_authorizer(request):
        assert request.json == {'partner_id': PARTNER_ID}
        return mockserver.make_response(
            status=200, json={'is_success': True, 'place_ids': []},
        )

    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 2, 'cursor': 0},
    )
    expected_response = {'payload': [], 'meta': {'can_fetch_next': False}}

    assert expected_response == response.json()


async def test_service_respond_400_if_authorizer_responded_400(
        taxi_eats_restapp_places, mock_authorizer_400, pgsql,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 2, 'cursor': 0},
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Error'}


async def test_service_respond_500_if_authorizer_responded_500(
        taxi_eats_restapp_places, mock_authorizer_500, pgsql,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 2, 'cursor': 0},
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }


async def test_service_respond_400_if_core_responded_400(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_400,
        mock_eats_place_subscriptions,
        pgsql,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 2, 'cursor': 0},
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'error'}


async def test_service_respond_500_if_core_responded_500(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_500,
        mock_eats_place_subscriptions,
        pgsql,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/search',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
        params={'limit': 2, 'cursor': 0},
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }
