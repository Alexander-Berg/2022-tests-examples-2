# encoding=utf-8
import datetime
import json
import time
from typing import List
from typing import Optional

import pytest

DAP_HEADERS = {
    'X-Ya-Service-Ticket': 'ticket',
    'X-YaTaxi-Park-Id': '1488',
    'X-YaTaxi-Driver-Profile-Id': 'driverSS',
    'X-Request-Application-Version': '8.30 (111)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-Request-Application': 'taximeter',
    'Accept-Language': 'ru',
}


def dap_headers(
        version_type, platform, brand='', build_type='', platform_version='',
):
    return {
        'X-Ya-Service-Ticket': 'ticket',
        'X-YaTaxi-Park-Id': '1488',
        'X-YaTaxi-Driver-Profile-Id': 'driverSS',
        'X-Request-Application-Version': '10.01 (1234)',
        'X-Request-Version-Type': version_type,
        'X-Request-Platform': platform,
        'X-Request-Application-Brand': brand,
        'X-Request-Application-Build-Type': build_type,
        'X-Request-Platform-Version': platform_version,
        'X-Request-Application': 'taximeter',
        'Accept-Language': 'ru',
    }


ACTIVE_MODE_CONSUMER = 'driver_protocol/driver_polling_state_active_mode'


@pytest.fixture
def client_notify(mockserver):
    class Handlers:
        @mockserver.json_handler('/client_notify/v2/push')
        def mock_client_notify(request):
            return {'notification_id': '123123'}

    return Handlers()


@pytest.fixture
def communications(mockserver):
    class Handlers:
        @mockserver.json_handler('/communications/driver/notification/push')
        def mock_communications(request):
            return {}

    return Handlers()


@pytest.fixture(autouse=True)
def driver_ui_profile(mockserver):
    @mockserver.json_handler('/driver_ui_profile/v1/mode')
    def mock_mode_get(request):
        assert 'park_id' in request.args
        assert 'driver_profile_id' in request.args
        return {
            'display_mode': 'default_display_mode',
            'display_profile': 'default_display_profile',
        }


@pytest.fixture(name='driver-weariness', autouse=True)
def _mock_driver_weariness(mockserver, load_json):
    @mockserver.json_handler('/driver_weariness/v1/driver-weariness')
    def _driver_weariness(request):
        _id = json.loads(request.get_data())['unique_driver_id']
        cache = load_json('driver_weariness_cache.json')
        if _id not in cache:
            return mockserver.make_response({}, status=404)
        return cache[_id]


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_DRIVERCLIENTCHAT_SPEECH_PARAMS={
        'ru': {
            'recognizer': 'yandex_speechkit',
            'vocalizer': 'undefined',
            'language_code': 'ru_RU',
        },
    },
)
# randomly testing with DAP headers instead of session
def test_basic(taxi_driver_protocol, mockserver, load_json, tvm2_client):
    tvm2_client.set_ticket(json.dumps({'19': {'ticket': 'ticket'}}))
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty', headers=DAP_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('FullAnswer.json')

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.experiments3(filename='exp3_app_matcher.json')
@pytest.mark.parametrize(
    'version_type, platform, brand, build_type, platform_version, expect_app',
    [
        ('', 'android', '', '', '', 'android prod'),
        ('', 'ios', '', '', '', 'ios prod'),
        ('az', 'android', '', '', '', 'android az'),
        ('beta', 'android', '', '', '', 'android beta'),
        ('uber', 'android', '', '', '', 'android uber'),
        ('', 'android', 'yandex', '', '11.0.0', 'android prod'),
        ('', 'ios', 'yandex', '', '11.0.0', 'ios prod'),
        ('az', 'android', 'az', '', '11.0.0', 'android az'),
        ('beta', 'android', 'yandex', 'beta', '11.0.0', 'android beta'),
        ('uber', 'android', 'uber', '', '11.0.0', 'android uber'),
        ('', 'android', 'rida', 'beta', '11.0.0', 'android rida beta'),
    ],
)
def test_driver_api_v1_auth(
        taxi_driver_protocol,
        tvm2_client,
        version_type,
        platform,
        brand,
        build_type,
        platform_version,
        expect_app,
):
    tvm2_client.set_ticket(json.dumps({'19': {'ticket': 'ticket'}}))
    headers = dap_headers(
        version_type=version_type,
        platform=platform,
        brand=brand,
        build_type=build_type,
        platform_version=platform_version,
    )
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&metrica_id=metrica1', headers=headers,
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert (
        resp_body['typed_experiments']['items']['app_matcher']['app']
        == expect_app
    )


def test_gas_stations_consent_accepted(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1489', 'qwerty1', 'driverSSS')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1489&session=qwerty1',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['taximeter_configs']['gas_stations_consent_accepted']

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1489},
        json={'driver_id': 'driverSSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response == response_internal.json()


def test_chair_categories(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.55 (562)',
        },
    )
    assert response.status_code == 200
    chairs = response.json()['taximeter_configs']['car_chairs_params']
    assert chairs['chairs'] == [
        {'brand': 'Яндекс', 'categories': [0, 1, 2], 'isofix': True},
        {'brand': '', 'categories': [3], 'isofix': False},
        {'brand': 'Яндекс', 'categories': [], 'isofix': False},
        {'brand': 'Other', 'categories': [0, 1, 2], 'isofix': True},
    ]

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.55 (562)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.now('2018-01-22T00:00:00Z')
def test_no_quality_control(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')
    driver_authorizer_service.set_session('777', 'abcdef', 'NoProviders')

    def check_hide_control(response):
        assert response.status_code == 200
        qc_params = response.json()['taximeter_configs']['qc_params']
        assert qc_params['dkk_not_required']
        assert qc_params['dkb_chair_not_required']
        assert qc_params['hide']

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    check_hide_control(response)

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driver', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=abcdef',
    )
    check_hide_control(response)

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={
            'driver_id': 'NoProviders',
            'user_agent': 'Taximeter 8.30 (111)',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.now('2018-03-01T00:00:00Z')
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'ready_gap_in_hours': 3})
def test_quality_control_text(
        taxi_driver_protocol,
        client_notify,
        redis_store,
        driver_authorizer_service,
        driver_work_rules,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'Vasya')

    # До ДКК осталось больше часа, но меньше ready_gap
    redis_store.hset(
        'Driver:DKK:DateNext:777', 'Vasya', '"2018-03-01T02:30:00Z"',
    )
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    assert qc_params['dkk_date'] == '2018-03-01T02:30:00.000000Z'
    assert qc_params['ready']
    assert qc_params['hours_to_deadline'] == 2
    text = 'Следующая проверка через 2 ч. Вы можете пройти её сейчас'
    assert qc_params['state_text'] == text

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (456)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    # До ДКК осталось меньше часа
    redis_store.hset(
        'Driver:DKK:DateNext:777', 'Vasya', '"2018-03-01T00:59:59Z"',
    )
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    assert qc_params['ready']
    assert qc_params['hours_to_deadline'] == 0
    text = (
        'Пройдите фотоконтроль сейчас. Иначе через час доступ к заказам '
        'может быть приостановлен'
    )
    assert qc_params['state_text'] == text

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (456)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()
    client_notify.mock_client_notify.wait_call()

    # Водитель просрочил ДКК
    redis_store.hset(
        'Driver:DKK:DateNext:777', 'Vasya', '"2018-02-28T23:59:59Z"',
    )
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    assert qc_params['ready']
    assert qc_params['hours_to_deadline'] == 0
    text = 'Чтобы выйти на линию, пройдите фотоконтроль'
    assert qc_params['state_text'] == text

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (456)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    # До ДКК еще двое суток
    redis_store.hset(
        'Driver:DKK:DateNext:777', 'Vasya', '"2018-03-03T00:00:00Z"',
    )
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    assert not qc_params['ready']
    assert qc_params['hours_to_deadline'] == 48
    text = (
        'Следующая проверка 03.03.2018. Вы сможете пройти ее за 3 ч. '
        'до срока в любое удобное время'
    )
    assert qc_params['state_text'] == text

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (456)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    # Водитель временно заблокирован
    redis_store.set('Driver:TimeBlock:777:Vasya', 'true')
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    text = (
        'Заказы Яндекс.Такси временно недоступны. Для разблокировки '
        'пройдите заново фотоконтроль'
    )
    assert qc_params['state_text'] == text

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (456)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    # Водитель в черном списке
    redis_store.hset(
        'Blacklist:Drivers',
        'M8209289',
        json.dumps(
            {
                'Date': '2018-02-01T00:00:00Z',
                'Description': (
                    'Человек в багажнике плохо упакован. И явно просрочен'
                ),
            },
        ),
    )
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    assert qc_params['dkk_date'] == '2018-02-01T00:00:00.000000Z'
    text = (
        'Вы добавлены в чёрный список по причине: '
        'Человек в багажнике плохо упакован. И явно просрочен. '
        'К сожалению, вы не можете работать с сервисом Яндекс.Такси.'
    )
    assert qc_params['state_text'] == text

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (456)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


def test_qc_params(
        taxi_driver_protocol,
        mockserver,
        redis_store,
        driver_authorizer_service,
        driver_work_rules,
):
    driver_authorizer_service.set_session('777', 'qwerty1', 'Vasya')
    driver_authorizer_service.set_session('777', 'qwerty2', 'selfreg')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty1',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    assert qc_params['without_bso']
    assert not qc_params['dkvu_check']
    assert not qc_params['selfie_check']

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    redis_store.hset(
        'Driver:DKK:DateLast:777', 'Vasya', '2018-02-01T08:29:49.067778Z',
    )

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty1',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    assert not qc_params['without_bso']
    assert qc_params['dkvu_check']
    assert not qc_params['selfie_check']

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty2',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    assert qc_params['without_bso']
    assert not qc_params['dkvu_check']
    assert qc_params['selfie_check']

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'selfreg', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    redis_store.hset(
        'Driver:DKK:DateLast:777', 'selfreg', '2018-02-01T08:29:49.067778Z',
    )

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty2',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    assert not qc_params['without_bso']
    assert qc_params['dkvu_check']
    assert not qc_params['selfie_check']

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'selfreg', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.redis_store(
    [
        'hset',
        'Driver:DKK:DateLast:777',
        'Vasya',
        '2018-02-01T08:29:49.067778Z',
    ],
)
def test_license_verification(
        taxi_driver_protocol,
        mockserver,
        db,
        driver_authorizer_service,
        driver_work_rules,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'Vasya')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    assert qc_params['dkvu_check']

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    query = {'driver_id': 'Vasya'}
    update = {'$set': {'license_verification': True}}
    db.dbdrivers.find_and_modify(query, update, False)

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty&license_verification=true',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    qc_params = response.json()['taximeter_configs']['qc_params']
    assert not qc_params['dkvu_check']

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal?license_verification=true',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.parametrize(
    'park,expected', [('1488', True), ('1499', True), ('1489', False)],
)
@pytest.mark.redis_store(
    ['sadd', 'PaySystem:Domains:AvailableForDrivers', '1488'],
)
def test_paysystem(
        taxi_driver_protocol, driver_authorizer_service, park, expected,
):
    driver_authorizer_service.set_session(park, 'qwerty', 'driver')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db={}&session=qwerty'.format(park),
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    taximeter_configs = response.json()['taximeter_configs']
    assert taximeter_configs['finance_params']['can_pay_in'] == expected

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': park},
        json={'driver_id': 'driver', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


def test_workshifts(
        taxi_driver_protocol,
        mockserver,
        driver_authorizer_service,
        driver_work_rules,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'Vasya')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    taximeter_configs = response.json()['taximeter_configs']
    assert taximeter_configs['work_shifts_enabled']

    assert driver_work_rules.list_times_called == 1

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.config(
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    WORKSHIFTS_TAGS_ENABLED=True,
    WORKSHIFTS_RULES_CACHE_UPDATE_ENABLED=True,
)
@pytest.mark.parametrize(
    'check,db_id,session,expected_response',
    [
        (False, '777', 'asdf1', True),
        (True, '777', 'asdf1', False),
        (True, '888', 'asdf1', True),
        (True, '1369', 'asdf1', True),
        (True, '1369', 'asdf2', False),
    ],
)
@pytest.mark.driver_experiments('show_menu_workshift_button')
@pytest.mark.now('2018-10-10T12:00:00+0300')
@pytest.mark.driver_tags_match(
    dbid='1369', uuid='Sasha', tags=['show_workshift0', 'show_workshift1'],
)
def test_workshifts_with_shifts(
        taxi_driver_protocol,
        config,
        client_notify,
        mockserver,
        check,
        db_id,
        session,
        expected_response,
        driver_authorizer_service,
        driver_work_rules,
):
    driver_id_mapper = {
        'asdf1': {'777': 'Vasya', '888': 'Sasha', '1369': 'Sasha'},
        'asdf2': {'1369': 'Vasya'},
    }
    driver_authorizer_service.set_session('777', 'asdf1', 'Vasya')
    driver_authorizer_service.set_session('888', 'asdf1', 'Sasha')
    driver_authorizer_service.set_session('1369', 'asdf1', 'Sasha')
    driver_authorizer_service.set_session('1369', 'asdf2', 'Vasya')

    config.set_values(dict(WORKSHIFTS_CHECK_SHIFTS_ENABLED=check))

    response = taxi_driver_protocol.get(
        'driver/polling/state?db={}&session={}'.format(db_id, session),
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    taximeter_configs = response.json()['taximeter_configs']
    assert taximeter_configs['work_shifts_enabled'] == expected_response

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': db_id},
        json={
            'driver_id': driver_id_mapper[session][db_id],
            'user_agent': 'Taximeter 8.30 (111)',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.config(
    FETCH_DRIVER_TAGS_BY_LICENSES_FROM_SERVICE=True,
    WORKSHIFTS_TAGS_ENABLED=True,
    WORKSHIFTS_RULES_CACHE_UPDATE_ENABLED=True,
    WORKSHIFTS_CHECK_SHIFTS_ENABLED=True,
)
@pytest.mark.now('2018-10-10T12:00:00+0300')
def test_workshifts_without_experiment(
        taxi_driver_protocol,
        client_notify,
        mockserver,
        driver_authorizer_service,
        driver_work_rules,
):
    driver_authorizer_service.set_session('1369', 'asdf2', 'Vasya')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1369&session=asdf2',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    taximeter_configs = response.json()['taximeter_configs']
    assert taximeter_configs['work_shifts_enabled']

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1369},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.config(
    TAXIMETER_UBER_INTEGRATION_ENABLED=True,
    TAXIMETER_UBER_RUSH_HOURS=[
        {'start': 3, 'end': 4},
        {'start': 0, 'end': 23},
    ],
)
def test_taximeter_uber(
        taxi_driver_protocol,
        mockserver,
        driver_authorizer_service,
        driver_work_rules,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'Vasya')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    taximeter_configs = response.json()['taximeter_configs']
    assert 'uber_params' in taximeter_configs
    assert taximeter_configs['uber_params'] == {
        'integration_enabled': True,
        'backend_enabled': True,
        'status_change_restart_delay_ms': 1000,
        'status_change_timeout_ms': 8000,
        'rush_hours_enable': False,
        'rush_hours_start_delay_ms': 300000,
        'rush_hours': [{'start': 3, 'end': 4}, {'start': 0, 'end': 23}],
    }
    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.redis_store(
    ['set', 'DriverSession:1488:qwerty', 'driverSS'],
    ['set', 'DriverSession:1489:qwerty', 'driver_8.68'],
    ['set', 'DriverSession:1369:qwerty', 'Vasya'],
    ['set', 'DriverSession:999:qwerty', '888'],
)
@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_MENU_SETTINGS={
        'enable': True,
        'cities': ['Москва', 'Алма-Ата', 'Сыктывкар'],
    },
)
@pytest.mark.parametrize(
    'park_id,offer_type',
    [
        ('1488', 'selfemployment'),
        ('1489', 'selfemployment_ie'),
        ('999', 'selfemployment_ie'),
        ('1369', 'none'),
    ],
)
def test_basic_employment_offer(
        taxi_driver_protocol,
        mockserver,
        park_id,
        offer_type,
        driver_authorizer_service,
        driver_work_rules,
):
    driver_id_mapper = {
        '1488': 'driverSS',
        '1489': 'driver_8.68',
        '1369': 'Vasya',
        '999': '888',
    }
    for key, value in driver_id_mapper.items():
        driver_authorizer_service.set_session(key, 'qwerty', value)

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=' + park_id + '&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data['employment'] == {'offer_type': offer_type}

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': park_id},
        json={
            'driver_id': driver_id_mapper[park_id],
            'user_agent': 'Taximeter 8.30 (111)',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_MENU_SETTINGS={
        'enable': False,
        'cities': ['Москва', 'Алма-Ата', 'Сыктывкар'],
    },
)
@pytest.mark.parametrize('park_id', ['1488', '1489', '1369', '999'])
def test_employment_offer_not_enabled(
        taxi_driver_protocol,
        mockserver,
        park_id,
        driver_authorizer_service,
        driver_work_rules,
):
    driver_id_mapper = {
        '1488': 'driverSS',
        '1489': 'driver_8.68',
        '1369': 'Vasya',
        '999': '888',
    }
    for key, value in driver_id_mapper.items():
        driver_authorizer_service.set_session(key, 'qwerty', value)

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=' + park_id + '&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data.get('employment') is None

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': park_id},
        json={
            'driver_id': driver_id_mapper[park_id],
            'user_agent': 'Taximeter 8.30 (111)',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    FREE_WAITING_TIME_RULES={'__default__': 600, 'Москва': 200},
)
def test_basic_free_waiting_time_config(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response_data = response.json()
    configs = response_data['taximeter_configs']['cancel_params']
    time_secs = configs['free_waiting_time_secs']
    assert time_secs == 200

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.parametrize(
    'sign_info,user_agent,expected_taximeter_version,'
    'user_agent_split, x_version_split, expected_user_agent_split',
    [
        (
            {
                'signature_exists': True,
                'signature_info': (
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiw'
                    'idmVyc2lvbl9jb2RlIjoxMDAsInNpZ25hdHVyZSI6Ik'
                    '5WMEJpVHBRTnArYVVrL2gyQmdpMncifQ'
                ),
            },
            'Taximeter-X 9.25 (2605)',
            '9.25 (2605)',
            'Taximeter-X 9.25 (3002605)',
            None,
            '9.25 (3002605)',
        ),
        (
            {
                'signature_exists': True,
                'signature_info': (
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiw'
                    'idmVyc2lvbl9jb2RlIjoxMDAsInNpZ25hdHVyZSI6Ik'
                    '5WMEJpVHBRTnArYVVrL2gyQmdpMncifQ'
                ),
            },
            'Taximeter-X 9.01 (2605)',
            '9.1 (2605)',
            'Taximeter-X 9.01 (3002605)',
            None,
            '9.1 (3002605)',
        ),
        (
            {
                'signature_exists': True,
                'signature_info': (
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiw'
                    'idmVyc2lvbl9jb2RlIjoxMDAsInNpZ25hdHVyZSI6Ik'
                    '5WMEJpVHBRTnArYVVrL2gyQmdpMncifQ'
                ),
            },
            'app:pro brand:yandex platform:android version:12.01 '
            'build:1234 build_type:x platform_version:10',
            '12.1 (1234)',
            None,
            '12.1 (3001234)',
            '12.1 (3001234)',
        ),
        (
            {
                'signature_exists': True,
                'signature_info': (
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiw'
                    'idmVyc2lvbl9jb2RlIjoxMDAsInNpZ25hdHVyZSI6Ik'
                    '5WMEJpVHBRTnArYVVrL2gyQmdpMncifQ'
                ),
            },
            'app:pro brand:yandex platform:android version:12.10 '
            'build:1234 build_type:x platform_version:10',
            '12.10 (1234)',
            'Taximeter-X 12.10 (3001234)',
            None,
            '12.10 (3001234)',
        ),
        (
            {
                'signature_exists': True,
                'signature_info': (
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiw'
                    'idmVyc2lvbl9jb2RlIjoxMDAsInNpZ25hdHVyZSI6Ik'
                    '5WMEJpVHBRTnArYVVrL2gyQmdpMncifQ'
                ),
            },
            'app:pro brand:yandex platform:android version:12.10 '
            'build:1234 build_type:x platform_version:10',
            '12.10 (1234)',
            'Taximeter-X 12.10 (3001234)',
            'Bad-X-Version-Split',
            '12.10 (3001234)',
        ),
        (
            {
                'signature_exists': False,
                'signature_ios_tmp': (
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiw'
                    'idmVyc2lvbl9jb2RlIjoxMDAsInNpZ25hdHVyZSI6Ik'
                    '5WMEJpVHBRTnArYVVrL2gyQmdpMncifQ'
                ),
            },
            'Taximeter 9.99 (1073759157)',
            '9.99 (1073759157)',
            None,
            None,
            None,
        ),
        (
            {
                'signature_exists': True,
                'signature_info': (
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiw'
                    'idmVyc2lvbl9jb2RlIjoxMDAsInNpZ25hdHVyZSI6Ik'
                    '5WMEJpVHBRTnArYVVrL2gyQmdpMncifQ'
                ),
                'signature_version': '3',
            },
            'Taximeter 8.78',
            '8.78',
            None,
            None,
            None,
        ),
        (
            {
                'signature_exists': True,
                'signature_info': (
                    'eyJhcHBfaWQiOiJydS55YW5kZXgudGF4aW1ldGVyIiw'
                    'idmVyc2lvbl9jb2RlIjoxMDAsInNpZ25hdHVyZSI6Ik'
                    '5WMEJpVHBRTnArYVVrL2gyQmdpMncifQ'
                ),
                'signature_version': 'XYZ',
                'signature_version_valid': False,
            },
            '100',
            '',
            None,
            None,
            None,
        ),
    ],
)
@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(AFS_SIGN_SEND=True)
def test_send_antifraud_sign_on(
        taxi_driver_protocol,
        mockserver,
        driver_authorizer_service,
        sign_info,
        user_agent,
        expected_taximeter_version,
        user_agent_split,
        x_version_split,
        expected_user_agent_split,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/antifraud/driver_client/check_sign')
    def mock_afs(request):
        data = request.json
        if user_agent_split or x_version_split:
            assert data['user_agent_split'] == expected_user_agent_split
        assert data['unique_driver_id'] == '543eac8978f3c2a8d7983111'
        assert not data.get('licenses')
        assert data['license_pd_ids'] == ['license_pd_id']
        assert data['driver_id'] == 'driverSS'
        assert data['taximeter_version'] == expected_taximeter_version
        assert data['user_agent'] == user_agent
        assert data['park_db_id'] == '1488'
        assert data['platform'] == 'android'
        assert data['signature_exists'] == sign_info['signature_exists']
        if data['signature_exists']:
            assert 'signature_info' in data
            assert data['signature_info'] == sign_info['signature_info']
            if 'signature_version' in sign_info and sign_info.get(
                    'signature_version_valid', True,
            ):
                assert 'signature_version' in data
                assert data['signature_version'] == int(
                    sign_info['signature_version'],
                )
            else:
                assert 'signature_version' not in data
        else:
            assert 'signature_info' not in data
        if 'signature_ios_tmp' in sign_info:
            assert sign_info['signature_ios_tmp'] == data['signature_ios_tmp']

    headers = {'Accept-Language': 'ru'}
    if user_agent is not None:
        headers['User-Agent'] = user_agent
    if user_agent_split is not None:
        headers['X-User-Agent-Split'] = user_agent_split
    if x_version_split is not None:
        headers['X-Version-Split'] = x_version_split

    if sign_info['signature_exists']:
        headers['X-Protector-Data'] = sign_info['signature_info']
        if 'signature_version' in sign_info:
            headers['X-Protector-Data-Version'] = sign_info[
                'signature_version'
            ]
    if 'signature_ios_tmp' in sign_info:
        headers['X-Image-Data'] = sign_info['signature_ios_tmp']
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty', headers=headers,
    )
    assert response.status_code == 200
    mock_afs.wait_call()

    params = {'db': 1488}
    json_body = {'driver_id': 'driverSS'}
    if user_agent is not None:
        json_body['user_agent'] = user_agent
    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params=params,
        json=json_body,
        headers={'Accept-Language': 'ru'},
    )
    if user_agent is not None:
        assert response_internal.status_code == 200
        assert response.json() == response_internal.json()
    else:
        assert response_internal.status_code == 400


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(AFS_SIGN_SEND=False)
def test_send_antifraud_sign_off(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/antifraud/driver_client/check_sign')
    def mock_afs(_):
        assert False

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    time.sleep(0.5)
    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()
    time.sleep(0.5)


@pytest.mark.parametrize(
    'feature_taximeter_version,response1,response2',
    [
        (
            '8.33',
            {
                'window_duration_millis': 10000,
                'moving_speed_km_per_hour': 18.0,
                'session_anchor_distance_limit_meters': 199.0,
                'initial_parking_anchor_distance_limit_meters': 200.0,
                'route_point_session_distance_limit_meters': 200.0,
                'billable_session_duration_millis': 180000,
                'auto_switch_on_enabled': False,
            },
            {
                'window_duration_millis': 10000,
                'moving_speed_km_per_hour': 18.0,
                'session_anchor_distance_limit_meters': 200.0,
                'initial_parking_anchor_distance_limit_meters': 200.0,
                'route_point_session_distance_limit_meters': 200.0,
                'billable_session_duration_millis': 180000,
                'auto_switch_on_enabled': True,
            },
        ),
        (
            '8.55',
            {
                'enable': True,
                'seconds_to_show': 180,
                'speed_to_hide': 100,
                'radius_to_turn_off': 50,
            },
            {
                'enable': True,
                'seconds_to_show': 180,
                'speed_to_hide': 5000,
                'radius_to_turn_off': 50,
            },
        ),
    ],
)
@pytest.mark.config(
    TAXIMETER_WAITING_IN_TRANSPORTING_BY_ZONE_V2={
        '__default__': {
            'window_duration_millis': 10000,
            'moving_speed_km_per_hour': 18.0,
            'session_anchor_distance_limit_meters': 200.0,
            'initial_parking_anchor_distance_limit_meters': 200.0,
            'route_point_session_distance_limit_meters': 200.0,
            'billable_session_duration_millis': 180000,
            'auto_switch_on_enabled': False,
        },
        'zones': {
            'Москва': {'session_anchor_distance_limit_meters': 199.0},
            'Сыктывкар': {'auto_switch_on_enabled': True},
        },
    },
    TAXIMETER_WAITING_IN_TRANSPORTING_BY_ZONE={
        '__default__': {
            'enable': True,
            'seconds_to_show': 180,
            'speed_to_hide': 10,
            'radius_to_turn_off': 50,
        },
        'zones': {
            'Москва': {'speed_to_hide': 100},
            'Сыктывкар': {'speed_to_hide': 5000},
        },
    },
)
def test_waiting_in_transporting_params(
        taxi_driver_protocol,
        config,
        feature_taximeter_version,
        response1,
        response2,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS3')
    driver_authorizer_service.set_session('777', 'qwerty1', 'driverFF')

    config.set_values(
        dict(
            TAXIMETER_VERSION_SETTINGS={
                'current': '8.45',
                'disabled': [],
                'feature_support': {
                    'taximeter_waiting_in_transporting': (
                        feature_taximeter_version
                    ),
                },
                'min': '8.45',
                'min_versions_cities': {},
            },
        ),
    )
    config.set_values(
        dict(
            TAXIMETER_VERSION_SETTINGS_BY_BUILD={
                '__default__': {
                    'current': '8.45',
                    'disabled': [],
                    'feature_support': {
                        'taximeter_waiting_in_transporting': (
                            feature_taximeter_version
                        ),
                    },
                    'min': '8.45',
                },
            },
        ),
    )
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.44 (997)',
        },
    )

    assert response.status_code == 200
    taximeter_configs = response.json()['taximeter_configs']

    assert taximeter_configs['waiting_in_transporting_params'] == response1

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS3', 'user_agent': 'Taximeter 8.44 (997)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty1',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.44 (997)',
        },
    )

    assert response.status_code == 200
    taximeter_configs = response.json()['taximeter_configs']

    assert taximeter_configs['waiting_in_transporting_params'] == response2

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'driverFF', 'user_agent': 'Taximeter 8.44 (997)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.config(
    TAXIMETER_WAITING_STATUS_PARAMS_BY_CITIES={
        '__default__': {
            'enable': True,
            'maxOrderDistance': 500,
            'maxOrderDistanceAirPort': 500,
            'maxOrderDistanceLinear': 40,
            'maxOrderPedestrianDistance': 250,
            'maxOrderPedestrianDistanceAirport': 500,
            'maxPhoneCallDistance': 2000,
            'maxPhoneCallDistanceAirport': 3000,
            'maxPhoneCallDistanceLinear': 100,
            'maxSpeed': 20,
            'responseTimeout': 5,
            'routeTimeoutMs': 30000,
        },
        'cities': {
            'Москва': {'maxOrderDistance': 100, 'responseTimeout': 10},
            'Сыктывкар': {'maxPhoneCallDistance': 5000},
        },
    },
)
def test_waiting_params(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS3')
    driver_authorizer_service.set_session('777', 'qwerty1', 'driverFF')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    taximeter_configs = response.json()['taximeter_configs']

    assert taximeter_configs['waiting_params'] == {
        'enable': True,
        'max_order_distance': 100,
        'max_order_distance_airport': 500,
        'max_order_distance_linear': 40,
        'max_order_pedestrian_distance': 250,
        'max_order_pedestrian_distance_airport': 500,
        'max_phone_call_distance': 2000,
        'max_phone_call_distance_airport': 3000,
        'max_phone_call_distance_linear': 100,
        'max_speed': 20,
        'response_timeout': 10,
        'route_timeout_ms': 30000,
        'max_order_distance_lbs': 3000,
        'max_phone_call_distance_lbs': 3000,
    }

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS3', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty1',
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    taximeter_configs = response.json()['taximeter_configs']

    assert taximeter_configs['waiting_params'] == {
        'enable': True,
        'max_order_distance': 500,
        'max_order_distance_airport': 500,
        'max_order_distance_linear': 40,
        'max_order_pedestrian_distance': 250,
        'max_order_pedestrian_distance_airport': 500,
        'max_phone_call_distance': 5000,
        'max_phone_call_distance_airport': 3000,
        'max_phone_call_distance_linear': 100,
        'max_speed': 20,
        'response_timeout': 5,
        'route_timeout_ms': 30000,
        'max_order_distance_lbs': 3000,
        'max_phone_call_distance_lbs': 3000,
    }

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'driverFF', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_DRIVERCLIENTCHAT_SPEECH_PARAMS={
        'ru': {
            'recognizer': 'yandex_speechkit',
            'vocalizer': 'undefined',
            'language_code': 'ru_RU',
        },
    },
)
def test_gps_params(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    gps_params = response.json()['gps_params']
    assert gps_params == load_json('FullAnswer.json')['gps_params']

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_WAITING_STATUS_PARAMS_BY_CITIES={
        '__default__': {
            'enable': True,
            'maxOrderDistance': 500,
            'maxOrderDistanceAirPort': 500,
            'maxOrderDistanceLinear': 40,
            'maxOrderDistanceLbs': 2000,
            'maxOrderPedestrianDistance': 100,
            'maxOrderPedestrianDistanceAirport': 100,
            'maxPhoneCallDistance': 500,
            'maxPhoneCallDistanceAirport': 1500,
            'maxPhoneCallDistanceLinear': 100,
            'maxPhoneCallDistanceLbs': 5000,
            'maxSpeed': 10,
            'responseTimeout': 5,
            'routeTimeoutMs': 30000,
        },
        'cities': {},
    },
)
def test_updating_waiting_params(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    waiting_params = response.json()['taximeter_configs']['waiting_params']
    assert waiting_params['max_order_distance_lbs'] == 2000
    assert waiting_params['max_phone_call_distance_lbs'] == 5000

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.now('2018-01-22T00:30:00Z')
@pytest.mark.config(
    TAXIMETER_DRIVERCLIENTCHAT_SPEECH_PARAMS={
        'ru': {
            'recognizer': 'yandex_speechkit',
            'vocalizer': 'undefined',
            'language_code': 'ru_RU',
        },
    },
    BPQ_ENABLE=True,
)
@pytest.mark.driver_experiments('bad_position_quality')
@pytest.mark.driver_experiments('bad_position_quality_p')
@pytest.mark.parametrize(
    'session_id,bad_position_quality', [('1111', True), ('2222', False)],
)
def test_bad_position_quality(
        taxi_driver_protocol,
        mockserver,
        session_id,
        bad_position_quality,
        driver_authorizer_service,
):
    driver_id_mapper = {'1111': 'driverSS', '2222': 'driverSS1'}
    driver_authorizer_service.set_session('1488', '1111', 'driverSS')
    driver_authorizer_service.set_session('1488', '2222', 'driverSS1')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=%s' % session_id,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response = response.json()
    if bad_position_quality:
        assert response['bad_position']['is_bad_position'] is True
    else:
        assert 'bad_position' not in response

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={
            'driver_id': driver_id_mapper[session_id],
            'user_agent': 'Taximeter 8.30 (111)',
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response == response_internal.json()


@pytest.mark.config(
    TAXIMETER_DRIVERCLIENTCHAT_SPEECH_PARAMS={
        'ru': {
            'recognizer': 'yandex_speechkit',
            'vocalizer': 'undefined',
            'language_code': 'ru_RU',
        },
    },
    BPQ_ENABLE=True,
)
@pytest.mark.driver_experiments('bad_position_quality')
@pytest.mark.driver_experiments(
    bad_position_quality_p={
        'salt': '100001',
        'driver_id_percent': {'to': 50, 'from': 0},
    },
)
@pytest.mark.parametrize(
    'timestamp, bad_position_quality',
    [
        (datetime.datetime(2018, 1, 22, 0, 0), True),
        (datetime.datetime(2018, 1, 22, 0, 1), True),
        (datetime.datetime(2018, 1, 22, 0, 2), True),
        (datetime.datetime(2018, 1, 22, 0, 20), False),
        (datetime.datetime(2018, 1, 22, 0, 21), False),
        (datetime.datetime(2018, 1, 22, 0, 22), False),
        (datetime.datetime(2018, 1, 22, 0, 30), True),
        (datetime.datetime(2018, 1, 22, 0, 31), True),
        (datetime.datetime(2018, 1, 22, 0, 32), True),
    ],
)
def test_bad_position_quality_experiment(
        taxi_driver_protocol,
        mockserver,
        timestamp,
        bad_position_quality,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', '1111', 'driverSS')

    taxi_driver_protocol.tests_control(invalidate_caches=True, now=timestamp)
    session_id = '1111'
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=%s' % session_id,
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response = response.json()
    if bad_position_quality:
        assert response['bad_position']['is_bad_position'] is True
    else:
        assert 'bad_position' not in response

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response == response_internal.json()


@pytest.mark.filldb(countries='tutorial_config')
def test_tutorial_config_by_config(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')
    driver_authorizer_service.set_session('1489', 'qwerty1', 'driverSSS')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['tutorial_config'] == {
        'mode': 'none',
        'fallback_to_web': True,
        'show_in_settings': False,
        'reason': 'config',
        'web_tutorial_url': 'http://ya.ru',
    }

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response == response_internal.json()

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1489&session=qwerty1',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['tutorial_config'] == {
        'mode': 'onboarding',
        'fallback_to_web': True,
        'show_in_settings': False,
        'reason': 'config',
        'web_tutorial_url': 'http://ya.ru',
    }

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1489},
        json={'driver_id': 'driverSSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response == response_internal.json()


@pytest.mark.filldb(countries='tutorial_config_2')
def test_tutorial_config_by_config_web(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1489', 'qwerty1', 'driverSSS')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1489&session=qwerty1',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['tutorial_config'] == {
        'mode': 'web',
        'fallback_to_web': True,
        'show_in_settings': False,
        'reason': 'config',
        'web_tutorial_url': 'http://ya.ru',
    }

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1489},
        json={'driver_id': 'driverSSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response == response_internal.json()


@pytest.mark.filldb(countries='tutorial_config_2')
def test_tutorial_config_by_config_none(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['tutorial_config'] == {
        'mode': 'none',
        'fallback_to_web': True,
        'show_in_settings': False,
        'reason': 'config',
        'web_tutorial_url': 'http://ya.ru',
    }

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response == response_internal.json()


@pytest.mark.filldb(countries='tutorial_config_2')
def test_tutorial_config_by_exp_no_one(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['tutorial_config'] == {
        'mode': 'none',
        'fallback_to_web': True,
        'show_in_settings': False,
        'reason': 'config',
        'web_tutorial_url': 'http://ya.ru',
    }

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response == response_internal.json()


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_DRIVERCLIENTCHAT_SPEECH_PARAMS={
        'ru': {
            'recognizer': 'yandex_speechkit',
            'vocalizer': 'undefined',
            'language_code': 'ru_RU',
        },
    },
)
@pytest.mark.parametrize(
    'user_agent, response_file_name',
    [
        (
            'Taximeter 8.32 (457)',
            'mocked_response_experiments3_driver_experiments.json',
        ),
    ],
)
def test_typed_experiments3_driver_experiments(
        taxi_driver_protocol,
        mockserver,
        load_json,
        user_agent,
        response_file_name,
        driver_authorizer_service,
        experiments3,
):
    experiments3.add_experiments_json(load_json(response_file_name))

    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru', 'User-Agent': user_agent},
    )
    assert response.status_code == 200
    assert response.json()['driver_experiments'] == ['driver_experiment1.0']

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': user_agent},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_DRIVERCLIENTCHAT_SPEECH_PARAMS={
        'ru': {
            'recognizer': 'yandex_speechkit',
            'vocalizer': 'undefined',
            'language_code': 'ru_RU',
        },
    },
)
@pytest.mark.parametrize(
    'user_agent, response_file_name, typed_experiments_field',
    [
        (
            'Taximeter 8.31 (456)',
            'mocked_response_experiments3_internal_navigation_ok.json',
            {
                'version': 4426,
                'items': {
                    'taximeter_internal_navigation': {'is_enabled': True},
                },
            },
        ),
        (
            'Taximeter 8.31 (456)',
            (
                'mocked_response_experiments3_'
                'internal_navigation_another_country.json'
            ),
            {
                'version': 4426,
                'items': {
                    'taximeter_internal_navigation': {'is_enabled': False},
                },
            },
        ),
        (
            'Taximeter 8.31 (456)',
            'mocked_response_experiments3_internal_navigation_city_ok.json',
            {
                'version': 4426,
                'items': {
                    'taximeter_internal_navigation': {'is_enabled': True},
                },
            },
        ),
        (
            'Taximeter 8.31 (456)',
            (
                'mocked_response_experiments3_'
                'internal_navigation_another_city.json'
            ),
            {
                'version': 4426,
                'items': {
                    'taximeter_internal_navigation': {'is_enabled': False},
                },
            },
        ),
        (
            'Taximeter 8.31 (456)',
            'mocked_response_experiments3_internal_navigation_empty.json',
            {'version': -1, 'items': {}},
        ),
        (
            'Taximeter 8.31 (456)',
            'mocked_response_experiments3_internal_navigation_percent_yes'
            '.json',
            {
                'version': 4426,
                'items': {
                    'taximeter_internal_navigation': {'is_enabled': True},
                },
            },
        ),
        (
            'Taximeter 8.31 (456)',
            'mocked_response_experiments3_internal_navigation_percent_no.json',
            {
                'version': 4426,
                'items': {
                    'taximeter_internal_navigation': {'is_enabled': False},
                },
            },
        ),
        (
            'Taximeter 8.32 (457)',
            (
                'mocked_response_experiments3_internal_navigation_ok_'
                'for_new_version.json'
            ),
            {
                'version': 4426,
                'items': {
                    'driver_experiment1.0': {},
                    'taximeter_internal_navigation': {'is_enabled': True},
                },
            },
        ),
        (
            'Taximeter 8.31 (457)',
            (
                'mocked_response_experiments3_internal_navigation_ok_'
                'for_new_version.json'
            ),
            {'version': 4426, 'items': {}},
        ),
        (
            'Taximeter-AZ 8.32 (457)',
            (
                'mocked_response_experiments3_internal_navigation_ok_'
                'for_new_version.json'
            ),
            {
                'version': 4426,
                'items': {
                    'driver_experiment1.0': {},
                    'taximeter_internal_navigation': {'is_enabled': True},
                },
            },
        ),
        (
            'Taximeter-AZ 8.31 (457)',
            (
                'mocked_response_experiments3_internal_navigation_ok_'
                'for_new_version.json'
            ),
            {'version': 4426, 'items': {}},
        ),
    ],
)
def test_typed_experiments3_ok(
        taxi_driver_protocol,
        mockserver,
        load_json,
        user_agent,
        response_file_name,
        typed_experiments_field,
        driver_authorizer_service,
        experiments3,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    experiments3.add_experiments_json(load_json(response_file_name))

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru', 'User-Agent': user_agent},
    )
    assert response.status_code == 200
    response_sample = load_json('FullAnswer.json')
    response_sample['typed_experiments'] = typed_experiments_field
    assert response.json() == response_sample

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': user_agent},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.now('2018-01-22T00:00:00Z')
@pytest.mark.config(
    TAXIMETER_DRIVERCLIENTCHAT_SPEECH_PARAMS={
        'ru': {
            'recognizer': 'yandex_speechkit',
            'vocalizer': 'undefined',
            'language_code': 'ru_RU',
        },
    },
)
@pytest.mark.parametrize(
    'mode, typed_experiments_field, driver_experiments_field',
    [
        (
            'ok',
            {
                'version': 4426,
                'items': {
                    'taximeter_internal_navigation': {'is_enabled': True},
                },
            },
            ['taximeter_internal_navigation'],
        ),
        ('experiments3_500', {'version': -1, 'items': {}}, []),
        ('incorrect_response', {'version': -1, 'items': {}}, []),
    ],
)
def test_typed_experiments3_fail(
        taxi_driver_protocol,
        mockserver,
        load_json,
        mode,
        typed_experiments_field,
        driver_experiments_field,
        now,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/v1/experiments/updates')
    def experiments3_proxy(request):
        if mode == 'ok':
            return load_json(
                'mocked_response_experiments3_internal_navigation_ok.json',
            )
        elif mode == 'experiments3_500':
            return mockserver.make_response(500, 'test failed')
        elif mode == 'incorrect_response':
            return {'something': 'wrong'}
        else:
            assert mode == ''

    taxi_driver_protocol.tests_control(now, invalidate_caches=True)

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.31 (456)',
        },
    )
    assert response.status_code == 200
    response_sample = load_json('FullAnswer.json')
    response_sample['typed_experiments'] = typed_experiments_field
    response_sample['driver_experiments'] = driver_experiments_field
    assert response.json() == response_sample

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.31 (456)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.experiments3(
    name='exp3_with_driver_tags',
    consumers=['taximeter/driver_polling_state'],
    match={
        'predicate': {'type': 'true'},
        'enabled': True,
        'applications': [{'name': 'taximeter', 'version_range': {}}],
    },
    clauses=[
        {
            'title': 'Попадем в эксперимент, если есть тег developer',
            'value': {'exp_enabled': True},
            'predicate': {
                'type': 'contains',
                'init': {
                    'arg_name': 'driver_tags',
                    'set_elem_type': 'string',
                    'value': 'developer',
                },
            },
        },
    ],
    default_value={'exp_enabled': False},
)
@pytest.mark.parametrize(
    'driver_tags, typed_experiments_field',
    [
        (
            [],
            {
                'version': 1,
                'items': {'exp3_with_driver_tags': {'exp_enabled': False}},
            },
        ),
        (
            ['courier'],
            {
                'version': 1,
                'items': {'exp3_with_driver_tags': {'exp_enabled': False}},
            },
        ),
        (
            ['courier', 'developer'],
            {
                'version': 1,
                'items': {'exp3_with_driver_tags': {'exp_enabled': True}},
            },
        ),
    ],
)
def test_typed_experiments3_driver_tags_kwarg(
        taxi_driver_protocol,
        mockserver,
        driver_authorizer_service,
        driver_tags_mocks,
        experiments3,
        driver_tags,
        typed_experiments_field,
):
    dbid, uuid, session = '1488', 'driverSS', 'qwerty'
    driver_authorizer_service.set_session(dbid, session, uuid)
    driver_tags_mocks.set_tags_info(dbid=dbid, uuid=uuid, tags=driver_tags)

    response = taxi_driver_protocol.get(
        f'driver/polling/state?db={dbid}&session={session}',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.31 (457)',
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['typed_experiments'] == typed_experiments_field


@pytest.mark.now('2020-04-24T17:00:00Z')
@pytest.mark.experiments3(
    name='digital_pass_check',
    consumers=['taximeter/driver_polling_state'],
    match={
        'predicate': {'type': 'true'},
        'enabled': True,
        'applications': [{'name': 'taximeter', 'version_range': {}}],
    },
    clauses=[
        {
            'title': 'По геозонам',
            'value': {},
            'predicate': {
                'init': {
                    'arg_name': 'geoarea',
                    'set_elem_type': 'string',
                    'set': ['moscow'],
                },
                'type': 'in_set',
            },
        },
    ],
)
@pytest.mark.parametrize(
    'lon, lat, experiment_found',
    [
        (37.634555, 55.751516, True),  # Moscow
        (60.601571, 56.788751, False),  # Ekb
    ],
)
def test_typed_experiments3_geoarea_kwarg(
        taxi_driver_protocol,
        mockserver,
        lon,
        lat,
        experiment_found,
        now,
        driver_authorizer_service,
        experiments3,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.get(
        f'driver/polling/state?db=1488&session=qwerty&lat={lat}&lon={lon}',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.32 (555)',
        },
    )
    assert response.status_code == 200
    typed_experiments = response.json()['typed_experiments']
    assert (
        'digital_pass_check' in typed_experiments['items']
    ) is experiment_found


@pytest.mark.now('2020-04-24T17:00:00Z')
@pytest.mark.experiments3(
    name='replace_activity_with_priority',
    consumers=['taximeter/driver_polling_state'],
    match={
        'predicate': {'type': 'true'},
        'enabled': True,
        'applications': [{'name': 'taximeter', 'version_range': {}}],
    },
    clauses=[
        {
            'title': 'По геоиерархии',
            'value': {},
            'predicate': {
                'init': {
                    'arg_name': 'zones',
                    'set_elem_type': 'string',
                    'value': 'moscow',
                },
                'type': 'contains',
            },
        },
    ],
)
@pytest.mark.parametrize(
    'lon, lat, experiment_found',
    [
        (37.634555, 55.751516, True),  # Moscow
        (60.601571, 56.788751, False),  # Ekb
    ],
)
def test_typed_experiments3_zones_kwarg_with_geoarea(
        taxi_driver_protocol,
        mockserver,
        lon,
        lat,
        experiment_found,
        now,
        driver_authorizer_service,
        experiments3,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.get(
        f'driver/polling/state?db=1488&session=qwerty&lat={lat}&lon={lon}',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.32 (555)',
        },
    )
    assert response.status_code == 200
    typed_experiments = response.json()['typed_experiments']
    assert (
        'replace_activity_with_priority' in typed_experiments['items']
    ) is experiment_found


@pytest.mark.now('2020-04-24T17:00:00Z')
@pytest.mark.experiments3(
    name='replace_activity_with_priority',
    consumers=['taximeter/driver_polling_state'],
    match={
        'predicate': {'type': 'true'},
        'enabled': True,
        'applications': [{'name': 'taximeter', 'version_range': {}}],
    },
    clauses=[
        {
            'title': 'По геоиерархии',
            'value': {},
            'predicate': {
                'init': {
                    'arg_name': 'zones',
                    'set_elem_type': 'string',
                    'value': 'br_tsentralnyj_fo',
                },
                'type': 'contains',
            },
        },
    ],
)
@pytest.mark.parametrize(
    'lon, lat, experiment_found',
    [
        (37.634555, 55.751516, True),  # Moscow
        (60.601571, 56.788751, False),  # Ekb
    ],
)
def test_typed_experiments3_zones_kwarg(
        taxi_driver_protocol,
        mockserver,
        lon,
        lat,
        experiment_found,
        now,
        driver_authorizer_service,
        experiments3,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    response = taxi_driver_protocol.get(
        f'driver/polling/state?db=1488&session=qwerty&lat={lat}&lon={lon}',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.32 (555)',
        },
    )
    assert response.status_code == 200
    typed_experiments = response.json()['typed_experiments']
    assert (
        'replace_activity_with_priority' in typed_experiments['items']
    ) is experiment_found


@pytest.mark.config(
    EXTRA_EXAMS_INFO={
        'business': {
            'description': 'Допуск к Бизнес тарифу',
            'permission': ['kids'],
            'requires': [],
        },
    },
)
@pytest.mark.parametrize(
    'enabled,premium_tariffs,driver_profile,expected_response',
    [
        (False, [], {'id': 'driverSS', 'deaf': False}, {}),
        (True, [], {'id': 'driverSS', 'deaf': False}, {'specialties': []}),
        (True, [], {'id': 'driverSS'}, {'specialties': []}),
        (
            True,
            [],
            {'id': 'driverSS', 'deaf': True},
            {'specialties': [{'type': 'impaired_hearing'}]},
        ),
        (
            True,
            ['business'],
            {'id': 'driverSS', 'deaf': True},
            {
                'specialties': [{'type': 'impaired_hearing'}],
                'service_status': {'type': 'premium'},
            },
        ),
    ],
)
def test_impaired_hearing_drivers(
        taxi_driver_protocol,
        mockserver,
        config,
        client_notify,
        enabled,
        premium_tariffs,
        driver_profile,
        expected_response,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    config.set_values(
        dict(
            DRIVER_SPECIALTIES_ENABLED=enabled,
            DRIVER_SPECIALTIES_PREMIUM_TARIFFS=premium_tariffs,
        ),
    )

    @mockserver.json_handler('/parks/driver-profiles/list')
    def driver_profiles(request):
        assert request.json == {
            'query': {
                'park': {'driver_profile': {'id': ['driverSS']}, 'id': '1488'},
            },
            'fields': {'driver_profile': ['deaf']},
            'removed_drivers_mode': 'as_normal_driver',
        }
        return {
            'driver_profiles': [{'driver_profile': driver_profile}],
            'parks': [],
        }

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    response = response.json()
    if enabled:
        assert response['driver'] == expected_response
    else:
        assert 'driver' not in response

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response == response_internal.json()


@pytest.mark.config(DRIVER_SPECIALTIES_ENABLED=True)
@pytest.mark.parametrize('err_code', [400, 500, 502, 503])
def test_parks_fallback(
        taxi_driver_protocol,
        mockserver,
        config,
        client_notify,
        err_code,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/parks/driver-profiles/list')
    def driver_profiles(request):
        return mockserver.make_response('', err_code)

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json()['driver'] == {'specialties': []}

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_DEFAULT_MODE={'default_mode': 'default'},
    DRIVER_MODE_TYPES={'default': 'default_type'},
    DRIVER_POLLING_STATE_USE_DRIVER_UI_PROFILE=False,
)
def test_dms_active_mode(
        taxi_driver_protocol,
        driver_authorizer_service,
        mockserver,
        experiments3,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    # no dms handler - 404
    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json()['active_mode'] == 'default'
    assert response.json()['active_mode_type'] == 'default_type'

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driver', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    # explicit 500
    @mockserver.json_handler('/driver_mode_subscription/v1/mode/get')
    def get_handler_500(request):
        return mockserver.make_response(status=500)

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json()['active_mode'] == 'default'
    assert response.json()['active_mode_type'] == 'default_type'

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driver', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    # no experiment3
    @mockserver.json_handler('/driver_mode_subscription/v1/mode/get')
    def get_handler_ok(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'active_mode': 'definitely_not_default',
                    'active_mode_type': 'some_other_value',
                    'active_since': '2019-11-01T00:00:00.000Z',
                },
            ),
            status=200,
        )

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json()['active_mode'] == 'default'
    assert response.json()['active_mode_type'] == 'default_type'

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driver', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()

    # add experiment3
    experiments3.add_experiment(
        name='driver_modes',
        consumers=[ACTIVE_MODE_CONSUMER],
        match={
            'consumers': [ACTIVE_MODE_CONSUMER],
            'predicate': {'type': 'true'},
            'enabled': True,
            'applications': [{'name': 'taximeter', 'version_range': {}}],
        },
        clauses=[
            {
                'title': 'main_clause',
                'value': {},
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_name': 'driver_id',
                                    'arg_type': 'string',
                                    'value': 'driver',
                                },
                            },
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_name': 'park_dbid',
                                    'arg_type': 'string',
                                    'value': '1488',
                                },
                            },
                        ],
                    },
                },
            },
        ],
    )
    taxi_driver_protocol.invalidate_caches()

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=qwerty',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.30 (111)',
        },
    )
    assert response.status_code == 200
    assert response.json()['active_mode'] == 'definitely_not_default'
    assert response.json()['active_mode_type'] == 'some_other_value'

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driver', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_DEFAULT_MODE={'default_mode': 'orders'},
    DRIVER_MODE_TYPES={'orders': 'orders', 'driver_fix': 'driver_fix'},
    DRIVER_POLLING_STATE_USE_DRIVER_UI_PROFILE=False,
)
@pytest.mark.parametrize(
    'active_mode,result', [('driver_fix', False), ('orders', True)],
)
def test_workshifts_show_with_driver_modes(
        taxi_driver_protocol,
        driver_authorizer_service,
        mockserver,
        experiments3,
        driver_work_rules,
        active_mode,
        result,
):
    driver_authorizer_service.set_session('777', 'qwerty', 'Vasya')

    # add experiment3
    experiments3.add_experiment(
        name='driver_modes',
        consumers=[ACTIVE_MODE_CONSUMER],
        match={
            'consumers': [ACTIVE_MODE_CONSUMER],
            'predicate': {'type': 'true'},
            'enabled': True,
            'applications': [{'name': 'taximeter', 'version_range': {}}],
        },
        clauses=[
            {
                'title': 'main_clause',
                'value': {},
                'predicate': {
                    'type': 'all_of',
                    'init': {
                        'predicates': [
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_name': 'driver_id',
                                    'arg_type': 'string',
                                    'value': 'Vasya',
                                },
                            },
                            {
                                'type': 'eq',
                                'init': {
                                    'arg_name': 'park_dbid',
                                    'arg_type': 'string',
                                    'value': '777',
                                },
                            },
                        ],
                    },
                },
            },
        ],
    )
    taxi_driver_protocol.invalidate_caches()

    @mockserver.json_handler('/driver_mode_subscription/v1/mode/get')
    def get_handler_(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'active_mode': active_mode,
                    'active_mode_type': active_mode,
                    'active_since': '2019-12-12T00:00:00.000Z',
                },
            ),
            status=200,
        )

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=777&session=qwerty',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 8.30 (111)',
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response['active_mode'] == active_mode
    assert response['active_mode_type'] == active_mode
    assert response['taximeter_configs']['work_shifts_enabled'] == result

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 777},
        json={'driver_id': 'Vasya', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response == response_internal.json()


@pytest.mark.now('2020-04-21T15:05:00Z')
@pytest.mark.config(
    TAXIMETER_GPS_FILTER_SETTINGS_BY_CITIES={
        '__default__': {
            'accuracy_warning_threshold_meters': 112.3,
            'accuracy_filter': 1000,
            'additional_providers_allow_statuses': [5],
            'change_to_lbs_distance_meters': 100000,
            'clear_after_rows_count_deleted': 300,
            'close_order_gps_timeout_millis': 10000,
            'db_buffer_millis': 1000,
            'db_buffer_size': 5,
            'db_max_orders': 2,
            'db_max_records': 100000,
            'db_records_delete_check_delay': 600000,
            'distance_delta_meters': 0,
            'enable_delta_meters': 1000,
            'enable_save_track': True,
            'enable_send_track': True,
            'gnss_anomaly_min_millis': 60000,
            'is_lbs_enabled': True,
            'is_lbs_turned_on': True,
            'is_mapkit_guide_enabled': False,
            'is_mapkit_guide_turned_on': False,
            'is_network_enabled': True,
            'is_network_turned_on': True,
            'kalman_coordinate_noise': 4,
            'kalman_time_step': 1,
            'last_good_location_delta_millis': 600000,
            'last_good_location_filter_enabled': True,
            'lbs_at_start': True,
            'lbs_good_accuracy': 200,
            'lbs_old_delta_millis': 30000,
            'lbs_polling_delay_millis': 10000,
            'location_provider': 'android',
            'max_distance': 15000,
            'min_distance': 15,
            'network_distance_meters': 0,
            'network_interval_millis': 10000,
            'old_location_millis': 300000,
            'order_shift_seconds': 0,
            'pause_time_not_to_ask_lbs_vs_gps_millis': 6000000,
            'providers_send_info': [
                'lbs',
                'mapkit_guide',
                'passive',
                'network',
                'gps',
            ],
            'retry_delay_millis': 5000,
            'satellites_bound': 3,
            'server_distance_delta_meters': 0,
            'server_time_delta_millis': 500,
            'speed_filter': 100,
            'switch_to_navi_timeout_millis': 10000,
            'time_before_change_bad_gps_to_lbs_millis': 30000,
            'time_delta_millis': 500,
            'use_kalman': False,
            'waiting_gps_lbs_min_distance_meters': 200,
        },
        'cities': {},
    },
)
def test_accuracy_warning_threshold_meters(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', '1111', 'driverSS')

    response = taxi_driver_protocol.get(
        'driver/polling/state?db=1488&session=1111',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    gps_params = response.json()['gps_params']
    assert gps_params['accuracy_warning_threshold_meters'] == 112.3

    response_internal = taxi_driver_protocol.post(
        'driver/polling/state/internal',
        params={'db': 1488},
        json={'driver_id': 'driverSS', 'user_agent': 'Taximeter 8.30 (111)'},
        headers={'Accept-Language': 'ru'},
    )
    assert response_internal.status_code == 200
    assert response.json() == response_internal.json()


@pytest.mark.now('2020-04-24T17:00:00Z')
@pytest.mark.parametrize(
    'in_experiment, policy, display_mode, display_profile,'
    'expected_concern, expected_profile',
    [
        # proxy policy into urgent argument
        (False, 'invalidate', 'orders', 'driver', 'urgent', 'usual_driver'),
        # no policy parameter
        (False, None, 'orders', 'driver', 'cached', 'usual_driver'),
        # force urgent concern based on experiment
        (True, None, 'orders', 'driver', 'urgent', 'usual_driver'),
        # explicitly not urgent (without experiment)
        (False, 'cached', 'orders', 'driver', 'cached', 'usual_driver'),
        # explicitly not urgent (ignore experiment)
        (True, 'cached', 'orders', 'driver', 'cached', 'usual_driver'),
        # detect courier ui
        (False, 'cached', 'orders', 'courier', 'cached', 'courier'),
        (True, 'invalidate', 'driver_fix', 'driver', 'urgent', 'driver_fix'),
        # default config value
        (False, 'cached', 'new', 'new', 'cached', 'default'),
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    name='ui_feature_toggles',
    consumers=['taximeter/driver_polling_state'],
    match={
        'predicate': {'type': 'true'},
        'enabled': True,
        'applications': [{'name': 'taximeter', 'version_range': {}}],
    },
    clauses=[
        {
            'value': {'profile': 'kwarg-missing'},
            'predicate': {
                'type': 'is_null',
                'init': {'arg_name': 'driver_mode_type'},
            },
        },
        {
            'value': {'profile': 'usual_driver'},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'driver_mode_type',
                    'set_elem_type': 'string',
                    'value': 'orders',
                },
            },
        },
        {
            'value': {'profile': 'driver_fix'},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'driver_mode_type',
                    'set_elem_type': 'string',
                    'value': 'driver_fix',
                },
            },
        },
        {
            'value': {'profile': 'courier'},
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'driver_mode_type',
                                'set_elem_type': 'string',
                                'value': 'orders',
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'display_profile',
                                'set_elem_type': 'string',
                                'value': 'courier',
                            },
                        },
                    ],
                },
            },
        },
    ],
    default_value={'profile': 'default'},
)
def test_ui_feature_toggles(
        taxi_driver_protocol,
        mockserver,
        in_experiment: bool,
        policy: Optional[str],
        display_mode: str,
        display_profile: str,
        expected_concern: str,
        expected_profile: str,
        now,
        driver_authorizer_service,
        experiments3,
):
    park_id = '1488'
    driver_id = 'driver'
    driver_authorizer_service.set_session(park_id, 'qwerty', driver_id)

    @mockserver.json_handler('/driver_ui_profile/v1/mode')
    def mock_mode_get(request):
        assert request.args['park_id'] == park_id
        assert request.args['driver_profile_id'] == driver_id
        assert request.args['concern'] == expected_concern
        return {
            'display_mode': display_mode,
            'display_profile': display_profile,
        }

    # This experiment may force 'urgent' concern on driver-ui-profile call
    experiments3.add_experiment(
        name='driver_modes',
        consumers=[ACTIVE_MODE_CONSUMER],
        match={
            'consumers': [ACTIVE_MODE_CONSUMER],
            'predicate': {'type': 'true'},
            'enabled': True,
            'applications': [{'name': 'taximeter', 'version_range': {}}],
        },
        clauses=[
            {
                'predicate': {'type': ('true' if in_experiment else 'false')},
                'value': {},
            },
        ],
    )
    taxi_driver_protocol.invalidate_caches()

    policy_param = '' if policy is None else f'&driver_mode_policy={policy}'
    response = taxi_driver_protocol.get(
        f'driver/polling/state?db={park_id}&session=qwerty{policy_param}',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.32 (555)',
        },
    )
    assert response.status_code == 200

    # TODO: Upgrade testsuite submodule to enable configs3.0
    # parameters = response.json()['parameters']
    # assert 'ui_feature_toggles' in parameters['items']
    # feature_toggles = parameters['items']['ui_feature_toggles']
    # assert feature_toggles['profile'] == expected_profile


