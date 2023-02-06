import bson
import pytest

from protocol.totw.test_common import check_points_statuses
from protocol.totw.test_common import update_destinations_statuses
from replica_dbusers_switch_parametrize import (
    PROTOCOL_SWITCH_TO_REPLICA_DBUSERS,
)


@pytest.fixture(name='driver_ratings_v2')
def _driver_ratings_v2(mockserver):
    @mockserver.json_handler('/driver-ratings/v2/driver/rating')
    def get_rating(request):
        return {'unique_driver_id': 'driver_id', 'rating': '4.877'}


def test_rating_output(taxi_protocol, tracker, now, db, driver_ratings_v2):
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200

    response_body = response.json()
    assert 'driver' in response_body
    assert 'rating' in response_body['driver']
    assert response_body['driver']['rating'] == '4.87'
    for route in response_body['request']['route']:
        assert 'extra_data' in route
        extra_data = route['extra_data']
        assert extra_data['doorphone_number'] == route['doorphone_number']
        assert extra_data['floor'] == route['floor_number']
        assert extra_data['apartment'] == route['quarters_number']


@pytest.mark.config(SHAREDROUTE_MINIMAL_PRESENTATION_RATING=4.88)
def test_rating_output_with_lower_bound(
        taxi_protocol, tracker, now, db, driver_ratings_v2,
):
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200

    response_body = response.json()
    assert 'driver' in response_body
    assert 'rating' in response_body['driver']
    assert response_body['driver']['rating'] == '4.88'


@pytest.mark.parametrize(
    'locale,db_carrier,expected_response_park,'
    'expected_response_partner, key',
    [
        (
            'ru',
            {
                'name': 'ООО Перевозчик',
                'registration_number': 'abcdereqqewqwe',
                'address': '3-я улица Строителей, 25',
                'work_hours': '8-16',
            },
            {
                'name': 'ООО Перевозчик',
                'legal_address': '3-я улица Строителей, 25',
                'ogrn': 'ОГРН: abcdereqqewqwe',
                'working_hours': 'Часы работы: 8-16',
            },
            {
                'name': 'Сити',
                'legal_address': 'Street',
                'ogrn': 'ОГРН: 1233231231',
            },
            '7071c41bba3407914e2b8db8fe3e5be4',
        ),
        (
            'en',
            {
                'name': 'ООО Перевозчик',
                'registration_number': '',
                'address': '',
                'work_hours': '8-16',
            },
            {'name': 'OOO Perevozcik', 'working_hours': 'Hours: 8-16'},
            {
                'name': 'Siti',
                'legal_address': 'Street',
                'ogrn': 'OGRN: 1233231231',
            },
            '7071c41bba3407914e2b8db8fe3e5be4',
        ),
        (
            'ru',
            None,
            {
                'name': 'Сити',
                'legal_address': 'Street',
                'ogrn': 'ОГРН: 1233231231',
            },
            {
                'name': 'Сити',
                'legal_address': 'Street',
                'ogrn': 'ОГРН: 1233231231',
            },
            'key_to_no_carrier_order_proc',
        ),
    ],
)
@pytest.mark.translations(
    client_messages={
        'taxiontheway.carrier.name': {'ru': '%(name)s'},
        'taxiontheway.carrier.address': {'ru': '%(address)s'},
        'taxiontheway.carrier.ogrn': {
            'ru': 'ОГРН: %(reg_number)s',
            'en': 'OGRN: %(reg_number)s',
        },
        'taxiontheway.carrier.working_hours': {
            'ru': 'Часы работы: %(working_hours)s',
            'en': 'Hours: %(working_hours)s',
        },
    },
)
def test_partner_park(
        taxi_protocol,
        tracker,
        now,
        db,
        locale,
        db_carrier,
        expected_response_park,
        expected_response_partner,
        key,
):
    if db_carrier:
        db.order_proc.update(
            {'_id': '8c83b49edb274ce0992f337061047375'},
            {'$set': {'order.performer.carrier': db_carrier}},
        )
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': key}, headers={'Accept-Language': locale},
    )

    assert response.status_code == 200
    response_body = response.json()
    assert response_body['park'] == expected_response_park
    assert response_body['partner'] == expected_response_partner


@pytest.mark.filldb(countries='carrier_disabled')
@pytest.mark.translations(
    client_messages={
        'taxiontheway.carrier.name': {'ru': '%(name)s'},
        'taxiontheway.carrier.address': {'ru': '%(address)s'},
        'taxiontheway.carrier.ogrn': {
            'ru': 'ОГРН: %(reg_number)s',
            'en': 'OGRN: %(reg_number)s',
        },
        'taxiontheway.carrier.working_hours': {
            'ru': 'Часы работы: %(working_hours)s',
            'en': 'Hours: %(working_hours)s',
        },
    },
)
def test_countries_carrier_disabled(
        taxi_protocol, tracker, now, db, driver_ratings_v2,
):
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)
    response = taxi_protocol.post(
        '3.0/sharedroute',
        {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    response_body = response.json()
    expected_park = {
        'name': 'Сити',
        'legal_address': 'Street',
        'ogrn': 'ОГРН: 1233231231',
    }
    assert 'partner' not in response_body
    assert response_body['park'] == expected_park


@pytest.mark.filldb(tariff_settings='disable_legal_entities')
@pytest.mark.translations(
    client_messages={
        'taxiontheway.carrier.name': {'ru': '%(name)s'},
        'taxiontheway.carrier.address': {'ru': '%(address)s'},
        'taxiontheway.carrier.ogrn': {
            'ru': 'ОГРН: %(reg_number)s',
            'en': 'OGRN: %(reg_number)s',
        },
        'taxiontheway.carrier.working_hours': {
            'ru': 'Часы работы: %(working_hours)s',
            'en': 'Hours: %(working_hours)s',
        },
    },
)
def test_legal_entities_disabled(
        taxi_protocol, tracker, now, db, driver_ratings_v2,
):
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)
    response = taxi_protocol.post(
        '3.0/sharedroute',
        {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    response_body = response.json()
    assert 'park' not in response_body
    assert 'partner' not in response_body


def test_point_passed_status_in_response(
        taxi_protocol, tracker, now, db, driver_ratings_v2,
):
    destinations_statuses = [False, False]
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)
    order_id = '8c83b49edb274ce0992f337061047375'

    update_destinations_statuses(db, order_id, destinations_statuses)
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    response_body = response.json()
    check_points_statuses(response_body, destinations_statuses)

    new_destinations_statuses = [True, False]
    update_destinations_statuses(db, order_id, new_destinations_statuses)
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    response_body = response.json()
    check_points_statuses(response_body, new_destinations_statuses)


@pytest.mark.config(SHARED_ROUTE_MAP_ENABLED=True)
def test_requested_route_image_url_in_response(
        taxi_protocol, driver_ratings_v2,
):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    response_body = response.json()
    assert 'requested_route_image_url' in response_body
    assert response_body['requested_route_image_url'] == (
        'https://tc.mobile.yandex.net/get-map/1.x/?l=map'
        '&size=400,400&cr=0&lg=0&scale=1.4&lang=en'
        '&pt=37.589180,55.733411,comma_solid_red'
        '~49.277265,53.500852,trackpoint'
        '~49.356954,53.540618,comma_solid_blue'
        '&pl=c:3C3C3CFF,w:6,37.589180,55.733411,49.277265,53.500852,'
        '49.356954,53.540618'
        '&bbox=36.647758,53.322247~50.298376,56.179923'
    )


@pytest.mark.config(SHARED_ROUTE_MAP_ENABLED=False)
def test_requested_route_image_url_not_in_response(
        taxi_protocol, driver_ratings_v2,
):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    response_body = response.json()
    assert 'requested_route_image_url' not in response_body


@pytest.mark.config(
    SHARED_ROUTE_CALL_MODE_ALLOWED_CATEGORIES={
        'enabled': True,
        'allowed_categories': ['econom'],
    },
)
def test_shared_route_driver_call_mode_on_demand(
        taxi_protocol, driver_ratings_v2,
):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    assert response.json()['driver']['call_mode'] == 'on_demand'


@pytest.mark.config(
    SHARED_ROUTE_CALL_MODE_ALLOWED_CATEGORIES={
        'enabled': True,
        'allowed_categories': [],
    },
)
def test_shared_route_driver_call_mode_disabled(
        taxi_protocol, driver_ratings_v2,
):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    assert response.json()['driver']['call_mode'] == 'disabled'


@pytest.mark.config(
    SHARED_ROUTE_CALL_MODE_ALLOWED_CATEGORIES={
        'enabled': True,
        'allowed_categories': [],
    },
    SHARED_ROUTE_CALL_MODE_ALLOWED_APPLICATIONS=['iphone'],
)
def test_shared_route_driver_call_mode_enabled_by_app(
        taxi_protocol, driver_ratings_v2,
):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    assert response.json()['driver']['call_mode'] == 'on_demand'


@pytest.mark.config(
    SHARED_ROUTE_CALL_MODE_ALLOWED_CATEGORIES={
        'enabled': True,
        'allowed_categories': [],
    },
)
def test_shared_route_driver_call_mode_enabled_for_other(
        taxi_protocol, db, driver_ratings_v2,
):
    db.order_proc.update(
        {'_id': '8c83b49edb274ce0992f337061047375'},
        {
            '$set': {
                'order.request.extra_user_phone_id': bson.ObjectId(
                    '5714f45e98956f06baaae3d5',
                ),
            },
        },
    )

    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    assert response.json()['driver']['call_mode'] == 'on_demand'


@pytest.mark.config(SHARED_ROUTE_SHOW_TARIFF_CLASS=True)
def test_shared_route_tariff_class_enabled(taxi_protocol, driver_ratings_v2):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    assert response.json()['driver']['tariff_class'] == 'econom'


def test_shared_route_tariff_class_disabled(taxi_protocol, driver_ratings_v2):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    assert 'tariff_class' not in response.json()['driver']


@pytest.mark.config(
    CONTRACTOR_TRANSPORT_HIDE_SETTINGS={
        '__default__': {'number': False, 'model': False, 'color': False},
        'pedestrian': {'number': True, 'model': True, 'color': True},
    },
)
@pytest.mark.parametrize(
    ('hide_enabled',),
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                CONTRACTOR_TRANSPORT_HIDE_ENABLED={'sharedroute': True},
            ),
            id='hide enable',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                CONTRACTOR_TRANSPORT_HIDE_ENABLED={'sharedroute': False},
            ),
            id='hide disable',
        ),
    ],
)
def test_shared_route_hide_transport(
        taxi_protocol, driver_ratings_v2, hide_enabled,
):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    driver = response.json()['driver']
    if hide_enabled:
        assert not driver.get('plates')
        assert not driver.get('model')
        assert not driver.get('car_info_text')
    else:
        assert driver.get('plates') == 'С441ТК'
        assert driver.get('model') == 'BMW 7er'
        assert driver.get('car_info_text') == 'BMW 7er С441ТК'


