import pytest

from tests_superapp_misc.test_availability import consts
from tests_superapp_misc.test_availability import helpers


def setup_gdepots(mockserver, depots, zones):
    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/depots')
    def _handle_depots(_request):
        return depots

    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/zones')
    def _handle_zones(_request):
        return zones


@consts.USE_CATLOG_STORAGE
@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
@pytest.mark.experiments3(
    filename=(
        'exp3_superapp_recieve_grocery_availability_from_overlord_catalog.json'
    ),
)
@pytest.mark.experiments3(
    name='grocery_availability_flow',
    consumers=['superapp-misc/grocery_availability'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'grocery_depots_client_enabled': True},
        },
    ],
    is_config=True,
)
@pytest.mark.parametrize(
    'grocery_api_available, exp_multipoint, waypoint_only, expected, depots',
    [
        pytest.param(
            True,
            None,
            False,
            True,
            {
                'depots': [
                    {
                        'address': 'Доширбург, Яичное лапшассе, 39',
                        'allow_parcels': True,
                        'assortment_id': (
                            'a12bc48f406141f49b851cf71c3cfb22000200010001'
                        ),
                        'company_id': (
                            'c643bfdbcedf4729bd58f3ba16fafeed000300010000'
                        ),
                        'company_type': 'yandex',
                        'country_iso2': 'RU',
                        'country_iso3': 'RUS',
                        'currency': 'RUS',
                        'depot_id': (
                            'ddb8a6fbcee34b38b5281d8ea6ef749a000100010011'
                        ),
                        'directions': '',
                        'email': '',
                        'hidden': False,
                        'legacy_depot_id': '112',
                        'location': {
                            'lat': 55.733862999999999,
                            'lon': 37.590533000000001,
                        },
                        'name': 'test_lavka_2',
                        'phone_number': '+78007700460',
                        'price_list_id': (
                            'eda86ab6cb45489f9d44137a971f64b9000200010000'
                        ),
                        'region_id': 213,
                        'root_category_id': (
                            '393b118f1cd54d3583fcd752a554cbdf000300010000'
                        ),
                        'short_address': 'Мир Дошиков',
                        'status': 'active',
                        'telegram': '',
                        'timezone': 'Europe/Moscow',
                    },
                ],
                'errors': [],
            },
            id='overlord-catalog is available',
        ),
        pytest.param(
            True,
            True,
            True,
            True,
            {
                'depots': [
                    {
                        'address': 'Доширбург, Яичное лапшассе, 39',
                        'allow_parcels': True,
                        'assortment_id': (
                            'a12bc48f406141f49b851cf71c3cfb22000200010001'
                        ),
                        'company_id': (
                            'c643bfdbcedf4729bd58f3ba16fafeed000300010000'
                        ),
                        'company_type': 'yandex',
                        'country_iso2': 'RU',
                        'country_iso3': 'RUS',
                        'currency': 'RUS',
                        'depot_id': (
                            'ddb8a6fbcee34b38b5281d8ea6ef749a000100010011'
                        ),
                        'directions': '',
                        'email': '',
                        'hidden': False,
                        'legacy_depot_id': '112',
                        'location': {
                            'lat': 55.733862999999999,
                            'lon': 37.590533000000001,
                        },
                        'name': 'test_lavka_2',
                        'phone_number': '+78007700460',
                        'price_list_id': (
                            'eda86ab6cb45489f9d44137a971f64b9000200010000'
                        ),
                        'region_id': 213,
                        'root_category_id': (
                            '393b118f1cd54d3583fcd752a554cbdf000300010000'
                        ),
                        'short_address': 'Мир Дошиков',
                        'status': 'active',
                        'telegram': '',
                        'timezone': 'Europe/Moscow',
                    },
                ],
                'errors': [],
            },
            id='overlord-catalog is available, multipoint ON',
        ),
        pytest.param(
            True,
            False,
            True,
            False,
            {'depots': [], 'errors': []},
            id='overlord-catalog is available, multipoint OFF',
        ),
        pytest.param(
            False,
            None,
            False,
            False,
            {'depots': [], 'errors': []},
            id='overlord-catalog is not available',
        ),
    ],
)
async def test_grocery_availability_from_overlord_catalog(
        taxi_superapp_misc,
        mockserver,
        experiments3,
        grocery_api_available,
        exp_multipoint,
        waypoint_only,
        expected,
        depots,
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

    setup_gdepots(
        mockserver,
        depots,
        {
            'zones': [
                {
                    'depot_id': 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010011',
                    'effective_from': '2019-12-01T01:01:01+00:00',
                    'geozone': {
                        'coordinates': [
                            [
                                [
                                    {
                                        'lat': 55.720862999999999,
                                        'lon': 37.190533000000001,
                                    },
                                    {
                                        'lat': 55.734552853773316,
                                        'lon': 37.190533000000001,
                                    },
                                    {
                                        'lat': 55.73770593659091,
                                        'lon': 37.74182090759277,
                                    },
                                    {
                                        'lat': 55.70701735403676,
                                        'lon': 37.94008283615112,
                                    },
                                    {
                                        'lat': 55.720862999999999,
                                        'lon': 37.190533000000001,
                                    },
                                ],
                            ],
                        ],
                        'type': 'MultiPolygon',
                    },
                    'timetable': [
                        {
                            'day_type': 'Everyday',
                            'working_hours': {
                                'from': {'hour': 0, 'minute': 0},
                                'to': {'hour': 0, 'minute': 0},
                            },
                        },
                    ],
                    'zone_id': '09e28de3a73645a5aee40773cbb0f84d000200010001',
                    'zone_status': 'active',
                    'zone_type': 'pedestrian',
                },
            ],
        },
    )

    await taxi_superapp_misc.invalidate_caches()

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/availability',
    )
    def _grocery_availability(request):
        available = not waypoint_only or helpers.is_equal_position(
            request.query, consts.ADDITIONAL_POSITION,
        )
        return (
            mockserver.make_response(
                status=200, json={'exists': True, 'available': available},
            )
            if grocery_api_available
            else mockserver.make_response(status=500)
        )

    if exp_multipoint is not None:
        helpers.add_exp_multipoint(experiments3, exp_multipoint)

    payload = helpers.build_payload(
        send_services=False, state=helpers.build_state(),
    )

    response = await taxi_superapp_misc.post(consts.URL, payload)
    assert response.status_code == 200
    assert _eda_availability.has_calls
    assert response.json() == helpers.ok_response(
        eats_available=True, grocery_available=expected,
    )


