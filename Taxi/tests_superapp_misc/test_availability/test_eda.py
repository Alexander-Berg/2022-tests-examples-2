import pytest

from tests_superapp_misc.test_availability import consts
from tests_superapp_misc.test_availability import helpers


@pytest.mark.parametrize(
    [
        'catalog_times_called',
        'storage_times_called',
        'eats_available',
        'grocery_available',
    ],
    [
        pytest.param(1, 1, True, True, id='catalog'),
        pytest.param(
            0,
            1,
            False,
            True,
            marks=consts.USE_CATLOG_STORAGE,
            id='catalog + eats-catalog-storage',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
async def test_services_from_eda(
        taxi_superapp_misc,
        mockserver,
        catalog_times_called,
        storage_times_called,
        eats_available,
        grocery_available,
):
    @mockserver.json_handler(consts.EDA_STORAGE_AVAILBILITY)
    def eats_storage_availability(_):
        return {
            'payload': {
                'services': [
                    {'type': 'eats', 'isAvailable': False, 'isExist': True},
                    {'type': 'grocery', 'isAvailable': True, 'isExist': True},
                ],
            },
        }

    @mockserver.json_handler('/eda-catalog/v1/availability')
    def catalog_availability(_):
        return {
            'payload': {
                'services': [
                    {'type': 'eats', 'isAvailable': True, 'isExist': True},
                    {'type': 'grocery', 'isAvailable': True, 'isExist': True},
                ],
            },
        }

    payload = helpers.build_payload(send_services=False)

    response = await taxi_superapp_misc.post(consts.URL, payload)
    assert response.status_code == 200
    assert catalog_availability.times_called == catalog_times_called
    assert eats_storage_availability.times_called == storage_times_called
    assert response.json() == helpers.ok_response(
        eats_available=eats_available, grocery_available=grocery_available,
    )


@consts.USE_CATLOG_STORAGE
@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
@pytest.mark.parametrize(
    'response_storage, response_catalog, eats_available, grocery_available',
    [
        pytest.param(None, None, False, False, id='both failed'),
        pytest.param(
            {
                'payload': {
                    'services': [
                        {'type': 'eats', 'isAvailable': True, 'isExist': True},
                        {
                            'type': 'grocery',
                            'isAvailable': False,
                            'isExist': True,
                        },
                    ],
                },
            },
            None,
            True,
            False,
            id='catalog failed',
        ),
        pytest.param(None, None, False, False, id='storage failed'),
    ],
)
async def test_services_from_eda_fallback(
        taxi_superapp_misc,
        mockserver,
        response_storage,
        response_catalog,
        eats_available,
        grocery_available,
):
    @mockserver.json_handler(consts.EDA_STORAGE_AVAILBILITY)
    def eats_storage_availability(_):
        if response_storage is None:
            return mockserver.make_response(status=500)
        return response_storage

    @mockserver.json_handler('/eda-catalog/v1/availability')
    def eda_availability(_):
        if response_catalog is None:
            return mockserver.make_response(status=500)
        return response_catalog

    payload = helpers.build_payload(send_services=False)

    response = await taxi_superapp_misc.post(consts.URL, payload)
    assert response.status_code == 200

    assert eda_availability.times_called == 0
    assert eats_storage_availability.times_called == 1

    assert response.json() == helpers.ok_response(
        eats_available=eats_available, grocery_available=grocery_available,
    )


@consts.USE_CATLOG_STORAGE
@pytest.mark.parametrize('screen_type', ['main', 'on_order'])
@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
async def test_eda_point_from_services_positions(
        taxi_superapp_misc, mockserver, screen_type,
):
    payload = helpers.build_payload(
        send_services=False, position=consts.DEFAULT_POSITION,
    )
    payload['state'] = {
        'fields': [{'type': 'b', 'position': [1, 1]}],
        'known_orders': ['taxi:xxx'],
        'screen_type': screen_type,
    }

    @mockserver.json_handler(consts.EDA_STORAGE_AVAILBILITY)
    def _eda_availability(request):
        # pylint: disable=protected-access
        query_dict = {k: float(v) for k, v in request._request.query.items()}
        expected_position = (
            {
                'longitude': consts.DEFAULT_POSITION[0],
                'latitude': consts.DEFAULT_POSITION[1],
            }
            if screen_type == 'main'
            else {'longitude': 1.0, 'latitude': 1.0}
        )
        assert query_dict == expected_position
        return {
            'payload': {
                'services': [
                    {'type': 'eats', 'isAvailable': True, 'isExist': True},
                    {'type': 'grocery', 'isAvailable': True, 'isExist': True},
                ],
            },
        }

    response = await taxi_superapp_misc.post(consts.URL, payload)
    assert response.status_code == 200
    assert response.json() == helpers.ok_response(
        eats_available=screen_type == 'main',
        grocery_available=screen_type == 'main',
    )


@consts.USE_CATLOG_STORAGE
@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
@pytest.mark.parametrize(
    'exp_multipoint, expected',
    [
        pytest.param(
            True, True, id='Waypoints only, exp: true, expected: true',
        ),
        pytest.param(
            False, False, id='Waypoints only, exp: false, expected: false',
        ),
    ],
)
async def test_services_from_eda_multipoint(
        taxi_superapp_misc, mockserver, experiments3, exp_multipoint, expected,
):
    @mockserver.json_handler(consts.EDA_STORAGE_AVAILBILITY)
    def _eda_availability_waypoints_only(request):
        available = helpers.is_equal_position(
            request.query, consts.ADDITIONAL_POSITION,
        )
        return {
            'payload': {
                'services': [
                    {
                        'type': 'eats',
                        'isAvailable': available,
                        'isExist': True,
                    },
                    {
                        'type': 'grocery',
                        'isAvailable': available,
                        'isExist': True,
                    },
                ],
            },
        }

    helpers.add_exp_multipoint(experiments3, exp_multipoint)

    payload = helpers.build_payload(
        send_services=False, state=helpers.build_state(),
    )

    response = await taxi_superapp_misc.post(consts.URL, payload)
    assert response.status_code == 200
    assert _eda_availability_waypoints_only.has_calls
    assert response.json() == helpers.ok_response(
        eats_available=expected, grocery_available=expected,
    )


@consts.USE_CATLOG_STORAGE
@pytest.mark.parametrize(
    'position, expected_availability_called, expected_response_part',
    [
        pytest.param(
            [36.06, 57.5], True, {}, id='No Eda services exist in this region',
        ),
        pytest.param(
            [36.06, 55.5],
            False,
            {'region_id': 1},
            id='Bypass existing services when deathflag is set',
        ),
    ],
)
@pytest.mark.config(EDA_CATALOG_POLYGONS_CACHE_ENABLED=True)
@pytest.mark.experiments3(filename='exp3_superapp_eats_deathflag.json')
async def test_bypass_eda(
        taxi_superapp_misc,
        mockserver,
        load_json,
        position,
        expected_availability_called,
        expected_response_part,
):
    @mockserver.json_handler(consts.EDA_STORAGE_AVAILBILITY)
    def _eda_availability(request):
        return {
            'payload': {
                'services': [
                    {'type': 'eats', 'isAvailable': True, 'isExist': True},
                    {'type': 'grocery', 'isAvailable': False, 'isExist': True},
                ],
            },
        }

    @mockserver.json_handler('/eats-core/v1/export/regions')
    def _eats_regions(request):
        return load_json('eats_regions_response.json')

    catalog_polygons = load_json('eda_catalog_polygons_response.json')

    @mockserver.json_handler('/eda-catalog/v1/catalog-polygons')
    def _eda_polygons(request):
        region_id = request.query.get('eatsRegionId')
        return catalog_polygons[region_id]

    payload = helpers.build_payload(send_services=False, position=position)

    response = await taxi_superapp_misc.post(consts.URL, payload)
    assert response.status_code == 200
    assert _eda_availability.has_calls == expected_availability_called
    expected_response = {
        'modes': [
            {
                'mode': 'eats',
                'parameters': {
                    'available': False,
                    'deathflag': True,
                    'product_tag': 'eats',
                },
            },
            {
                'mode': 'grocery',
                'parameters': {
                    'available': False,
                    # no 'deathflag' coz we didn't set it in experiment
                    'product_tag': 'grocery',
                },
            },
        ],
        'products': [
            {'service': 'eats', 'tag': 'eats', 'title': 'Eats'},
            {'service': 'grocery', 'tag': 'grocery', 'title': 'Grocery'},
        ],
        'typed_experiments': {'items': [], 'version': -1},
    }
    expected_response.update(expected_response_part)
    assert response.json() == expected_response
