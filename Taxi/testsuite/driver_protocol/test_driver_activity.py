import json

import pytest


@pytest.fixture
def geotracks_response_track3(mockserver):
    @mockserver.json_handler('/geotracks/gps-storage/get')
    def mock_geotracks_response(request):
        track = [
            {
                'timestamp': 1503844951,
                'bearing': 0,
                'point': [37.571051666666669, 55.720183333333338],
                'speed': 0,
            },
            {
                'timestamp': 1503845071,
                'bearing': 0,
                'point': [37.581051666666669, 55.730183333333338],
                'speed': 0,
            },
        ]
        return {
            'tracks': [
                {'req_id': 0, 'track': track},
                {'req_id': 1, 'track': track},
                {'req_id': 2, 'track': track},
                {'req_id': 3, 'track': track},
            ],
        }


def dm_response_prepare(body, event_descriptor_pkey='name'):
    return {
        'items': [
            {
                'id': '5cf62b5f629526419e1b58ed',
                'activity_value_change': -97,
                'timestamp': '2019-06-04T08:27:11.468000Z',
                'driver_id': '100500_2eaf04fe6dec4330a6f29a6a7701c459',
                'db_id': '16de978d526e40c0bf91e847245af741',
                'time_to_a': 301,
                'distance_to_a': 16698,
                'order_id': body.get('order_ids', [''])[0],
                'order_alias_id': body.get('alias_ids', [''])[0],
                'zone': 'moscow',
                'activity_value_before': 97,
                'event_type': 'order',
                'event_descriptor': {
                    event_descriptor_pkey: 'user_cancel',
                    'tags': None,
                },
                'dispatch_traits': {'distance': 'medium'},
            },
            {
                'id': '5cf62b5f629526419e1b58ea',
                'activity_value_change': -9,
                'timestamp': '2019-06-04T08:27:11.468000Z',
                'driver_id': '100500_2eaf04fe6dec4330a6f29a6a7701c459',
                'db_id': '16de978d526e40c0bf91e847245af741',
                'time_to_a': 1880,
                'distance_to_a': 16698,
                'order_id': body.get('order_ids', [''])[0],
                'order_alias_id': body.get('alias_ids', [''])[0],
                'zone': 'moscow',
                'activity_value_before': 97,
                'event_type': 'order',
                'event_descriptor': {
                    event_descriptor_pkey: 'unknown',
                    'tags': None,
                },
            },
            {
                'id': '5cf62b5f629526419e1b58eb',
                'activity_value_change': 10,
                'timestamp': '2019-06-04T08:27:11.468000Z',
                'driver_id': '100500_2eaf04fe6dec4330a6f29a6a7701c459',
                'db_id': '16de978d526e40c0bf91e847245af741',
                'time_to_a': 300,
                'distance_to_a': 16698,
                'order_id': body.get('order_ids', [''])[0],
                'order_alias_id': body.get('alias_ids', [''])[0],
                'zone': 'moscow',
                'activity_value_before': 97,
                'event_type': 'order',
                'event_descriptor': {
                    event_descriptor_pkey: 'complete',
                    'tags': ['lol'],
                },
                'dispatch_traits': {'distance': 'short'},
            },
            {
                'id': '5cf62b5f629526419e1b58eg',
                'activity_value_change': -7,
                'event_descriptor': {
                    event_descriptor_pkey: 'set_activity_manual',
                },
                'event_type': 'dm_service_manual',
                'order_alias_id': '',
                'order_id': '',
                'timestamp': '2019-06-04T08:27:12.468000Z',
                'zone': '',
            },
        ][: body.get('limit')],
    }


@pytest.fixture
def driver_metrics_mockserver(mockserver):
    @mockserver.json_handler('/driver_metrics/v1/activity/history/')
    def mock_driver_metrics_response(request):
        body = json.loads(list(request.form.items())[0][0])
        return dm_response_prepare(body, event_descriptor_pkey='name')


@pytest.mark.translations(
    taximeter_messages={
        'driveractivity.pass_ride': {'ru': 'пропуск', 'en': 'pass_ride'},
        'driveractivity.cancel_ride': {'ru': 'отмена', 'en': 'cancel_ride'},
        'driveractivity.complete_ride': {
            'ru': 'завершена',
            'en': 'complete_ride',
        },
        'driveractivity.activity_title': {
            'ru': 'активность',
            'en': 'activity_title',
        },
        'driveractivity.near_transfer': {
            'ru': 'близкая подача',
            'en': 'near_transfer',
        },
        'driveractivity.middle_transfer': {
            'ru': 'средняя подача',
            'en': 'middle_transfer',
        },
        'driveractivity.far_transfer': {
            'ru': 'далекая подача',
            'en': 'far_transfer',
        },
        'driveractivity.manual_activity_change': {
            'ru': 'корректировка',
            'en': 'manual_activity_change_title',
        },
        'driveractivity.event_any_order_title_template': {
            'ru': '%(time)s • %(distance)s',
            'en': '%(time)s • %(distance)s',
        },
        'driveractivity.event_any_order_comment_template': {
            'ru': '%(comment)s',
            'en': '%(comment)s',
        },
        'driveractivity.event_manual_activity_change_template': {
            'ru': '%(comment)s',
            'en': '%(comment)s',
        },
    },
    tariff={
        'round.few_meters': {'ru': '%(value).0f м', 'en': '%(value).0f m'},
        'round.kilometers': {'ru': '%(value).0f км', 'en': '%(value).0f km'},
        'round.minute': {'ru': '%(value).0f мин', 'en': '%(value).0f min'},
        'round.tens_minutes': {
            'ru': '%(value).0f мин',
            'en': '%(value).0f min',
        },
    },
)
@pytest.mark.config(
    DRIVER_EVENT_TITLE_TEMPLATES={
        '__default__': {
            '__default__': {
                'title_template': (
                    'driveractivity.event_any_order_title_template'
                ),
                'comment_template': (
                    'driveractivity.event_any_order_comment_template'
                ),
            },
        },
        'dm_service_manual': {
            'set_activity_manual': {
                'title_template': (
                    'driveractivity.event_manual_activity_change_template'
                ),
            },
        },
    },
)
@pytest.mark.now('2017-04-29T12:00:00+0300')
@pytest.mark.parametrize(
    'show_track, limit, no_dm_proxy_percents, dms_response_code',
    [
        (1, 4, 0, 200),
        (1, 4, 0, 200),
        (0, 3, 100, 200),
        (0, 3, 100, 200),
        (0, 3, 100, 429),
        (0, 3, 100, 429),
    ],
)
def test_driver_activity_base(
        taxi_driver_protocol,
        show_track,
        limit,
        mockserver,
        geotracks_response_track3,
        driver_authorizer_service,
        driver_metrics_mockserver,
        no_dm_proxy_percents,
        dms_context,
        dms_fixture,
        dms_response_code,
):
    dms_context.set_v1_activity_history_response(
        dm_response_prepare,
        response_code=dms_response_code,
        response_type=(
            'text/plain' if dms_response_code == 429 else 'application/json'
        ),
    )
    dms_context.set_no_proxy_activity_history_percents(no_dm_proxy_percents)
    taxi_driver_protocol.invalidate_caches()

    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af741',
        'test_session_id_123FFFF',
        '2eaf04fe6dec4330a6f29a6a7701c459',
    )
    response = taxi_driver_protocol.post(
        '/driver/activity',
        headers={'User-Agent': 'Taximeter 9.88'},
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'session': 'test_session_id_123FFFF',
            'newer_than': '2018-8-22T08:50:36+0023',
            'older_than': '2018-8-26T08:50:36+0023',
            'image_size': '800,400',
            'image_scale': '1.4',
            'show_track': show_track,
            'limit': limit,
        },
    )
    assert response.status_code == dms_response_code
    if dms_response_code != 200:
        return

    response_json = response.json()
    assert len(response_json['activity']) == limit
    if show_track == 1:
        assert response_json == {
            'activity': [
                {
                    'card': {
                        'items': [
                            {
                                'result': {'value': '-97'},
                                'subtitle': 'cancel_ride',
                                'title': 'activity_title',
                            },
                            {
                                'subtitle': 'middle_transfer',
                                'title': '6 min • 17 km',
                            },
                        ],
                    },
                    'date': '2019-06-04T08:27:11.468000Z',
                    'item': {
                        'result': {'comment': 'cancel_ride', 'value': '-97'},
                        'subtitle': 'middle_transfer',
                        'title': '6 min • 17 km',
                    },
                },
                {
                    'card': {
                        'items': [
                            {
                                'result': {'value': '-9'},
                                'title': 'activity_title',
                            },
                            {'title': '32 min • 17 km'},
                        ],
                    },
                    'date': '2019-06-04T08:27:11.468000Z',
                    'item': {
                        'result': {'value': '-9'},
                        'title': '32 min • 17 km',
                    },
                },
                {
                    'card': {
                        'items': [
                            {
                                'result': {'value': '+10'},
                                'subtitle': 'complete_ride',
                                'title': 'activity_title',
                            },
                            {
                                'subtitle': 'near_transfer',
                                'title': '5 min • 17 km',
                            },
                        ],
                    },
                    'date': '2019-06-04T08:27:11.468000Z',
                    'item': {
                        'result': {'comment': 'complete_ride', 'value': '+10'},
                        'subtitle': 'near_transfer',
                        'title': '5 min • 17 km',
                    },
                },
                {
                    'card': {
                        'items': [
                            {
                                'result': {'value': '-7'},
                                'subtitle': 'manual_activity_change_title',
                                'title': 'activity_title',
                            },
                            {'title': '1 min • 0 m'},
                        ],
                    },
                    'date': '2019-06-04T08:27:12.468000Z',
                    'item': {
                        'result': {'value': '-7'},
                        'title': 'manual_activity_change_title',
                    },
                },
            ],
            'last_items': True,
        }
    else:
        assert response_json['activity'][0]['card']
