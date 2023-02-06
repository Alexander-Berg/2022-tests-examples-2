# flake8: noqa
# pylint: disable=redefined-outer-name

import pytest


PARTNER_ID = 1

CORE_PLACES_INFO = [
    {
        'id': 1,
        'name': 'name1',
        'available': True,
        'currency': {'code': 'code1', 'sign': 'sign1', 'decimal_places': 1},
        'country_code': 'country_code1',
        'address': {
            'country': 'country1',
            'city': 'city1',
            'street': 'street1',
            'building': 'building1',
            'full': 'country1 city1 street1 building1',
        },
        'region': {'id': 58, 'slug': 'PENZA'},
        'show_shipping_time': True,
        'integration_type': 'native',
        'slug': 'slug1',
    },
    {
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
    },
    {
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
    },
    {
        'id': 6,
        'name': 'name4',
        'available': False,
        'currency': {'code': 'code4', 'sign': 'sign4', 'decimal_places': 3},
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
    },
]

SERVICE_PLACES_INFO = [
    {
        'id': 1,
        'name': 'name1',
        'is_available': True,
        'is_switching_on_requested': False,
        'address': 'street1, building1, city1, country1',
        'integration_type': 'native',
    },
    {
        'id': 3,
        'name': 'name2',
        'is_available': True,
        'is_switching_on_requested': False,
        'address': 'street2, building2, city2, country2',
        'integration_type': 'native',
    },
    {
        'id': 5,
        'name': 'name3',
        'is_available': False,
        'is_switching_on_requested': True,
        'address': 'street3, building3, city3, country3',
        'integration_type': 'native',
        'disable_details': {
            'disable_at': '2020-07-28T09:07:12+00:00',
            'available_at': '2020-07-28T09:07:12+00:00',
            'status': 1,
            'reason': 47,
        },
    },
    {
        'id': 6,
        'name': 'name4',
        'is_available': False,
        'is_switching_on_requested': False,
        'address': 'street4, building4, city4, country4',
        'integration_type': 'native',
        'disable_details': {
            'disable_at': '2020-07-28T09:07:12+00:00',
            'available_at': '2020-07-28T09:07:12+00:00',
            'status': 1,
            'reason': 47,
        },
    },
]


PLACE_IDS = [1, 2, 3, 4, 5, 6, 7, 9]


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
        if request.json['place_ids'] == PLACE_IDS:
            return mockserver.make_response(
                status=200, json={'payload': CORE_PLACES_INFO},
            )
        return mockserver.make_response(
            status=404, json={'code': '', 'message': ''},
        )


@pytest.mark.pgsql(
    'eats_restapp_places', files=['insert_switching_on_requested.sql'],
)
async def test_service_respond_successfully_to_get_short_places_info(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_places_info,
        pgsql,
):
    service_response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/suggest',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    sorted_response = {
        'payload': sorted(
            service_response.json()['payload'], key=lambda x: x['id'],
        ),
        'meta': service_response.json()['meta'],
    }
    print(sorted_response)
    expected_response = {'payload': SERVICE_PLACES_INFO, 'meta': {'count': 4}}

    assert service_response.status_code == 200
    assert sorted_response == expected_response


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
        '/4.0/restapp-front/places/v1/suggest',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )
    expected_response = {'payload': [], 'meta': {'count': 0}}

    assert expected_response == response.json()


async def test_service_respond_400_if_authorizer_responded_400(
        taxi_eats_restapp_places, mock_authorizer_400, pgsql,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/suggest',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'Error'}


async def test_service_respond_500_if_authorizer_responded_500(
        taxi_eats_restapp_places, mock_authorizer_500, pgsql,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/suggest',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
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
        pgsql,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/suggest',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'error'}


async def test_service_respond_500_if_core_responded_500(
        taxi_eats_restapp_places,
        mock_authorizer_places_list,
        mock_eats_core_500,
        pgsql,
):
    response = await taxi_eats_restapp_places.get(
        '/4.0/restapp-front/places/v1/suggest',
        headers={'X-YaEda-PartnerId': str(PARTNER_ID)},
    )

    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }
