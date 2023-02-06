# pylint: disable=too-many-lines
import copy
import json

import pytest

URL = '/4.0/persuggest/v1/finalsuggest'

AUTHORIZED_HEADERS = {
    'X-YaTaxi-UserId': '12345678901234567890123456789012',
    'X-YaTaxi-PhoneId': '123456789012345678901234',
    'X-Yandex-UID': '400000000',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Request-Application': 'app_name=android',
    'X-Request-Language': 'he',
}


def all_common_mocks(mockserver, load_json, yamaps):
    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_zones(request):
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('geosearch.json'))

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_graph(request):
        return {
            'adjusted': [
                {'longitude': 34.7, 'latitude': 32.1, 'geo_distance': 100},
            ],
        }


@pytest.mark.geoareas(filename='geoareas_tel_aviv.json')
@pytest.mark.tariffs(filename='tariffs_tel_aviv.json')
@pytest.mark.tariff_settings(
    filename='tariff_settings_telaviv.json',
    visibility_overrides={
        'tel_aviv': {
            'econom': {'visible_by_default': False},
            'uberx': {'visible_by_default': True},
        },
    },
)
async def test_finalsuggest_special_zones(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    request_to_check = {
        'type': 'a',
        'geopoint': [0, 0],
        'filter': {'excluded_zone_types': [], 'persistent_only': False},
    }

    @mockserver.json_handler('/special-zones/special-zones/v1/zones')
    def _mock_special_zones(request):
        assert json.loads(request.get_data()) == request_to_check
        return load_json('zones_empty_response.json')

    @mockserver.json_handler('/umlaas-geo/umlaas-geo/v1/finalsuggest')
    def _mock_umlaas_geo(request):
        return {}

    yamaps.add_fmt_geo_object(load_json('geosearch.json'))

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_graph(request):
        return {
            'adjusted': [
                {'longitude': 34.7, 'latitude': 32.1, 'geo_distance': 100},
            ],
        }

    request = {
        'action': 'pin_drop',
        'position': [0, 0],
        'state': {
            'accuracy': 120,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    taxi_services = response.json()['services']['taxi']
    assert not taxi_services['available']
    message = taxi_services['unavailability_reason']['message']
    assert message == 'This region is not supported yet'


@pytest.mark.geoareas(filename='geoareas_tel_aviv.json')
@pytest.mark.tariffs(filename='tariffs_tel_aviv.json')
@pytest.mark.tariff_settings(
    filename='tariff_settings_telaviv.json',
    visibility_overrides={
        'tel_aviv': {
            'econom': {'visible_by_default': False},
            'uberx': {'visible_by_default': True},
        },
    },
)
async def test_finalsuggest_nz_no_zone(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    all_common_mocks(mockserver, load_json, yamaps)
    request = {
        'action': 'pin_drop',
        'position': [0, 0],
        'state': {
            'accuracy': 120,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    taxi_services = response.json()['services']['taxi']
    assert not taxi_services['available']
    message = taxi_services['unavailability_reason']['message']
    assert message == 'This region is not supported yet'


@pytest.mark.config(
    ZONES_COMING_SOON_WITH_URLS={
        'tel_aviv': {
            'message': 'nearestzone.tel_aviv_coming_soon_text',
            'url': {
                '__default': 'https://yango.yandex.com/action/isr',
                'ru': 'https://yango.yandex.com/action/isr-ru',
                'en': 'https://yango.yandex.com/action/isr-en',
                'he': 'https://yango.yandex.com/action/isr-he',
            },
            'url_text': 'nearestzone.tel_aviv_coming_soon_url_text',
        },
    },
    LOCALES_SUPPORTED=['ru', 'en', 'he', 'uk'],
)
@pytest.mark.translations(
    client_messages={
        'nearestzone.tel_aviv_coming_soon_text': {
            'en': 'Tel-aviv is coming soon!!! en',
            'he': 'Tel-aviv is coming soon!!! he',
        },
        'nearestzone.tel_aviv_coming_soon_url_text': {
            'en': 'See more... en',
            'he': 'See more... he',
        },
    },
)
@pytest.mark.geoareas(filename='geoareas_tel_aviv.json')
@pytest.mark.parametrize(
    'accept_language,excepted_answer',
    [
        ('he', 'Tel-aviv is coming soon!!! he'),
        ('en', 'Tel-aviv is coming soon!!! en'),
    ],
)
@pytest.mark.tariff_settings(
    filename='tariff_settings_telaviv.json',
    visibility_overrides={
        'tel_aviv': {'econom': {'visible_by_default': False}},
    },
)
async def test_finalsuggest_nz_coming_soon_zone(
        taxi_persuggest,
        accept_language,
        excepted_answer,
        mockserver,
        load_json,
        yamaps,
):
    all_common_mocks(mockserver, load_json, yamaps)
    request = {
        'action': 'pin_drop',
        'position': [34.7, 32.1],
        'state': {
            'accuracy': -120,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': True,
        'type': 'a',
    }
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-Request-Language'] = accept_language
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    taxi_services = response.json()['services']['taxi']
    assert not taxi_services['available']
    message = taxi_services['unavailability_reason']['message']
    assert message == excepted_answer


@pytest.mark.tariff_settings(filename='tariff_settings_telaviv.json')
@pytest.mark.geoareas(filename='geoareas_tel_aviv.json')
@pytest.mark.tariffs(filename='tariffs_tel_aviv.json')
async def test_finalsuggest_nz_nearest_zone(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    all_common_mocks(mockserver, load_json, yamaps)
    request = {
        'action': 'pin_drop',
        'position': [0, 0],
        'state': {
            'accuracy': 120,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': False,
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    taxi_services = response.json()['services']['taxi']
    assert taxi_services['nearest_zone'] == 'tel_aviv'


@pytest.mark.parametrize(
    'position,application,expected_zone',
    [
        ([34.7, 32.1], 'app_name=uber_android,app_brand=yauber', 'tel_aviv'),
        (
            [0.5, 0.5],
            'app_name=yango_android,app_brand=yango',
            'test_business',
        ),
    ],
)
@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom'],
        'yauber': ['econom'],
        'yango': ['business'],
    },
)
@pytest.mark.geoareas(filename='geoareas_tel_aviv.json')
@pytest.mark.geoareas(filename='geoareas_tel_aviv_test_business.json')
@pytest.mark.tariffs(filename='tariffs_tel_aviv.json')
@pytest.mark.tariff_settings(filename='tariff_settings_telaviv.json')
async def test_finalsuggest_nz_brand(
        taxi_persuggest,
        mockserver,
        load_json,
        yamaps,
        position,
        application,
        expected_zone,
):
    all_common_mocks(mockserver, load_json, yamaps)

    @mockserver.json_handler('/yaga-adjust/adjust/position')
    def _mock_graph(request):
        return {
            'adjusted': [
                {
                    'longitude': position[0],
                    'latitude': position[1],
                    'geo_distance': 100,
                },
            ],
        }

    request = {
        'action': 'pin_drop',
        'position': [0, 0],
        'state': {
            'accuracy': 120,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': False,
        'type': 'a',
    }
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-Request-Application'] = application
    response = await taxi_persuggest.post(URL, request, headers=headers)
    taxi_services = response.json()['services']['taxi']
    assert taxi_services['nearest_zone'] == expected_zone


@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': ['econom'],
        'yauber': ['econom'],
        'yango': ['comfortplus'],
    },
)
@pytest.mark.tariff_settings(filename='tariff_settings_telaviv.json')
@pytest.mark.geoareas(filename='geoareas_tel_aviv.json')
@pytest.mark.tariffs(filename='tariffs_tel_aviv.json')
async def test_finalsuggest_nz_brand_404(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    all_common_mocks(mockserver, load_json, yamaps)
    request = {
        'action': 'pin_drop',
        'position': [0, 0],
        'state': {
            'accuracy': 120,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': False,
        'type': 'a',
    }
    headers = copy.deepcopy(AUTHORIZED_HEADERS)
    headers['X-Request-Application'] = 'app_name=yango_android,app_brand=yango'
    response = await taxi_persuggest.post(URL, request, headers=headers)
    assert response.status_code == 200
    taxi_services = response.json()['services']['taxi']
    assert not taxi_services['available']


@pytest.mark.tariff_settings(
    filename='tariff_settings_telaviv.json',
    visibility_overrides={
        'tel_aviv': {
            'econom': {
                'visible_by_default': False,
                'show_experiment': 'show_econom_tel_aviv',
            },
        },
    },
)
@pytest.mark.geoareas(filename='geoareas_tel_aviv.json')
@pytest.mark.tariffs(filename='tariffs_tel_aviv.json')
@pytest.mark.experiments3(filename='exp3_tariff_visibility_configs.json')
async def test_finalsuggest_nz_show_exp3(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    all_common_mocks(mockserver, load_json, yamaps)
    request = {
        'action': 'pin_drop',
        'position': [0, 0],
        'state': {
            'accuracy': 120,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': False,
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    taxi_services = response.json()['services']['taxi']
    assert taxi_services['nearest_zone'] == 'tel_aviv'


@pytest.mark.tariff_settings(
    filename='tariff_settings_telaviv.json',
    visibility_overrides={
        'tel_aviv': {
            'econom': {
                'visible_by_default': True,
                'hide_experiment': 'hide_econom_tel_aviv',
            },
        },
    },
)
@pytest.mark.geoareas(filename='geoareas_tel_aviv.json')
@pytest.mark.tariffs(filename='tariffs_tel_aviv.json')
@pytest.mark.experiments3(filename='exp3_tariff_visibility_configs.json')
async def test_finalsuggest_nz_hide_exp3(
        taxi_persuggest, mockserver, load_json, yamaps,
):
    all_common_mocks(mockserver, load_json, yamaps)
    request = {
        'action': 'pin_drop',
        'position': [0, 0],
        'state': {
            'accuracy': 120,
            'bbox': [30, 50, 40, 60],
            'fields': [],
            'location': [0, 0],
        },
        'sticky': False,
        'type': 'a',
    }
    response = await taxi_persuggest.post(
        URL, request, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200
    taxi_services = response.json()['services']['taxi']
    assert not taxi_services['available']
