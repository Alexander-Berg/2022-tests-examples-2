import pytest


REUSE_ACTIVITY_VERSION = '8.92'
CONFIG = {
    'TAXIMETER_VERSION_SETTINGS': {
        'current': '8.78',
        'disabled': [],
        'feature_support': {
            'activity_reuse_order_details': REUSE_ACTIVITY_VERSION,
        },
        'min': '8.78',
        'min_versions_cities': {},
    },
    'TAXIMETER_VERSION_SETTINGS_BY_BUILD': {
        '__default__': {
            'current': '8.78',
            'disabled': [],
            'feature_support': {
                'activity_reuse_order_details': REUSE_ACTIVITY_VERSION,
            },
            'min': '8.78',
        },
    },
    'DRIVER_ACTIVITY_UNIQUE_DRIVER_ID': True,
    'DRIVER_EVENTS_TO_SHOW_IN_ACTIVITY_HISTORY': {
        'dm_service_manual': {
            'set_activity_manual': 'driveractivity.manual_activity_change',
        },
        'multioffer_order': {
            'auto_reorder': 'driveractivity.cancel_ride',
            'complete': 'driveractivity.complete_ride',
            'offer_timeout': 'driveractivity.pass_ride',
            'park_cancel': 'driveractivity.cancel_ride',
            'park_fail': 'driveractivity.cancel_ride',
            'reject_auto_cancel': 'driveractivity.pass_ride',
            'reject_bad_position': 'driveractivity.pass_ride',
            'reject_manual': 'driveractivity.pass_ride',
            'reject_missing_tariff': 'driveractivity.pass_ride',
            'reject_seen_impossible': 'driveractivity.pass_ride',
            'reject_wrong_way': 'driveractivity.pass_ride',
            'seen_timeout': 'driveractivity.pass_ride',
            'user_cancel': 'driveractivity.cancel_ride',
        },
        'order': {
            'auto_reorder': 'driveractivity.cancel_ride',
            'complete': 'driveractivity.complete_ride',
            'offer_timeout': 'driveractivity.pass_ride',
            'park_cancel': 'driveractivity.cancel_ride',
            'park_fail': 'driveractivity.cancel_ride',
            'reject_auto_cancel': 'driveractivity.pass_ride',
            'reject_bad_position': 'driveractivity.pass_ride',
            'reject_manual': 'driveractivity.pass_ride',
            'reject_missing_tariff': 'driveractivity.pass_ride',
            'reject_seen_impossible': 'driveractivity.pass_ride',
            'reject_wrong_way': 'driveractivity.pass_ride',
            'seen_timeout': 'driveractivity.pass_ride',
            'user_cancel': 'driveractivity.cancel_ride',
        },
    },
    'DRIVER_EVENT_TITLE_TEMPLATES': {
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
}

TRANSLATIONS = {
    'taximeter_messages': {
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
        'driveractivity.today': {'ru': 'Сегодня', 'en': 'Today'},
        'driveractivity.yesterday': {'ru': 'Вчера', 'en': 'Yesterday'},
        'driveractivity.about_activity': {
            'ru': 'Подробнее об активности: ',
            'en': 'About activity: ',
        },
        'driveractivity.no_orders': {
            'ru': 'У вас не было заказов в течение последней недели',
            'en': 'You\'ve got no orders in last 7 days',
        },
        'driveractivity.event_any_order_title_template': {
            'ru': '%(time)s • %(distance)s',
            'en': '%(time)s • %(distance)s',
        },
        'driveractivity.event_any_order_comment_template': {
            'ru': '%(comment)s',
            'en': '%(comment)s',
        },
    },
    'notify': {
        'helpers.month_1_part': {'ru': 'Январь', 'en': 'January'},
        'helpers.month_2_part': {'ru': 'Февраль', 'en': 'February'},
        'helpers.month_5_part': {'ru': 'Мая', 'en': 'May'},
        'helpers.month_6_part': {'ru': 'Июня', 'en': 'June'},
    },
    'tariff': {
        'round.kilometers': {'ru': '%(value).0f км', 'en': '%(value).0f km'},
        'round.hundreds_meters': {
            'ru': '%(value).0f м',
            'en': '%(value).0f m',
        },
        'round.tens_minutes': {
            'ru': '%(value).0f мин',
            'en': '%(value).0f min',
        },
    },
}


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
                'activity_value_before': 97,
                'activity_value_change': -14,
                'db_id': '16de978d526e40c0bf91e847245af741',
                'dispatch_traits': {'distance': 'medium'},
                'distance_to_a': 1000,
                'driver_id': '999010_2eaf04fe6dec4330a6f29a6a7701c459',
                'event_descriptor': {
                    event_descriptor_pkey: 'user_cancel',
                    'tags': ['chained'],
                },
                'event_type': 'order',
                'id': '5cf62b5f629526419e1b58ed',
                'order_alias_id': 'alias_5',
                'order_id': 'id_5',
                'timestamp': '2019-06-04T08:27:11.468000Z',
                'time_to_a': 300,
                'zone': 'moscow',
            },
            {
                'activity_value_before': 97,
                'activity_value_change': -7,
                'db_id': '16de978d526e40c0bf91e847245af741',
                'dispatch_traits': {'distance': 'medium'},
                'distance_to_a': 1000,
                'driver_id': '999010_2eaf04fe6dec4330a6f29a6a7701c459',
                'event_descriptor': {
                    event_descriptor_pkey: 'park_cancel',
                    'tags': ['chained'],
                },
                'event_type': 'order',
                'id': '5cf62b5f629526419e1b58eu',
                'order_alias_id': 'alias_6',
                'order_id': '4',
                'time_to_a': 300,
                'timestamp': '2019-06-01T08:27:11.468000Z',
                'zone': 'moscow',
            },
            {
                'activity_value_before': 100,
                'activity_value_change': -3,
                'distance_to_a': 3000,
                'driver_id': '999010_2eaf04fe6dec4330a6f29a6a7701c459',
                'event_descriptor': {
                    'tags': [
                        'dispatch_short',
                        'tariff_econom',
                        'lookup_mode_multioffer',
                        'has_order_comment',
                    ],
                    event_descriptor_pkey: 'reject_manual',
                },
                'event_type': 'multioffer_order',
                'id': '5cf62b5f629526419e1b58ey',
                'order_alias_id': '',
                'order_id': 'order_id_3',
                'time_to_a': 560,
                'timestamp': '2019-05-01T08:27:11.468000Z',
                'zone': 'moscow',
            },
        ],
    }


