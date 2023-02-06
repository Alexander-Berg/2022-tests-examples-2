import pytest

from . import common


DMS_ACTIVITY_VALUES = {
    '543eac8978f3c2a8d798362d': 94,
    '543eac8f78f3c2a8d798363c': 97,
}


class TrackerContext:
    def __init__(self):
        self.direction = 328
        self.lat = 55.75
        self.lon = 37.6
        self.speed = 30
        self.timestamp = 1502366306

    def set_position(self, direction, lat, lon, speed, timestamp):
        self.direction = direction
        self.lat = lat
        self.lon = lon
        self.speed = speed
        self.timestamp = timestamp


@pytest.fixture
def tracker_server(mockserver):
    tracker_context = TrackerContext()

    @mockserver.json_handler('/tracker/position')
    def get_position(request):
        return {
            'direction': tracker_context.direction,
            'lat': tracker_context.lat,
            'lon': tracker_context.lon,
            'speed': tracker_context.speed,
            'timestamp': tracker_context.timestamp,
        }

    return tracker_context


def test_bad_request(taxi_driver_protocol):
    response = taxi_driver_protocol.post('service/driver/info')
    assert response.status_code == 400

    response = taxi_driver_protocol.post(
        'service/driver/info', params={'db': '777', 'uuid': ''},
    )
    assert response.status_code == 400


def test_driver_not_found(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={'db': 'not-existing', 'uuid': 'not-existing'},
    )
    assert response.status_code == 404


@pytest.mark.translations(
    taximeter_messages={
        'driverinfo.tariff_available': {
            'ru': 'Тариф доступен.',
            'en': 'Tariff available.',
        },
        'driverinfo.tariff_unavailable': {
            'ru': 'Тариф недоступен.',
            'en': 'Tariff unavailable.',
        },
        'driverinfo.tariff_blocked': {
            'ru': 'Тариф заблокирован.',
            'en': 'Tariff is blocked.',
        },
        'driverinfo.tariff_need_support': {
            'ru': 'Обратитесь в техническую поддержку.',
            'en': 'Need support.',
        },
        'driverinfo.tariff_need_exam': {
            'ru': 'Необходимо сдать экзамен.',
            'en': 'Need exam.',
        },
        'driverinfo.tariff_need_extra_exam': {
            'ru': 'Необходимо сдать доп. экзамен.',
            'en': 'Need extra exam.',
        },
    },
)
@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={
        '__default__': 17.4,
        'moscow': 23.2,
        'Москва': 100500,
        'spb': 23.2,
    },
    DRIVER_POINTS_WARN_RULES={
        '__default__': 33.6,
        'moscow': 41.5,
        'Москва': 100500,
        'spb': 41.5,
    },
    EXTRA_EXAMS_BY_ZONE={
        'moscow': {'child_tariff': ['kids'], 'vip': ['business']},
    },
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_correct_karma_points(
        taxi_driver_protocol,
        tracker_server,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    resp_json['tariffs'] = sorted(
        resp_json['tariffs'], key=lambda x: x['tariff_name'],
    )
    assert resp_json == {
        'karma_points': {
            'unique_driver_id': '543eac8978f3c2a8d798362d',
            'value': dms_context.pick_karma_points(94, 95.1),
            'taxi_city': 'Москва',
            'disable_threshold': 23.2,
            'warn_threshold': 41.5,
        },
        'exam_score': 5.0,
        'tariffs': [
            {
                'request_exam_pass': True,
                'is_blocked': True,
                'tariff_name': 'child_tariff',
                'text_info': (
                    'Тариф недоступен. Необходимо сдать доп. экзамен.'
                ),
            },
            {
                'request_exam_pass': True,
                'is_blocked': True,
                'tariff_name': 'vip',
                'text_info': 'Тариф недоступен. Необходимо сдать экзамен.',
            },
        ],
    }

    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={
            'db': 'dbf0d2bb16d9492798ad3e2a3cc0a64f',
            'uuid': '47c61fe50b264122ab70bc43f617f92a',
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    resp_json['tariffs'] = sorted(
        resp_json['tariffs'], key=lambda x: x['tariff_name'],
    )

    assert resp_json == {
        'karma_points': {
            'unique_driver_id': '543eac8f78f3c2a8d798363c',
            'value': dms_context.pick_karma_points(97, 98.0),
            'taxi_city': 'Санкт-Петербург',
            'disable_threshold': 23.2,
            'warn_threshold': 41.5,
        },
        'exam_score': 5.0,
        'exam_created': '2017-12-05T01:01:01.000000Z',
        'tariffs': [
            {
                'request_exam_pass': True,
                'is_blocked': True,
                'tariff_name': 'child_tariff',
                'text_info': 'Тариф недоступен. Необходимо сдать экзамен.',
            },
            {
                'request_exam_pass': True,
                'is_blocked': True,
                'tariff_name': 'vip',
                'text_info': 'Тариф недоступен. Необходимо сдать экзамен.',
            },
        ],
    }


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={'__default__': 17.4, 'Москва': 23.2},
    DRIVER_POINTS_WARN_RULES={'__default__': 33.6, 'Москва': 41.5},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_correct_karma_points_spb(
        taxi_driver_protocol,
        tracker_server,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
        },
    )
    assert response.status_code == 200
    assert response.json() == {  # Moscow driver
        'karma_points': {
            'unique_driver_id': '543eac8978f3c2a8d798362d',
            'disable_threshold': 23.2,
            'taxi_city': 'Москва',
            'value': dms_context.pick_karma_points(94, 95.1),
            'warn_threshold': 41.5,
        },
        'exam_score': 5.0,
    }

    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={
            'db': 'dbf0d2bb16d9492798ad3e2a3cc0a64f',
            'uuid': '47c61fe50b264122ab70bc43f617f92a',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'karma_points': {
            'unique_driver_id': '543eac8f78f3c2a8d798363c',
            'value': dms_context.pick_karma_points(97, 98.0),
            'taxi_city': 'Санкт-Петербург',
            'disable_threshold': 17.4,
            'warn_threshold': 33.6,
        },
        'exam_score': 5.0,
        'exam_created': '2017-12-05T01:01:01.000000Z',
    }


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={'__default__': 17.4},
    DRIVER_POINTS_WARN_RULES={'__default__': 33.6},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_correct_karma_points_unknown(
        taxi_driver_protocol,
        tracker_server,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    # Should not find geoarea in here
    tracker_server.set_position(328, 42.8, 44.9985, 30, 1502366306)

    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
        },
    )
    assert response.status_code == 200
    assert response.json() == {  # Moscow driver
        'karma_points': {
            'unique_driver_id': '543eac8978f3c2a8d798362d',
            'disable_threshold': 17.4,
            'taxi_city': 'Москва',
            'value': dms_context.pick_karma_points(94, 95.1),
            'warn_threshold': 33.6,
        },
        'exam_score': 5.0,
    }

    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={
            'db': 'dbf0d2bb16d9492798ad3e2a3cc0a64f',
            'uuid': '47c61fe50b264122ab70bc43f617f92a',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'karma_points': {
            'unique_driver_id': '543eac8f78f3c2a8d798363c',
            'value': dms_context.pick_karma_points(97, 98.0),
            'taxi_city': 'Санкт-Петербург',
            'disable_threshold': 17.4,
            'warn_threshold': 33.6,
        },
        'exam_score': 5.0,
        'exam_created': '2017-12-05T01:01:01.000000Z',
    }


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={'__default__': 17.4, 'Москва': 23.2},
    DRIVER_POINTS_WARN_RULES={'__default__': 33.6, 'Москва': 41.5},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_correct_disabled_karma_points(
        taxi_driver_protocol,
        tracker_server,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'karma_points': {
            'unique_driver_id': '543eac8978f3c2a8d798362d',
            'disable_threshold': 23.2,
            'taxi_city': 'Москва',
            'value': dms_context.pick_karma_points(94, 95.1),
            'warn_threshold': 41.5,
        },
        'exam_score': 5.0,
    }

    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={
            'db': 'dbf0d2bb16d9492798ad3e2a3cc0a64f',
            'uuid': '47c61fe50b264122ab70bc43f617f92a',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'karma_points': {
            'unique_driver_id': '543eac8f78f3c2a8d798363c',
            'disable_threshold': 17.4,
            'taxi_city': 'Санкт-Петербург',
            'value': dms_context.pick_karma_points(97, 98.0),
            'warn_threshold': 33.6,
        },
        'exam_score': 5.0,
        'exam_created': '2017-12-05T01:01:01.000000Z',
    }


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={'__default__': 17.4, 'Москва': 23.2},
    DRIVER_POINTS_WARN_RULES={'__default__': 33.6, 'Москва': 41.5},
)
def test_absent_karma_points(taxi_driver_protocol, tracker_server):
    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'uuid': '264ef3e6786c4d9bb7627c831b035ead',
        },
    )
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.translations(
    taximeter_messages={
        'driverinfo.tariff_available': {
            'ru': 'Тариф доступен.',
            'en': 'Tariff available.',
        },
        'driverinfo.tariff_unavailable': {
            'ru': 'Тариф недоступен.',
            'en': 'Tariff unavailable.',
        },
        'driverinfo.tariff_blocked': {
            'ru': 'Тариф заблокирован.',
            'en': 'Tariff is blocked.',
        },
        'driverinfo.tariff_need_support': {
            'ru': 'Обратитесь в техническую поддержку.',
            'en': 'Need support.',
        },
        'driverinfo.tariff_need_exam': {
            'ru': 'Необходимо сдать экзамен.',
            'en': 'Need exam.',
        },
        'driverinfo.tariff_need_extra_exam': {
            'ru': 'Необходимо сдать доп. экзамен.',
            'en': 'Need extra exam.',
        },
        'driverinfo.tag_bad_car_reason': {
            'ru': 'Плохая машина.',
            'en': 'Bad car.',
        },
        'driverinfo.tag_dirty_car_reason': {
            'ru': 'Грязная машина.',
            'en': 'Dirty car.',
        },
        'driverinfo.tag_dirty_car_action': {
            'ru': 'Помойте машину.',
            'en': 'Wash car.',
        },
    },
)
@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={'__default__': 17.4, 'Москва': 23.2},
    DRIVER_POINTS_WARN_RULES={'__default__': 33.6, 'Москва': 41.5},
    EXTRA_EXAMS_BY_ZONE={
        '__default__': {'econom': [], 'comfort': []},
        'moscow': {
            'child_tariff': ['kids'],
            'econom': [],
            'vip': ['business', 'kids'],
            'business': ['comfort', 'business', 'kids'],
        },
    },
    EXTRA_EXAMS_INFO={
        'kids': {
            'description': 'Допуск к Детскому тарифу',
            'permission': ['child_tariff'],
            'requires': [],
        },
    },
    DISPATCH_SETTINGS_BACKEND_CPP_CACHE_UPDATE_ENABLED=True,
    DRIVER_INFO_FOR_BLOCKING_TAGS={
        'bad_car_tag': {'reason': 'driverinfo.tag_bad_car_reason'},
        'dirty_car_tag': {
            'reason': 'driverinfo.tag_dirty_car_reason',
            'action': 'driverinfo.tag_dirty_car_action',
        },
        'non_translation_tag1': {
            'reason': 'driverinfo.tag_non_translation_reason',
        },
        'non_translation_tag2': {
            'reason': 'driverinfo.tag_non_translation_reason',
        },
    },
)
@pytest.mark.parametrize(
    'uuid,entity_tags,expected_response',
    [
        (
            '2eaf04fe6dec4330a6f29a6a7701c459',
            ['bad_car_tag', 'salt_tag'],
            'expected_response1.json',
        ),
        (
            '2eaf04fe6dec4330a6f29a6a7701c450',
            ['dirty_car_tag'],
            'expected_response2.json',
        ),
        (
            '2eaf04fe6dec4330a6f29a6a7701c451',
            ['non_translation_tag1', 'non_translation_tag2', 'non_key_tag'],
            'expected_response3.json',
        ),
    ],
)
@pytest.mark.filldb(dbdrivers='locales')
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_driver_tariff_info(
        taxi_driver_protocol,
        driver_tags_mocks,
        tracker_server,
        load_json,
        mockserver,
        uuid,
        entity_tags,
        expected_response,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/dispatch_settings/v2/categories/fetch')
    def _mock_category_fetch(_):
        return {
            'categories': [
                {'zone_name': '__default__', 'tariff_names': ['__default__']},
            ],
            'groups': [],
        }

    @mockserver.json_handler('/dispatch_settings/v1/settings/fetch')
    def _mock_dispatch_settings(request):
        return load_json('dispatch_settings.json')

    DBID = '16de978d526e40c0bf91e847245af741'

    driver_tags_mocks.set_tags_info(dbid=DBID, uuid=uuid, tags=entity_tags)

    response = taxi_driver_protocol.post(
        'service/driver/info', params={'db': DBID, 'uuid': uuid},
    )
    assert response.status_code == 200
    resp_json = response.json()
    resp_json['tariffs'] = sorted(
        resp_json['tariffs'], key=lambda x: x['tariff_name'],
    )
    assert resp_json == dms_context.mod_expected_karma_points(
        load_json('response/' + expected_response), 94,
    )


@pytest.mark.translations(
    taximeter_messages={
        'driverinfo.tariff_available': {
            'ru': 'Тариф доступен.',
            'en': 'Tariff available.',
        },
        'driverinfo.tariff_unavailable': {
            'ru': 'Тариф недоступен.',
            'en': 'Tariff unavailable.',
        },
        'driverinfo.tariff_blocked': {
            'ru': 'Тариф заблокирован.',
            'en': 'Tariff is blocked.',
        },
        'driverinfo.tariff_need_support': {
            'ru': 'Обратитесь в техническую поддержку.',
            'en': 'Need support.',
        },
        'driverinfo.tariff_need_exam': {
            'ru': 'Необходимо сдать экзамен.',
            'en': 'Need exam.',
        },
        'driverinfo.tariff_need_extra_exam': {
            'ru': 'Необходимо сдать доп. экзамен.',
            'en': 'Need extra exam.',
        },
    },
)
@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={'__default__': 17.4, 'Москва': 23.2},
    DRIVER_POINTS_WARN_RULES={'__default__': 33.6, 'Москва': 41.5},
    EXTRA_EXAMS_BY_ZONE={'moscow': {'child_tariff': ['kids']}},
    EXTRA_EXAMS_INFO={
        'kids': {
            'description': 'Допуск к Детскому тарифу',
            'permission': ['child_tariff'],
            'requires': [],
        },
    },
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_driver_tariff_info_extra_exam(
        taxi_driver_protocol,
        tracker_server,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'karma_points': {
            'unique_driver_id': '543eac8978f3c2a8d798362d',
            'value': dms_context.pick_karma_points(94, 95.1),
            'taxi_city': 'Москва',
            'disable_threshold': 23.2,
            'warn_threshold': 41.5,
        },
        'exam_score': 5.0,
        'tariffs': [
            {
                'request_exam_pass': True,
                'is_blocked': False,
                'tariff_name': 'child_tariff',
                'text_info': (
                    'Тариф доступен. ' 'Необходимо сдать ' 'экзамен.'
                ),
            },
        ],
    }


@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_get_inactive_drivers(
        taxi_driver_protocol,
        tracker_server,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    response = taxi_driver_protocol.post(
        'service/driver/info',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'uuid': '2eaf04fe6dec4330a6f29a6a7701c459a',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'karma_points': {
            'unique_driver_id': '543eac8978f3c2a8d798362d',
            'disable_threshold': 30.0,
            'taxi_city': 'Москва',
            'value': dms_context.pick_karma_points(94, 95.1),
            'warn_threshold': 60.0,
        },
        'exam_score': 5.0,
    }