def make_banner_config_mark(enabled=True):
    return pytest.mark.config(
        SHARED_ROUTE_BANNER_SETTINGS_BY_APPLICATION={
            'iphone': {
                'enabled': enabled,
                'title': 'test_banner_title',
                'subtitle': 'test_banner_subtitle',
            },
        },
    )


@pytest.mark.translations(
    client_messages={
        'test_banner_title': {'en': 'Test banner title'},
        'test_banner_subtitle': {'en': 'Test banner subtitle'},
    },
)
@pytest.mark.parametrize(
    'is_banner_enabled_for_app',
    [
        pytest.param(False, id='Empty config'),
        pytest.param(
            False, marks=make_banner_config_mark(enabled=False), id='Disabled',
        ),
        pytest.param(
            True, marks=make_banner_config_mark(enabled=True), id='Enabled',
        ),
    ],
)
def test_banner(taxi_protocol, driver_ratings_v2, is_banner_enabled_for_app):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    data = response.json()
    if is_banner_enabled_for_app:
        assert data['banner'] == {
            'title': 'Test banner title',
            'subtitle': 'Test banner subtitle',
        }
    else:
        assert 'banner' not in data


@pytest.mark.config(SHARED_ROUTE_PRICE_ENABLED_BY_APPLICATION=['iphone'])
def test_minimal_price_enabled(taxi_protocol, driver_ratings_v2):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['price_info'] == {
        'price': 69.99,
        'currency_symbol': '₽',
        'kind': 'minimal',
    }


@pytest.mark.config(SHARED_ROUTE_PREDICTION_PRICE_REASONS=['LONG_TRIP'])
@pytest.mark.config(SHARED_ROUTE_PRICE_ENABLED_BY_APPLICATION=['iphone'])
def test_prediction_price_enabled(taxi_protocol, driver_ratings_v2):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['price_info'] == {
        'price': 151.23,
        'currency_symbol': '₽',
        'kind': 'prediction',
    }


def test_price_disbled(taxi_protocol, driver_ratings_v2):
    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    data = response.json()
    assert 'price_info' not in data


@PROTOCOL_SWITCH_TO_REPLICA_DBUSERS
def test_read_user_from_secondary(
        taxi_protocol, tracker, now, db, testpoint, read_from_replica_dbusers,
):
    tracker.set_position('999012_a5709ce56c2740d9a536650f5390de0b', now, 1, 0)

    @testpoint('UserExperimentsHelper::GetById')
    def replica_dbusers_test_point(data):
        assert read_from_replica_dbusers == data['replica']

    response = taxi_protocol.post(
        '3.0/sharedroute', {'key': '7071c41bba3407914e2b8db8fe3e5be4'},
    )

    assert response.status_code == 200
    assert replica_dbusers_test_point.wait_call()
