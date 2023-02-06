import pytest

from tests_fleet_orders_misc import common


ENDPOINT = 'fleet/fleet-orders-misc/v1/tariffs/classes/dictionary'

ZONES = [
    {
        'city_id': 'Berlin',
        'country': 'ger',
        'name': 'berlin',
        'time_zone': 'Europe/Berline',
    },
    {
        'city_id': 'Berlin',
        'country': 'ger',
        'name': 'berlin1',
        'time_zone': 'Europe/Berline',
    },
]


@pytest.fixture(name='mock_tariffs')
def _mock_tariffs(mockserver, load_json):
    @mockserver.json_handler('/taxi-tariffs/v1/tariff_zones')
    def _mock(request, *args, **kwargs):
        assert {**request.query} == {'city_ids': 'Berlin', 'locale': 'ru'}
        return {'zones': ZONES}

    return _mock


@pytest.fixture(name='mock_zoneinfo')
def _mock_zoneinfo(mockserver, load_json):
    all_responses = load_json('zoneinfo_responses.json')

    @mockserver.json_handler('/integration-api/v1/zoneinfo')
    def _mock(request, *args, **kwargs):
        zone_name = request.json.pop('zone_name')
        assert request.json == {}
        assert request.headers['Accept-Language'] == 'ru'
        return all_responses[zone_name]

    return _mock


@pytest.fixture(name='dispatch_requirements')
def _mock_dispatch_requirements(mockserver):
    @mockserver.json_handler(
        '/fleet-parks/internal/v1/dispatch-requirements/retrieve-by-park',
    )
    def _mock(request):
        assert request.json['park_id'] == 'extra_super_park_id2'
        return {
            'park_id': 'extra_super_park_id2',
            'label_id': 'label_id',
            'dispatch_requirement': 'only_source_park',
        }

    return _mock


@pytest.mark.config(
    FLEET_SAAS_ALLOWED_TARIFF_CLASSES=['econom', 'business', 'comfortplus'],
)
async def test_ok(
        taxi_fleet_orders_misc,
        mock_fleet_parks_list,
        dispatch_requirements,
        mock_tariffs,
        mock_zoneinfo,
):
    headers = {
        **common.YA_USER_HEADERS,
        'X-Park-Id': 'extra_super_park_id2',
        'Accept-Language': 'ru',
    }

    response = await taxi_fleet_orders_misc.get(
        ENDPOINT, headers=headers, params={},
    )
    assert response.status_code == 200
    assert response.json() == {
        'tariff_classes': [
            {'localized_name': 'Бизнес', 'tariff_class_id': 'business'},
            {
                'localized_name': 'Комфорт-Плюс',
                'tariff_class_id': 'comfortplus',
            },
            {'localized_name': 'Эконом', 'tariff_class_id': 'econom'},
        ],
    }

    assert mock_zoneinfo.times_called == 2
    zoneinfo_request = mock_zoneinfo.next_call()['request']
    assert (
        zoneinfo_request.headers['User-Agent']
        == 'whitelabel/superweb/label_id'
    )


async def test_park_not_found(taxi_fleet_orders_misc, mock_fleet_parks_list):
    headers = {
        **common.YA_USER_HEADERS,
        'X-Park-Id': 'no_susch_park',
        'Accept-Language': 'ru',
    }

    response = await taxi_fleet_orders_misc.get(
        ENDPOINT, headers=headers, params={},
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'park not found'}


async def test_429(
        mockserver,
        taxi_fleet_orders_misc,
        mock_fleet_parks_list,
        dispatch_requirements,
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
        ENDPOINT, headers=headers, params={},
    )
    assert response.status_code == 429


async def test_404(
        mockserver,
        taxi_fleet_orders_misc,
        mock_fleet_parks_list,
        dispatch_requirements,
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
        ENDPOINT, headers=headers, params={},
    )
    assert response.status_code == 200
    assert response.json() == {'tariff_classes': []}
