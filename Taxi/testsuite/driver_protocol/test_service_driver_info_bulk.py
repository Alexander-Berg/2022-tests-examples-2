import pytest

from . import common

DMS_ACTIVITY_VALUES = {
    '543eac8978f3c2a8d798362d': 94,
    '543eac8f78f3c2a8d798363c': 97,
    '543eac8f78f3c2a8d7983007': 78,
    '543eac8f78f3c2a8d7983008': 9,
}


def test_bad_request(taxi_driver_protocol):
    response = taxi_driver_protocol.post('service/driver/info_bulk')
    assert response.status_code == 400

    response = taxi_driver_protocol.post(
        'service/driver/info_bulk', {'drivers': [{'db': '777', 'uuid': ''}]},
    )
    assert response.status_code == 400


def test_drivers_not_found(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/driver/info_bulk',
        {'drivers': [{'db': 'not-existing', 'uuid': 'not-existing'}]},
    )
    assert response.status_code == 200
    assert response.json() == {'karma_points': [{}]}


def test_empty_clid(taxi_driver_protocol):
    response = taxi_driver_protocol.post(
        'service/driver/info_bulk',
        {
            'drivers': [
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a008',
                    'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {'karma_points': [{}]}


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={
        '__default__': 17.4,
        'moscow': 23.2,
        'Москва': 100500,
        'spb': 20.2,
    },
    DRIVER_POINTS_WARN_RULES={
        '__default__': 33.6,
        'moscow': 41.5,
        'Москва': 100500,
        'spb': 39.5,
    },
    EXTRA_EXAMS_BY_ZONE={
        'moscow': {'child_tariff': ['kids'], 'vip': ['business']},
    },
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_bulk_correct_karma_points(
        taxi_driver_protocol,
        mockserver,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/driver_trackstory/position')
    # driver position is in "moscow" zone. Thresholds should correspond
    # "moscow" zone, regardless of taxi_city
    def get_position(request):
        return {
            'position': {
                'direction': 328,
                'lat': 55.75,
                'lon': 37.6,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }

    response = taxi_driver_protocol.post(
        'service/driver/info_bulk',
        {
            'drivers': [
                {
                    'db': '16de978d526e40c0bf91e847245af741',
                    'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
                },
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a64f',
                    'uuid': '47c61fe50b264122ab70bc43f617f92a',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'karma_points': [
            {
                'unique_driver_id': '543eac8978f3c2a8d798362d',
                'value': dms_context.pick_karma_points(94.0, 95.1),
                'taxi_city': 'Москва',
                'disable_threshold': 23.2,
                'warn_threshold': 41.5,
            },
            {
                'unique_driver_id': '543eac8f78f3c2a8d798363c',
                'value': dms_context.pick_karma_points(97.0, 98.0),
                'taxi_city': 'Санкт-Петербург',
                'disable_threshold': 23.2,
                'warn_threshold': 41.5,
            },
        ],
    }


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={'__default__': 17.4, 'Москва': 23.2},
    DRIVER_POINTS_WARN_RULES={'__default__': 33.6, 'Москва': 41.5},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_bulk_correct_karma_points_spb(
        taxi_driver_protocol,
        mockserver,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/driver_trackstory/position')
    def get_position(request):
        return {
            'position': {
                'direction': 328,
                'lat': 55.75,
                'lon': 37.6,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }

    # Driver position is in "moscow" zone, which is absent in config.
    response = taxi_driver_protocol.post(
        'service/driver/info_bulk',
        {
            'drivers': [
                {
                    'db': '16de978d526e40c0bf91e847245af741',
                    'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
                },
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a64f',
                    'uuid': '47c61fe50b264122ab70bc43f617f92a',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'karma_points': [
            {  # Moscow driver. Thresholds are defined by taxi_city
                'unique_driver_id': '543eac8978f3c2a8d798362d',
                'disable_threshold': 23.2,
                'taxi_city': 'Москва',
                'value': dms_context.pick_karma_points(94.0, 95.1),
                'warn_threshold': 41.5,
            },
            {  # No info about "Санкт-Петербург" in config.
                # Thresholds are set by __default__.
                'unique_driver_id': '543eac8f78f3c2a8d798363c',
                'value': dms_context.pick_karma_points(97.0, 98.0),
                'taxi_city': 'Санкт-Петербург',
                'disable_threshold': 17.4,
                'warn_threshold': 33.6,
            },
        ],
    }


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={'__default__': 17.4},
    DRIVER_POINTS_WARN_RULES={'__default__': 33.6},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_bulk_correct_karma_points_unknown(
        taxi_driver_protocol,
        mockserver,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/driver_trackstory/position')
    def get_position(request):
        return {
            'position': {
                'direction': 328,
                'lat': 55.75,
                'lon': 37.6,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }

    response = taxi_driver_protocol.post(
        'service/driver/info_bulk',
        {
            'drivers': [
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a64f',
                    'uuid': '47c61fe50b264122ab70bc43f617f92a',
                },
                {
                    'db': '16de978d526e40c0bf91e847245af741',
                    'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'karma_points': [
            {
                'unique_driver_id': '543eac8f78f3c2a8d798363c',
                'value': dms_context.pick_karma_points(97, 98.0),
                'taxi_city': 'Санкт-Петербург',
                'disable_threshold': 17.4,
                'warn_threshold': 33.6,
            },
            {
                'unique_driver_id': '543eac8978f3c2a8d798362d',
                'disable_threshold': 17.4,
                'taxi_city': 'Москва',
                'value': dms_context.pick_karma_points(94, 95.1),
                'warn_threshold': 33.6,
            },
        ],
    }


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={'__default__': 17.4, 'Москва': 23.2},
    DRIVER_POINTS_WARN_RULES={'__default__': 33.6, 'Москва': 41.5},
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_bulk_correct_disabled_karma_points(
        taxi_driver_protocol,
        mockserver,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/driver_trackstory/position')
    def get_position(request):
        return {
            'position': {
                'direction': 328,
                'lat': 55.75,
                'lon': 37.6,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }

    response = taxi_driver_protocol.post(
        'service/driver/info_bulk',
        {
            'drivers': [
                {
                    'db': '16de978d526e40c0bf91e847245af741',
                    'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
                },
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a64f',
                    'uuid': '47c61fe50b264122ab70bc43f617f92a',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'karma_points': [
            {
                'unique_driver_id': '543eac8978f3c2a8d798362d',
                'disable_threshold': 23.2,
                'taxi_city': 'Москва',
                'value': dms_context.pick_karma_points(94, 95.1),
                'warn_threshold': 41.5,
            },
            {
                'unique_driver_id': '543eac8f78f3c2a8d798363c',
                'disable_threshold': 17.4,
                'taxi_city': 'Санкт-Петербург',
                'value': dms_context.pick_karma_points(97, 98.0),
                'warn_threshold': 33.6,
            },
        ],
    }


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={'__default__': 17.4, 'Москва': 23.2},
    DRIVER_POINTS_WARN_RULES={'__default__': 33.6, 'Москва': 41.5},
)
@common.dms_decorator(driver_points_values=[None], fallback_activity_value=13)
def test_absent_karma_points(
        taxi_driver_protocol,
        mockserver,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/driver_trackstory/position')
    def get_position(request):
        return {
            'position': {
                'direction': 328,
                'lat': 55.75,
                'lon': 37.6,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }

    response = taxi_driver_protocol.post(
        'service/driver/info_bulk',
        {
            'drivers': [
                {
                    'db': '16de978d526e40c0bf91e847245af741',
                    'uuid': '264ef3e6786c4d9bb7627c831b035ead',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'karma_points': [
            {
                'disable_threshold': 23.2,
                'taxi_city': 'Москва',
                'unique_driver_id': '5a21222bd23ea6c588c8efb2',
                'value': dms_context.pick_karma_points(13, 13.0),
                'warn_threshold': 41.5,
            },
        ],
    }


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={'__default__': 17.4, 'Москва': 23.2},
    DRIVER_POINTS_WARN_RULES={'__default__': 33.6, 'Москва': 41.5},
)
def test_no_license_points(taxi_driver_protocol, mockserver, testpoint):
    @mockserver.json_handler('/driver_trackstory/position')
    def get_position(request):
        return {
            'position': {
                'direction': 328,
                'lat': 55.75,
                'lon': 37.6,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }

    response = taxi_driver_protocol.post(
        'service/driver/info_bulk',
        {
            'drivers': [
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a007',
                    'uuid': '2eaf04fe6dec4330a6f29a6a7701c459a',
                },
            ],
        },
    )
    assert response.status_code == 200
    assert response.json() == {'karma_points': [{}]}


@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_get_inactive_drivers(
        taxi_driver_protocol,
        mockserver,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/driver_trackstory/position')
    def get_position(request):
        return {
            'position': {
                'direction': 328,
                'lat': 55.75,
                'lon': 37.6,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }

    response = taxi_driver_protocol.post(
        'service/driver/info_bulk',
        {
            'drivers': [
                {
                    'db': '16de978d526e40c0bf91e847245af741',
                    'uuid': '2eaf04fe6dec4330a6f29a6a7701c459a',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'karma_points': [
            {
                'unique_driver_id': '543eac8978f3c2a8d798362d',
                'disable_threshold': 30.0,
                'taxi_city': 'Москва',
                'value': dms_context.pick_karma_points(94, 95.1),
                'warn_threshold': 60.0,
            },
        ],
    }


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={
        '__default__': 17.4,
        'spb': 40,
        'Москва': 23.2,
        'Санкт-Петербург': 20.5,
    },
    DRIVER_POINTS_WARN_RULES={
        '__default__': 33.6,
        'spb': 60,
        'Москва': 41.5,
        'Санкт-Петербург': 42.2,
    },
    DRIVER_INFO_BULK_THREADS_LIMIT=2,
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_colisions(
        taxi_driver_protocol,
        mockserver,
        testpoint,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/driver_trackstory/position')
    def get_position(request):
        return {
            'position': {
                'direction': 328,
                'lat': 55.75,
                'lon': 37.6,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }

    response = taxi_driver_protocol.post(
        'service/driver/info_bulk',
        {
            'drivers': [
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a64f',
                    'uuid': '47c61fe50b264122ab70bc43f617f007',
                },
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a007',
                    'uuid': '47c61fe50b264122ab70bc43f617f007',
                },
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a64f',
                    'uuid': '47c61fe50b264122ab70bc43f617f007',
                },
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a007',
                    'uuid': '47c61fe50b264122ab70bc43f617f007',
                },
            ],
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json == {
        'karma_points': [
            {
                'unique_driver_id': '543eac8f78f3c2a8d7983007',
                'disable_threshold': 20.5,
                'taxi_city': 'Санкт-Петербург',
                'value': dms_context.pick_karma_points(78, 77.0),
                'warn_threshold': 42.2,
            },
            {
                'unique_driver_id': '543eac8f78f3c2a8d7983007',
                'disable_threshold': 17.4,
                'taxi_city': 'Сасово',
                'value': dms_context.pick_karma_points(78, 77.0),
                'warn_threshold': 33.6,
            },
            {
                'unique_driver_id': '543eac8f78f3c2a8d7983007',
                'disable_threshold': 20.5,
                'taxi_city': 'Санкт-Петербург',
                'value': dms_context.pick_karma_points(78, 77.0),
                'warn_threshold': 42.2,
            },
            {
                'unique_driver_id': '543eac8f78f3c2a8d7983007',
                'disable_threshold': 17.4,
                'taxi_city': 'Сасово',
                'value': dms_context.pick_karma_points(78, 77.0),
                'warn_threshold': 33.6,
            },
        ],
    }


@pytest.mark.config(
    DRIVER_POINTS_MIN_RULES={
        '__default__': 17.4,
        'spb': 40,
        'Москва': 23.2,
        'Санкт-Петербург': 20.5,
    },
    DRIVER_POINTS_WARN_RULES={
        '__default__': 33.6,
        'spb': 60,
        'Москва': 41.5,
        'Санкт-Петербург': 42.2,
    },
    DRIVER_INFO_BULK_THREADS_LIMIT=1,
)
@common.dms_decorator(driver_points_values=DMS_ACTIVITY_VALUES)
def test_query(
        taxi_driver_protocol,
        mockserver,
        testpoint,
        config,
        dms_fixture,
        dms_context,
        use_dms_driver_points,
):
    @mockserver.json_handler('/driver_trackstory/position')
    def get_position(request):
        return {
            'position': {
                'direction': 328,
                'lat': 55.75,
                'lon': 37.6,
                'speed': 30,
                'timestamp': 1502366306,
            },
            'type': 'raw',
        }

    response = taxi_driver_protocol.post(
        'service/driver/info_bulk',
        {
            'drivers': [
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a64f',
                    'uuid': '47c61fe50b264122ab70bc43f617f007',
                },
                {
                    'db': 'dbf0d2bb16d9492798ad3e2a3cc0a007',
                    'uuid': '47c61fe50b264122ab70bc43f617f008',
                },
            ],
        },
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json == {
        'karma_points': [
            {
                'unique_driver_id': '543eac8f78f3c2a8d7983007',
                'disable_threshold': 20.5,
                'taxi_city': 'Санкт-Петербург',
                'value': dms_context.pick_karma_points(78, 77.0),
                'warn_threshold': 42.2,
            },
            {
                'unique_driver_id': '543eac8f78f3c2a8d7983008',
                'disable_threshold': 17.4,
                'taxi_city': 'Сасово',
                'value': dms_context.pick_karma_points(9, 8.0),
                'warn_threshold': 33.6,
            },
        ],
    }
