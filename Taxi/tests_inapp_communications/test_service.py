import copy

import pytest

# pylint: disable=import-error,wildcard-import
from inapp_communications_plugins.generated_tests import *  # noqa


SHORTCUTS_HEADERS = {
    'X-Yandex-UID': 'uid_1',
    'X-YaTaxi-PhoneId': 'phone_id_unknown',
    'X-YaTaxi-UserId': 'user_id_1',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app=iphone',
}

SHORTCUTS_REQUEST = {
    'user_context': {
        'pin_position': [-37, -55],
        'show_at': '2020-08-30T12:39:50+03:00',
    },
}

PROMOS_ON_SUMMARY_HEADERS = {
    'X-Request-Application': (
        'app_name=android,app_ver1=1,app_ver2=2,app_ver3=4'
    ),
    'X-Request-Language': 'ru',
    'X-YaTaxi-UserId': 'user_id_1',
    'X-Yandex-UID': 'yauid',
    'X-Ya-User-Ticket': 'user-ticket',
    'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
    'X-YaTaxi-PhoneId': 'phone_id_1',
    'X-AppMetrica-UUID': 'appmetrica_uid',
    'X-AppMetrica-DeviceId': 'device_id',
}

PROMOS_ON_SUMMARY_REQUEST = {
    'summary_state': {
        'offer_id': 'some_offer_id',
        'tariff_classes': ['econom', 'comfort', 'vip', 'ultima'],
    },
    'state': {
        'location': [37.211375, 55.477065],
        'accuracy': 12,
        'bbox': [37.615, 55.753, 37.619, 55.758],
        'known_orders': [
            'taxi:taxi_order_id:revision',
            'eats:eats_order_id',
            'grocery:grocery_order_id',
        ],
        'fields': [
            {
                'type': 'a',
                'position': [37.211375, 55.477065],
                'uri': 'uri',
                'entrance': '6',
            },
        ],
        'nz': 'moscow',
    },
    'client_info': {
        'supported_features': [
            {'type': 'promoblock', 'widgets': ['arrow_button']},
        ],
        'mdash_width': 20.0,
        'ndash_width': 9.0,
    },
    'media_size_info': {
        'screen_height': 1920,
        'screen_width': 1080,
        'scale': 2.5,
    },
}

COMMUNICATIONS_REQUEST = {'size_hint': 320}

COMMUNICATIONS_HEADERS = {
    'X-Yandex-UID': '1234567890',
    'X-YaTaxi-UserId': 'test_user_id',
    'X-YaTaxi-PhoneId': 'test_phone_id',
    'User-Agent': (
        'yandex-taxi/3.107.0.dev_sergu_b18dbfd* Android/6.0.1 (LGE; Nexus 5)'
    ),
    'X-Request-Application': (
        'app_name=android,app_brand=yataxi,app_ver1=1,app_ver2=2,app_ver3=3'
    ),
    'X-Request-Language': 'ru',
}

PROMOS_ON_MAP_REQUEST = {
    'position': [37.211375, 55.477065],
    'bbox': [37.211375, 55.477065, 38.022770, 55.983040],
    'cache_bbox': [37.211375, 55.477065, 38.022770, 55.983040],
    'location': [37.211375, 55.477065],
}

PROMOS_ON_MAP_HEADERS = {
    'X-Request-Application': (
        'app_name=android,app_ver1=1,app_ver2=2,app_ver3=4'
    ),
    'X-Request-Language': 'ru',
    'X-YaTaxi-UserId': 'user_id_1',
    'X-Yandex-UID': 'yauid',
    'X-YaTaxi-PhoneId': 'phone_id_1',
    'X-AppMetrica-UUID': 'appmetrica_uid',
    'X-AppMetrica-DeviceId': 'device_id',
}

EDA_BANNERS_HEADERS = {
    'X-Request-Application': 'app_name=android',
    'X-Request-Language': 'ru',
    'X-YaTaxi-UserId': 'user_id_1',
    'X-YaTaxi-PhoneId': 'phone_id_1',
    'X-AppMetrica-UUID': 'appmetrica_uid',
}