_FALLBACK_RULES = [
    {'tag': 'orders', 'display_mode': 'orders', 'display_profile': 'orders'},
    {
        'tag': 'courier',
        'display_mode': 'courier',
        'display_profile': 'power_safe',
    },
]


def _fallback_config(condition: str):
    return {'condition': condition, 'rules': _FALLBACK_RULES}


@pytest.mark.now('2020-04-24T17:00:00Z')
@pytest.mark.parametrize(
    'policy, fail_requests, fallback_condition, driver_tags, expected_code',
    [
        pytest.param('cached', [], 'never', None, 200, id='no_failure'),
        pytest.param('cached', ['ui'], 'never', None, 500, id='disabled'),
        pytest.param(
            'cached',
            ['ui'],
            'always',
            ['courier'],
            200,
            id='courier_always_falls_back',
        ),
        pytest.param(
            'cached',
            ['ui'],
            'always',
            ['developer'],
            500,
            id='failed_to_match_rule',
        ),
        pytest.param(
            'cached',
            ['ui', 'tags'],
            'always',
            [],
            500,
            id='failed_to_get_tags',
        ),
        pytest.param(
            'invalidate',
            ['ui'],
            'only_cached',
            [],
            500,
            id='disabled_by_concern',
        ),
        pytest.param(
            'cached',
            ['ui'],
            'only_cached',
            ['courier'],
            200,
            id='fallback_cached',
        ),
        pytest.param(
            'cached',
            ['ui'],
            'only_cached',
            ['developer'],
            500,
            id='failed_to_match_rule_2',
        ),
        pytest.param(
            'cached',
            ['ui', 'tags'],
            'only_cached',
            [],
            500,
            id='failed_to_get_tags_2',
        ),
    ],
)
def test_driver_ui_profile_tags_fallback(
        taxi_driver_protocol,
        mockserver,
        config,
        policy: str,
        fail_requests: List[str],
        fallback_condition: str,
        driver_tags: Optional[List[str]],
        expected_code: int,
        now,
        driver_authorizer_service,
):
    park_id = '1488'
    driver_id = 'driver'
    session = 'qwerty'
    driver_authorizer_service.set_session(park_id, session, driver_id)

    config.set_values(
        dict(
            DRIVER_POLLING_STATE_DRIVER_UI_TAGS_FALLBACK=_fallback_config(
                fallback_condition,
            ),
        ),
    )

    taxi_driver_protocol.invalidate_caches()

    @mockserver.json_handler('/driver_tags/v1/drivers/match/profile')
    def mock_match_tags(request):
        if 'tags' in fail_requests:
            return mockserver.make_response('', 500)

        return {'tags': driver_tags}

    @mockserver.json_handler('/driver_ui_profile/v1/mode')
    def mock_mode_get(request):
        assert request.args['park_id'] == park_id
        assert request.args['driver_profile_id'] == driver_id
        expected_concern = 'urgent' if policy == 'invalidate' else 'cached'
        assert request.args['concern'] == expected_concern
        if 'ui' in fail_requests:
            return mockserver.make_response('', 500)

        return {
            'display_mode': 'test_orders',
            'display_profile': 'test_orders_courier',
        }

    args = f'db={park_id}&session={session}&driver_mode_policy={policy}'
    response = taxi_driver_protocol.get(
        f'driver/polling/state?{args}',
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.32 (555)',
        },
    )
    assert response.status_code == expected_code