@pytest.fixture
def driver_metrics_mockserver(mockserver):
    @mockserver.json_handler('/driver_metrics/v1/activity/history/')
    def mock_driver_metrics_response(request):
        return dm_response_prepare({}, event_descriptor_pkey='name')


@pytest.mark.config(**CONFIG)
@pytest.mark.now('2019-06-04T08:27:11.468000Z')
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.parametrize('reuse_activity', [True, False])
@pytest.mark.parametrize(
    'timezone, time_range, no_dm_proxy_percents, dms_response_code',
    [
        ('Europe/Moscow', '28 May — 2 June', 0, 200),
        ('Pacific/Kiritimati', '28 May — 2 June', 0, 200),
        ('Europe/Moscow', '28 May — 2 June', 100, 200),
        ('Pacific/Kiritimati', '28 May — 2 June', 100, 200),
        ('Europe/Moscow', '28 May — 2 June', 100, 429),
        ('Pacific/Kiritimati', '28 May — 2 June', 100, 429),
    ],
    ids=[
        'timezone_1_1',
        'timezone_2_1',
        'timezone_1_2_ok',
        'timezone_2_2_ok',
        'timezone_1_2_toomany',
        'timezone_2_2_toomany',
    ],
)
def test_driver_activity_list_base(
        taxi_driver_protocol,
        mockserver,
        reuse_activity,
        geotracks_response_track3,
        timezone,
        time_range,
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
        '/driver/activity_list',
        params={
            'db': '16de978d526e40c0bf91e847245af741',
            'session': 'test_session_id_123FFFF',
            'limit': 3,
            'tz': timezone,
        },
        headers={
            'Accept-Language': 'en',
            'User-Agent': (
                'Taximeter {} (997)'.format(REUSE_ACTIVITY_VERSION)
                if reuse_activity
                else 'Taximeter 8.78 (997)'
            ),
        },
    )
    assert response.status_code == dms_response_code
    if dms_response_code != 200:
        return

    response_json = response.json()
    items = response_json['ui']['items']

    def filter_out_none_values(inmap):
        if isinstance(inmap, dict):
            return {
                k: filter_out_none_values(v)
                for k, v in inmap.items()
                if v is not None
            }
        if isinstance(inmap, list):
            return [filter_out_none_values(v) for v in inmap]
        return inmap

    def get_payload(
            timestamp=None,
            subtitle1=None,
            subtitle2=None,
            order_id=None,
            order_alias_id=None,
            value=None,
            time_distance=None,
    ):
        if reuse_activity:
            retval = {
                'date': timestamp,
                'type': 'navigate_financial_order_details',
            }
            if order_alias_id:
                retval['order_id'] = order_alias_id
            return filter_out_none_values(retval)
        return filter_out_none_values(
            {
                'date': timestamp,
                'order_info': {
                    'id': order_id,
                    'items': [
                        {
                            'result': {'value': value},
                            'subtitle': subtitle1,
                            'title': 'activity_title',
                        },
                        {'subtitle': subtitle2, 'title': time_distance},
                    ],
                },
                'type': 'activity_history_order',
            },
        )

    expected = [
        {
            'center': True,
            'horizontal_divider_type': 'bottom',
            'payload': {
                'title': 'activity_title',
                'type': 'navigate_url',
                'url': 'https://driver.yandex/activity',
            },
            'right_icon': 'navigate',
            'title': 'About activity: ',
            'type': 'default',
        },
        {'title': 'Today', 'type': 'title'},
        {
            'detail': '-14',
            'horizontal_divider_type': 'bottom',
            'subdetail': 'cancel_ride',
            'subtitle': 'middle_transfer',
            'title': '5 min • 1 km',
            'type': 'detail',
            'right_icon': 'navigate',
            'payload': get_payload(
                **{
                    'timestamp': '2019-06-04T08:27:11.468000Z',
                    'subtitle1': 'cancel_ride',
                    'subtitle2': 'middle_transfer',
                    'order_id': 'id_5',
                    'order_alias_id': 'alias_5',
                    'value': '-14',
                    'time_distance': '5 min • 1 km',
                },
            ),
        },
        {'title': time_range, 'type': 'title'},
        {
            'detail': '-7',
            'horizontal_divider_type': 'bottom',
            'subdetail': 'cancel_ride',
            'subtitle': 'middle_transfer',
            'title': '5 min • 1 km',
            'type': 'detail',
            'right_icon': 'navigate',
            'payload': get_payload(
                **{
                    'timestamp': '2019-06-01T08:27:11.468000Z',
                    'subtitle1': 'cancel_ride',
                    'subtitle2': 'middle_transfer',
                    'order_id': '4',
                    'order_alias_id': 'alias_6',
                    'value': '-7',
                    'time_distance': '5 min • 1 km',
                },
            ),
        },
        {
            'detail': '-3',
            'horizontal_divider_type': 'bottom',
            'subdetail': 'pass_ride',
            'title': '10 min • 3 km',
            'type': 'detail',
            'right_icon': 'navigate',
            'payload': get_payload(
                **{
                    'timestamp': '2019-05-01T08:27:11.468000Z',
                    'subtitle1': 'pass_ride',
                    'subtitle2': None,
                    'order_id': 'order_id_3',
                    'order_alias_id': None,
                    'value': '-3',
                    'time_distance': '10 min • 3 km',
                },
            ),
        },
    ]
    assert expected == items