EDA_BANNERS_REQUEST = {
    'device_id': 'device_id1',
    'application': {'version': '1.2.4', 'platform': 'eda_desktop_web'},
    'state': {
        'point': {'latitude': 55.73552, 'longitude': 37.642474},
        'places': [{'id': 123321}],
        'brands': [{'id': 777}],
        'collections': [{'slug': 'slug'}],
    },
}


# Tests service start with default mocks in conftest.py
@pytest.mark.servicetest
async def test_empty(taxi_inapp_communications):
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        SHORTCUTS_REQUEST,
        headers=SHORTCUTS_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'scenario_tops': [], 'showcases': []}


async def _check_promos_on_summary(
        taxi_inapp_communications, presence, iteration=None,
):
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/promos-on-summary',
        PROMOS_ON_SUMMARY_REQUEST,
        headers=PROMOS_ON_SUMMARY_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()
    if presence:
        assert len(body['offers']['promoblocks']['items']) == 1
        assert (
            body['offers']['promoblocks']['items'][0]['show_policy'][
                'max_widget_usage_count'
            ]
            == iteration
        )
    else:
        assert not body['offers']['promoblocks']['items']


async def _check_communications(
        taxi_inapp_communications, presence, iteration=None,
):
    data = copy.deepcopy(COMMUNICATIONS_REQUEST)

    for promotion_id in [
            'id_fs_ok',
            'id_card_ok',
            'id_notification_ok',
            'id_story_ok',
    ]:
        data['promotion_id'] = promotion_id
        response = await taxi_inapp_communications.post(
            '/4.0/promotions/v1/promotion/retrieve',
            json=data,
            headers=COMMUNICATIONS_HEADERS,
        )

        if presence:
            assert response.status == 200
            prior = (
                response.json()['options']['priority']
                if promotion_id == 'id_story_ok'
                else response.json()['priority']
            )
            assert prior == iteration
        else:
            assert response.status == 404


async def _check_promos_on_map(
        taxi_inapp_communications, presence, iteration=None,
):
    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/promos-on-map',
        PROMOS_ON_MAP_REQUEST,
        headers=PROMOS_ON_MAP_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()

    if presence:
        assert len(body['objects']) == 1
        assert body['objects'][0]['bubble']['max_per_session'] == iteration
    else:
        assert not body['objects']