@pytest.mark.now('2021-01-10T00:00:00Z')
def test_experiments3_udid_kwarg(
        taxi_driver_protocol,
        mockserver,
        driver_authorizer_service,
        driver_work_rules,
        experiments3,
):
    # first driver from db_unique_drivers.json
    driver_authorizer_service.set_session('777555', 'qwerty', '12345FFFF')
    experiments3.add_experiment(
        name='udid_experiment_to_check',
        consumers=['taximeter/driver_polling_state'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'unique_driver_id',
                        'arg_type': 'string',
                        # _id from db_unique_drivers.json
                        'value': '543eac8978f3c2a8d798362d',
                    },
                },
                'value': {'enabled': True},
            },
        ],
        default_value={'enabled': False},
    )
    taxi_driver_protocol.invalidate_caches()

    response = taxi_driver_protocol.get(
        'driver/polling/state',
        params={'db': '777555', 'session': 'qwerty'},
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.60 (1234)',
        },
    )

    assert response.status_code == 200

    response_exp3 = response.json()['typed_experiments']['items']
    assert response_exp3['udid_experiment_to_check'] == {'enabled': True}

    # test driver w/o unique_driver_id
    driver_authorizer_service.set_session('777', 'qwerty', 'Vasya')
    experiments3.add_experiment(
        name='udid_experiment_to_check_v2',
        consumers=['taximeter/driver_polling_state'],
        match={
            'predicate': {
                'type': 'not_null',
                'init': {'arg_name': 'unique_driver_id'},
            },
            'enabled': True,
        },
        clauses=[{'value': {'enabled': True}, 'predicate': {'type': 'true'}}],
        default_value={'enabled': False},
    )
    taxi_driver_protocol.invalidate_caches()

    response = taxi_driver_protocol.get(
        'driver/polling/state',
        params={'db': '777', 'session': 'qwerty'},
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.60 (1234)',
        },
    )

    response_exp3 = response.json()['typed_experiments']['items']
    assert 'udid_experiment_to_check_v2' not in response_exp3


@pytest.mark.parametrize(
    'disabled,balance_revision', [(True, 321), (False, 123)],
)
def test_last_payment_number_disabled_config(
        taxi_driver_protocol,
        config,
        driver_authorizer_service,
        disabled,
        balance_revision,
):
    config.set(DRIVER_PROTOCOL_LAST_PAYMENT_NUMBER_DISABLED=disabled)

    driver_authorizer_service.set_session(
        '1488', 's1', 'test_balance_revision',
    )

    response = taxi_driver_protocol.get(
        'driver/polling/state',
        params={'db': '1488', 'session': 's1'},
        headers={
            'Accept-Language': 'ru',
            'User-Agent': 'Taximeter 9.60 (1234)',
        },
    )
    taximeter_configs = response.json()['taximeter_configs']
    assert taximeter_configs['balance_revision'] == balance_revision
