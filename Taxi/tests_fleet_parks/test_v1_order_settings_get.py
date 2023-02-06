import pytest

from tests_fleet_parks import utils


ENDPOINT_FLEET = '/fleet/fleet-parks/v1/order-settings'
ENDPOINT_INTERNAL = '/internal/v1/order-settings'

HEADERS = {
    'X-Ya-Service-Ticket': utils.SERVICE_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-UID': '100',
    'X-Ya-User-Ticket': utils.SERVICE_TICKET,
}


@pytest.mark.config(
    FLEET_PARKS_DISPATCH_REQUIREMENT_TYPES={
        'default_type': 'only_source_park',
        'types_list': ['only_source_park', 'source_park_and_all'],
        'is_enabled': True,
    },
)
@pytest.mark.parametrize('endpoint', [ENDPOINT_FLEET, ENDPOINT_INTERNAL])
@pytest.mark.parametrize(
    'park_id, service_response',
    [
        (
            'park_id1',
            {
                'dispatch_requirement': 'only_source_park',
                'is_getting_orders_from_app': False,
                'auto_assign_preorders': False,
            },
        ),
        (
            'park_id2',
            {
                'dispatch_requirement': 'only_source_park',
                'is_getting_orders_from_app': True,
                'auto_assign_preorders': False,
            },
        ),
        (
            'park_id3',
            {
                'dispatch_requirement': 'source_park_and_all',
                'is_getting_orders_from_app': False,
                'auto_assign_preorders': True,
            },
        ),
        (
            'park_id4',
            {
                'dispatch_requirement': 'source_park_and_all',
                'is_getting_orders_from_app': True,
                'auto_assign_preorders': True,
            },
        ),
        (
            'park_id_none_dispatch_requirement1',
            {
                'dispatch_requirement': 'only_source_park',
                'is_getting_orders_from_app': False,
                'auto_assign_preorders': True,
            },
        ),
        (
            'park_id_none_dispatch_requirement2',
            {
                'dispatch_requirement': 'only_source_park',
                'is_getting_orders_from_app': True,
                'auto_assign_preorders': True,
            },
        ),
    ],
)
async def test_ok_dispatch_requirement_enabled(
        taxi_fleet_parks, mongodb, endpoint, park_id, service_response,
):
    headers = HEADERS
    headers['X-Park-ID'] = park_id

    response = await taxi_fleet_parks.get(endpoint, headers=headers)

    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.config(
    FLEET_PARKS_DISPATCH_REQUIREMENT_TYPES={
        'default_type': 'only_source_park',
        'types_list': ['only_source_park', 'source_park_and_all'],
        'is_enabled': False,
    },
)
@pytest.mark.parametrize('endpoint', [ENDPOINT_FLEET, ENDPOINT_INTERNAL])
@pytest.mark.parametrize(
    'park_id, service_response',
    [
        (
            'park_id1',
            {
                'is_getting_orders_from_app': False,
                'auto_assign_preorders': False,
            },
        ),
        (
            'park_id2',
            {
                'is_getting_orders_from_app': True,
                'auto_assign_preorders': False,
            },
        ),
        (
            'park_id_none_dispatch_requirement1',
            {
                'is_getting_orders_from_app': False,
                'auto_assign_preorders': True,
            },
        ),
        (
            'park_id_none_dispatch_requirement2',
            {
                'is_getting_orders_from_app': True,
                'auto_assign_preorders': True,
            },
        ),
    ],
)
async def test_ok_dispatch_requirement_disabled(
        taxi_fleet_parks, mongodb, endpoint, park_id, service_response,
):
    headers = HEADERS
    headers['X-Park-ID'] = park_id

    response = await taxi_fleet_parks.get(endpoint, headers=headers)

    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.parametrize('endpoint', [ENDPOINT_FLEET, ENDPOINT_INTERNAL])
async def test_failed_park_not_found(taxi_fleet_parks, mongodb, endpoint):
    headers = HEADERS
    headers['X-Park-ID'] = 'non_existing_park_id'

    response = await taxi_fleet_parks.get(endpoint, headers=headers)

    assert response.status_code == 404
    assert response.json() == {
        'code': 'PARK_NOT_FOUND',
        'message': 'No park found for park_id non_existing_park_id',
    }


@pytest.mark.parametrize('endpoint', [ENDPOINT_FLEET, ENDPOINT_INTERNAL])
async def test_failed_not_saas_park(taxi_fleet_parks, mongodb, endpoint):
    headers = HEADERS
    headers['X-Park-ID'] = 'park_id_not_saas'

    response = await taxi_fleet_parks.get(endpoint, headers=headers)

    assert response.status_code == 400
    assert response.json() == {
        'code': 'NOT_SAAS_PARK',
        'message': 'Not a saas park, park_id: park_id_not_saas',
    }


@pytest.mark.config(
    FLEET_PARKS_DISPATCH_REQUIREMENT_TYPES={
        'default_type': 'only_source_park',
        'types_list': ['only_source_park', 'source_park_and_all'],
        'is_enabled': True,
    },
)
@pytest.mark.parametrize('endpoint', [ENDPOINT_FLEET, ENDPOINT_INTERNAL])
async def test_failed_incorrect_dispatch_requirement(
        taxi_fleet_parks, mongodb, endpoint,
):
    headers = HEADERS
    headers['X-Park-ID'] = 'park_id_incorrect_dispatch_requirement'

    response = await taxi_fleet_parks.get(endpoint, headers=headers)

    assert response.status_code == 500
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }
