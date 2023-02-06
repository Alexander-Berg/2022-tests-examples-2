import pytest

from tests_fleet_orders_misc import common


ENDPOINT_ZONES = 'fleet/fleet-orders-misc/v1/tariffs/zones'
ENDPOINT_CLASSES = 'fleet/fleet-orders-misc/v1/tariffs/classes'
ENDPOINT_REQUIREMENTS = 'fleet/fleet-orders-misc/v1/tariffs/requirements'


@pytest.fixture(name='mock_tariffs')
def _mock_tariffs(mockserver, load_json):
    all_zones = load_json('tariff_zones.json')
    all_tariffs = load_json('tariffs.json')

    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _mock_tariff_zones(request, *args, **kwargs):
        request_for_cities = request.query.get('city_ids')
        assert request_for_cities

        cities = request_for_cities.split(',')
        zones = [zone for zone in all_zones if zone['city_id'] in cities]
        return mockserver.make_response(json={'zones': zones})

    @mockserver.json_handler('/taxi-tariffs/v1/tariff/current')
    def _current_tariff(request):
        assert request.query['zone']
        tariffs = [
            tariff
            for tariff in all_tariffs
            if tariff['home_zone'] == request.query['zone']
        ]
        return tariffs[0]


@pytest.fixture(name='mock_dispatch_requirements')
def _mock_dispatch_requirements(mockserver):
    @mockserver.json_handler(
        '/fleet-parks/internal/v1/dispatch-requirements/retrieve-by-park',
    )
    def _mock(request):
        assert request.json['park_id'] in [
            'extra_super_park_id1',
            'extra_super_park_id2',
        ]

        if request.json['park_id'] == 'extra_super_park_id1':
            return mockserver.make_response(
                json={
                    'code': 'NOT_SAAS_PARK',
                    'message': (
                        'Not a saas park, park_id: extra_super_park_id1'
                    ),
                },
                status=400,
            )

        return {
            'park_id': 'extra_super_park_id2',
            'label_id': 'label_id',
            'dispatch_requirement': 'only_source_park',
        }

    return _mock


@pytest.fixture(name='mock_zoneinfo')
def _mock_zoneinfo(mockserver, load_json):
    all_responses = load_json('zoneinfo_responses.json')
    all_responses_no_icons = load_json('zoneinfo_responses_no_icons.json')

    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _mock(request, *args, **kwargs):
        zone_name = request.json.pop('zone_name')
        if 'size_hint' in request.json:
            assert request.json['size_hint'] == 9999
        if 'skin_version' in request.json:
            assert request.json['skin_version'] == 7
        assert request.headers['Accept-Language'] == 'ru'
        if zone_name not in all_responses:
            return mockserver.make_response(status=404)
        if 'size_hint' in request.json:
            return all_responses[zone_name]
        return all_responses_no_icons[zone_name]

    return _mock


@pytest.mark.parametrize(
    'park_id, service_response',
    [
        (
            'extra_super_park_id',
            {'zones': [{'zone_id': 'corleone', 'localized_name': 'corleone'}]},
        ),
        (
            'extra_super_park_id2',
            {
                'zones': [
                    {'zone_id': 'berlin', 'localized_name': 'berlin'},
                    {'zone_id': 'berlin1', 'localized_name': 'berlin1'},
                ],
            },
        ),
    ],
)
async def test_zones_ok(
        taxi_fleet_orders_misc,
        mock_fleet_parks_list,
        mock_tariffs,
        park_id,
        service_response,
):
    headers = common.YA_USER_HEADERS
    headers['X-Park-ID'] = park_id
    headers['Accept-Language'] = 'en-us'

    response = await taxi_fleet_orders_misc.get(
        ENDPOINT_ZONES, headers=headers, params={},
    )
    assert response.status_code == 200
    assert response.json() == service_response


@pytest.mark.parametrize(
    'park_id, params, service_response',
    [
        (
            'extra_super_park_id1',
            {'zone_id': 'barnaul'},
            {
                'classes': [
                    {
                        'tariff_class_id': 'comfortplus',
                        'localized_name': 'Комфорт-Плюс',
                        'currency_info': {'currency_code': 'RUB'},
                        'distance_included': 0.0,
                        'distance_price': 0.0,
                        'minimal': 213.0,
                        'suburb_distance_included': 2.0,
                        'suburb_distance_price': 24.0,
                        'suburb_time_included': 3.0,
                        'suburb_time_price': 9.0,
                        'time_from': '00:00',
                        'time_included': 0.0,
                        'time_price': 0.0,
                        'time_to': '23:59',
                        'waiting_price': 5.0,
                        'icon': {
                            'url': (
                                'https://tc.tst.mobile.yandex.net/static/test'
                                '-images/598/cf0daca24f2b4353aa99071f61696913'
                            ),
                        },
                    },
                    {
                        'tariff_class_id': 'econom',
                        'localized_name': 'Эконом',
                        'currency_info': {'currency_code': 'RUB'},
                        'distance_included': 0.0,
                        'distance_price': 0.0,
                        'minimal': 10.0,
                        'minimal_price': 10.0,
                        'suburb_distance_included': 0.0,
                        'suburb_distance_price': 32.0,
                        'suburb_time_included': 3.0,
                        'suburb_time_price': 9.0,
                        'time_from': '00:00',
                        'time_included': 0.0,
                        'time_price': 0.0,
                        'time_to': '23:00',
                        'waiting_included': 10.0,
                        'waiting_price': 10.0,
                        'icon': {
                            'url': (
                                'https://tc.tst.mobile.yandex.net/static/test'
                                '-images/598/cf0daca24f2b4353aa99071f61696913'
                            ),
                        },
                    },
                    {
                        'tariff_class_id': 'econom',
                        'localized_name': 'Эконом',
                        'currency_info': {'currency_code': 'RUB'},
                        'distance_included': 0.0,
                        'distance_price': 0.0,
                        'minimal': 31.0,
                        'suburb_distance_included': 2.0,
                        'suburb_distance_price': 24.0,
                        'suburb_time_included': 3.0,
                        'suburb_time_price': 9.0,
                        'time_from': '23:01',
                        'time_included': 0.0,
                        'time_price': 0.0,
                        'time_to': '23:59',
                        'waiting_price': 5.0,
                        'icon': {
                            'url': (
                                'https://tc.tst.mobile.yandex.net/static/test'
                                '-images/598/cf0daca24f2b4353aa99071f61696913'
                            ),
                        },
                    },
                ],
            },
        ),
        (
            'extra_super_park_id2',
            {'zone_id': 'himki'},
            {
                'classes': [
                    {
                        'tariff_class_id': 'econom',
                        'localized_name': 'Эконом',
                        'currency_info': {'currency_code': 'RUB'},
                        'distance_included': 2.0,
                        'distance_price': 6.0,
                        'minimal': 99.0,
                        'suburb_distance_included': 0.0,
                        'suburb_distance_price': 16.0,
                        'suburb_time_included': 3.0,
                        'suburb_time_price': 6.0,
                        'time_from': '00:00',
                        'time_included': 3.0,
                        'time_price': 6.0,
                        'time_to': '23:59',
                        'waiting_included': 2.0,
                        'waiting_price': 6.0,
                        'icon': {
                            'url': (
                                'https://tc.tst.mobile.yandex.net/static/test'
                                '-images/598/cf0daca24f2b4353aa99071f61696913'
                            ),
                        },
                    },
                ],
            },
        ),
        (
            'extra_super_park_id2',
            {'zone_id': 'muscat'},
            {
                'classes': [
                    {
                        'tariff_class_id': 'econom',
                        'localized_name': 'Эконом',
                        'currency_info': {'currency_code': 'OMR'},
                        'distance_included': 3.0,
                        'distance_price': 4.0,
                        'minimal': 10.0,
                        'suburb_distance_included': 2.0,
                        'suburb_distance_price': 7.0,
                        'suburb_time_included': 4.0,
                        'suburb_time_price': 8.0,
                        'time_from': '00:00',
                        'time_included': 5.0,
                        'time_price': 6.0,
                        'time_to': '23:59',
                        'waiting_included': 0.0,
                        'waiting_price': 2.0,
                        'icon': {
                            'url': (
                                'https://tc.tst.mobile.yandex.net/static/test'
                                '-images/598/cf0daca24f2b4353aa99071f61696913'
                            ),
                        },
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(
    FLEET_SAAS_ALLOWED_TARIFF_CLASSES=['econom', 'business', 'comfortplus'],
)
async def test_tariff(
        taxi_fleet_orders_misc,
        mock_fleet_parks_list,
        mock_dispatch_requirements,
        mock_tariffs,
        mock_zoneinfo,
        park_id,
        params,
        service_response,
):
    headers = {
        **common.YA_USER_HEADERS,
        'X-Park-Id': park_id,
        'Accept-Language': 'ru',
    }

    response = await taxi_fleet_orders_misc.get(
        ENDPOINT_CLASSES, headers=headers, params=params,
    )

    assert response.status_code == 200
    assert response.json() == service_response


async def test_429(
        mockserver,
        taxi_fleet_orders_misc,
        mock_fleet_parks_list,
        mock_dispatch_requirements,
        mock_tariffs,
):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _mock(request, *args, **kwargs):
        return mockserver.make_response(json={}, status=429)

    headers = {
        **common.YA_USER_HEADERS,
        'X-Park-Id': 'extra_super_park_id2',
        'Accept-Language': 'ru',
    }

    response = await taxi_fleet_orders_misc.get(
        ENDPOINT_CLASSES, headers=headers, params={'zone_id': 'muscat'},
    )
    assert response.status_code == 429


async def test_no_intapi_zoneinfo(
        mockserver,
        taxi_fleet_orders_misc,
        mock_fleet_parks_list,
        mock_dispatch_requirements,
        mock_tariffs,
):
    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _mock(request, *args, **kwargs):
        return mockserver.make_response(json={}, status=404)

    headers = {
        **common.YA_USER_HEADERS,
        'X-Park-Id': 'extra_super_park_id2',
        'Accept-Language': 'ru',
    }

    response = await taxi_fleet_orders_misc.get(
        ENDPOINT_CLASSES, headers=headers, params={'zone_id': 'muscat'},
    )
    assert response.status_code == 200
    assert response.json() == {'classes': []}


@pytest.mark.parametrize(
    'zone_id, tariff_class_id, service_response_code, service_response',
    [
        ('himki', 'econom', 200, {'requirements': []}),
        (
            'himki',
            'business',
            200,
            {
                'requirements': [
                    {
                        'id': 'medical_transport',
                        'name': 'Medical transport',
                        'type': 'boolean',
                    },
                    {
                        'id': 'meeting_arriving',
                        'name': 'Airport pickup service',
                        'type': 'text',
                    },
                ],
            },
        ),
        (
            'himki',
            'some_class_id',
            400,
            {
                'code': 'NO_SUCH_TARIFF',
                'message': 'Requsted tarrif not found in requested zone',
            },
        ),
        (
            'himki2',
            'econom',
            400,
            {'code': 'NO_SUCH_ZONE', 'message': 'No tarrifs found for zone'},
        ),
    ],
)
async def test_tariff_requirements(
        taxi_fleet_orders_misc,
        mock_dispatch_requirements,
        mock_zoneinfo,
        zone_id,
        tariff_class_id,
        service_response_code,
        service_response,
):
    headers = {
        **common.YA_USER_HEADERS,
        'X-Park-Id': 'extra_super_park_id2',
        'Accept-Language': 'ru',
    }

    response = await taxi_fleet_orders_misc.get(
        ENDPOINT_REQUIREMENTS,
        headers=headers,
        params={'zone_id': zone_id, 'tariff_class_id': tariff_class_id},
    )

    assert response.status_code == service_response_code
    assert response.json() == service_response