@pytest.mark.config(**CONFIG)
@pytest.mark.now('2019-02-07T15:00:00Z')
@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2017-04-29T12:00:00+0300')
@pytest.mark.parametrize(
    'reuse_activity, no_dm_proxy_percents',
    [
        (True, 0),
        (False, 0),
        (True, 100),
        (False, 100),
        (True, 100),
        (False, 100),
    ],
)
def test_driver_activity_list_unique_driver_id(
        taxi_driver_protocol,
        geotracks_response_track3,
        mockserver,
        reuse_activity,
        driver_authorizer_service,
        driver_metrics_mockserver,
        no_dm_proxy_percents,
        dms_context,
        dms_fixture,
):
    dms_context.set_v1_activity_history_response(dm_response_prepare)
    dms_context.set_no_proxy_activity_history_percents(no_dm_proxy_percents)
    taxi_driver_protocol.invalidate_caches()

    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af741',
        'test_session_id_123FFFF',
        '2eaf04fe6dec4330a6f29a6a7701c459',
    )
    driver_authorizer_service.set_session(
        '16de978d526e40c0bf91e847245af741',
        'test_session_id_123DDDD',
        '2eaf04fe6dec4330a6f29a6a77010001',
    )
    request_params = {
        'db': '16de978d526e40c0bf91e847245af741',
        'session': 'test_session_id_123FFFF',
        'newer_than': '2018-8-22T08:50:36+0023',
        'older_than': '2018-8-26T08:50:36+0023',
        'limit': 3,
    }
    user_agent = (
        'Taximeter {} (997)'.format(REUSE_ACTIVITY_VERSION)
        if reuse_activity
        else 'Taximeter 8.78 (997)'
    )
    response = taxi_driver_protocol.post(
        '/driver/activity_list',
        params=request_params,
        headers={'Accept-Language': 'en', 'User-Agent': user_agent},
    )
    assert response.status_code == 200

    request_params['session'] = 'test_session_id_123DDDD'

    response_2 = taxi_driver_protocol.post(
        '/driver/activity_list',
        params=request_params,
        headers={'Accept-Language': 'en', 'User-Agent': user_agent},
    )
    assert response.status_code == 200
    if reuse_activity:
        # Orders from other driver profiles aren't clickable
        items = response.json()['ui']['items'][-4:]
        items_2 = response_2.json()['ui']['items'][-4:]
        assert (
            'payload' not in items[0]
            and 'payload' in items[1]
            and 'payload' in items[2]
            and 'payload' in items[3]
        )
        assert (
            'payload' not in items_2[0]
            and 'payload' not in items_2[1]
            and 'payload' not in items_2[2]
            and 'payload' not in items_2[3]
        )
        assert len(response.json()['ui']['items']) == 5
    else:
        assert len(response.json()['ui']['items']) == 5
        assert len(response_2.json()['ui']['items']) == 5