@consts.USE_CATLOG_STORAGE
@pytest.mark.experiments3(
    filename=(
        'exp3_superapp_recieve_grocery_availability_from_overlord_catalog.json'
    ),
)
async def test_grocery_availability_with_auth_context(
        taxi_superapp_misc, mockserver, experiments3,
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

    @mockserver.json_handler(
        '/overlord-catalog/internal/v1/catalog/v1/availability',
    )
    def _grocery_availability(request):
        headers = request.headers
        assert headers.get('X-Yandex-UID') == consts.DEFAULT_YANDEX_UID
        assert headers.get('X-YaTaxi-PhoneId') == consts.DEFAULT_PHONE_ID
        assert headers.get('X-YaTaxi-UserId') == consts.DEFAULT_USER_ID

        available = True
        return mockserver.make_response(
            status=200, json={'exists': True, 'available': available},
        )

    payload = helpers.build_payload(
        send_services=False, state=helpers.build_state(),
    )

    response = await taxi_superapp_misc.post(
        consts.URL,
        payload,
        headers={
            'X-Yandex-UID': consts.DEFAULT_YANDEX_UID,
            'X-YaTaxi-PhoneId': consts.DEFAULT_PHONE_ID,
            'X-YaTaxi-UserId': consts.DEFAULT_USER_ID,
        },
    )
    assert response.status_code == 200