async def _check_eda_banners(
        taxi_inapp_communications, presence, iteration=None,
):
    response = await taxi_inapp_communications.post(
        '/inapp-communications/v1/eda-communications',
        EDA_BANNERS_REQUEST,
        headers=EDA_BANNERS_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()

    if presence:
        assert len(body['banners']) == 1
        assert body['banners'][0]['priority'] == iteration
    else:
        assert not body['banners']


async def _check_deeplink_shortcuts(
        taxi_inapp_communications, presence, iteration=None,
):
    response = await taxi_inapp_communications.post(
        '/4.0/inapp-communications/shortcuts',
        SHORTCUTS_REQUEST,
        headers=SHORTCUTS_HEADERS,
    )
    assert response.status_code == 200
    body = response.json()

    if presence:
        assert len(body['scenario_tops']) == 1
        shortcuts = body['scenario_tops'][0]['shortcuts']
        assert len(shortcuts) == 1
        assert shortcuts[0]['scenario_params']['deeplink_params'][
            'deeplink'
        ] == str(iteration)
    else:
        assert not body['scenario_tops']


@pytest.mark.config(
    INAPP_USE_BLENDER_TO_PRIORITIZE_PROMOBLOCKS=False,
    INAPP_SOURCES_OF_PROMOBLOCKS=[
        {'source_name': 'inapp-communications', 'enabled': True},
    ],
)
@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_update(taxi_inapp_communications, mockserver, load_json):
    class CallsCounter:
        calls = 0

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        resp = load_json(
            f'promotions_response_with_obsolete_ids_'
            f'iter_{str(CallsCounter.calls)}.json',
        )
        CallsCounter.calls += 1
        return resp

    # initial full update
    await _check_promos_on_summary(taxi_inapp_communications, True, 1)
    await _check_communications(taxi_inapp_communications, True, 1)
    await _check_promos_on_map(taxi_inapp_communications, True, 1)
    await _check_deeplink_shortcuts(taxi_inapp_communications, True, 1)
    await _check_eda_banners(taxi_inapp_communications, True, 1)

    # inc update
    await taxi_inapp_communications.tests_control(
        invalidate_caches=True, clean_update=False,
    )
    await _check_promos_on_summary(taxi_inapp_communications, True, 2)
    await _check_communications(taxi_inapp_communications, True, 2)
    await _check_promos_on_map(taxi_inapp_communications, True, 2)
    await _check_deeplink_shortcuts(taxi_inapp_communications, True, 2)
    await _check_eda_banners(taxi_inapp_communications, True, 2)

    # full update
    await taxi_inapp_communications.tests_control(
        invalidate_caches=True, clean_update=True,
    )
    await _check_promos_on_summary(taxi_inapp_communications, True, 3)
    await _check_communications(taxi_inapp_communications, True, 3)
    await _check_promos_on_map(taxi_inapp_communications, True, 3)
    await _check_deeplink_shortcuts(taxi_inapp_communications, True, 3)
    await _check_eda_banners(taxi_inapp_communications, True, 3)

    # inc update old revisions
    await taxi_inapp_communications.tests_control(
        invalidate_caches=True, clean_update=False,
    )
    await _check_promos_on_summary(taxi_inapp_communications, True, 3)
    await _check_communications(taxi_inapp_communications, True, 3)
    await _check_promos_on_map(taxi_inapp_communications, True, 3)
    await _check_deeplink_shortcuts(taxi_inapp_communications, True, 3)
    await _check_eda_banners(taxi_inapp_communications, True, 3)

    # inc update actual revisions
    await taxi_inapp_communications.tests_control(
        invalidate_caches=True, clean_update=False,
    )
    await _check_promos_on_summary(taxi_inapp_communications, False)
    await _check_communications(taxi_inapp_communications, False)
    await _check_promos_on_map(taxi_inapp_communications, False)
    await _check_deeplink_shortcuts(taxi_inapp_communications, False)
    await _check_eda_banners(taxi_inapp_communications, False)


def _check_db_size(pgsql, expected):
    db = pgsql['dbinappcommunications']
    cursor = db.cursor()
    cursor.execute('SELECT *  FROM inapp_communications.promos_on_map_cache')
    assert len(cursor.fetchall()) == expected


@pytest.mark.config(INAPP_CACHE_PROMOS_ON_MAP_ENABLED=True)
@pytest.mark.config(INAPP_CACHE_PROMOS_ON_MAP_TIMEOUT=0)
@pytest.mark.experiments3(filename='exp3_dummy.json')
async def test_promos_on_map_cache_clearing(
        taxi_inapp_communications, mockserver, pgsql, load_json,
):
    class CallsCounter:
        calls = 0

    @mockserver.json_handler('/promotions/internal/promotions/list')
    def _mock_promotions(request):
        resp = load_json(
            f'promotions_response_with_obsolete_ids_'
            f'iter_{str(CallsCounter.calls)}.json',
        )
        CallsCounter.calls += 1
        return resp

    # initial full update
    await _check_promos_on_map(taxi_inapp_communications, True, 1)
    _check_db_size(pgsql, 1)

    # inc update
    await taxi_inapp_communications.tests_control(
        invalidate_caches=True, clean_update=False,
    )
    _check_db_size(pgsql, 0)
    await _check_promos_on_map(taxi_inapp_communications, True, 2)
    _check_db_size(pgsql, 1)

    # full update
    await taxi_inapp_communications.tests_control(
        invalidate_caches=True, clean_update=True,
    )
    _check_db_size(pgsql, 0)
    await _check_promos_on_map(taxi_inapp_communications, True, 3)
    _check_db_size(pgsql, 1)

    # inc update old revisions
    await taxi_inapp_communications.tests_control(
        invalidate_caches=True, clean_update=False,
    )
    _check_db_size(pgsql, 0)
    await _check_promos_on_map(taxi_inapp_communications, True, 3)
    _check_db_size(pgsql, 1)

    # inc update actual revisions
    await taxi_inapp_communications.tests_control(
        invalidate_caches=True, clean_update=False,
    )
    _check_db_size(pgsql, 0)
    await _check_promos_on_map(taxi_inapp_communications, False)
    _check_db_size(pgsql, 0)
