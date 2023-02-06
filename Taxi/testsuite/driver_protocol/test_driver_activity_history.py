import pytest


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
        'driveractivity.manual_activity_change': {
            'ru': 'корректировка',
            'en': 'manual_activity_change',
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
    'tariff': {
        'round.few_meters': {'ru': '%(value).0f м', 'en': '%(value).0f m'},
        'round.kilometers': {'ru': '%(value).0f км', 'en': '%(value).0f km'},
        'round.minute': {'ru': '%(value).0f мин', 'en': '%(value).0f min'},
        'round.tens_minutes': {
            'ru': '%(value).0f мин',
            'en': '%(value).0f min',
        },
        'currency_with_sign.default': {
            'ru': '$SIGN$$VALUE$$CURRENCY$',
            'en': '$SIGN$$VALUE$$CURRENCY$',
        },
        'currency.rub': {'ru': '₽', 'en': '₽'},
    },
}


# The difference b/w dm and dms event descriptor in `name` and `type`.
# dm_response_prepare used to set correct key in response.
def dm_response_prepare(body, event_descriptor_pkey='name'):
    return {
        'items': [
            {
                'id': '5cf62b5f629526419e1b58ed',
                'activity_value_change': -97,
                'timestamp': '2019-06-04T08:27:11.468000Z',
                'driver_id': '100500_2eaf04fe6dec4330a6f29a6a7701c459',
                'db_id': '16de978d526e40c0bf91e847245af741',
                'time_to_a': 300,
                'distance_to_a': 16698,
                'order_id': '4',
                'zone': 'moscow',
                'activity_value_before': 97,
                'event_type': 'order',
                'event_descriptor': {
                    event_descriptor_pkey: 'user_cancel',
                    'tags': ['chained'],
                },
            },
            {
                'id': '5cf62b5f629526419e1b58eu',
                'activity_value_change': -7,
                'timestamp': '2019-06-04T08:27:11.468000Z',
                'driver_id': '100500_2eaf04fe6dec4330a6f29a6a7701c459',
                'db_id': '16de978d526e40c0bf91e847245af741',
                'time_to_a': 300,
                'distance_to_a': 16698,
                'order_id': '4',
                'zone': 'moscow',
                'activity_value_before': 97,
                'event_type': 'order',
                'event_descriptor': {
                    event_descriptor_pkey: 'park_cancel',
                    'tags': ['chained'],
                },
                'dispatch_traits': {'distance': 'short'},
            },
            {
                'id': '5cf62b5f629526419e1b58ex',
                'activity_value_change': -8,
                'event_descriptor': {
                    event_descriptor_pkey: 'set_activity_manual',
                },
                'event_type': 'dm_service_manual',
                'order_alias_id': '',
                'order_id': '',
                'timestamp': '2019-06-04T08:27:12.468000Z',
                'zone': '',
            },
        ],
    }


@pytest.fixture
def driver_metrics_mockserver(mockserver):
    @mockserver.json_handler('/driver_metrics/v1/activity/history/')
    def mock_driver_metrics_response(request):
        return dm_response_prepare({}, event_descriptor_pkey='name')


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2017-04-29T12:00:00+0300')
@pytest.mark.config(
    TVM_RULES=[
        {'src': 'driver_protocol', 'dst': 'driver-metrics'},
        {'src': 'driver_protocol', 'dst': 'driver-metrics-storage'},
    ],
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'limit, no_dm_proxy_percents, dms_response_code',
    [
        (1, 0, 200),
        (2, 0, 200),
        (1, 100, 200),
        (2, 100, 200),
        (3, 100, 200),
        (1, 100, 429),
        (2, 100, 429),
    ],
)
def test_driver_activity_driver_metrics(
        taxi_driver_protocol,
        driver_metrics_mockserver,
        limit,
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

    request = {
        'db': '16de978d526e40c0bf91e847245af741',
        'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
        'newer_than': '2018-8-22T08:50:36+0023',
        'older_than': '2018-8-26T08:50:36+0023',
        'limit': limit,
    }
    response = taxi_driver_protocol.post(
        '/driver/activity_history',
        request,
        headers={'Accept-Language': 'ru', 'User-Agent': 'Taximeter 9.88'},
    )
    assert response.status_code == dms_response_code
    if dms_response_code != 200:
        return

    response_json = response.json()
    assert len(response_json['activity']) == limit
    assert (
        response_json['activity']
        == [
            {
                'date': '2019-06-04T08:27:11.468000Z',
                'item': {
                    'code': 'USER_CANCEL:chained',
                    'distance': 16698,
                    'order_id': '4',
                    'result': {'comment': 'отмена', 'value': '-97'},
                    'time': 300,
                },
            },
            {
                'date': '2019-06-04T08:27:11.468000Z',
                'item': {
                    'code': 'PARK_CANCEL:chained',
                    'distance': 16698,
                    'order_id': '4',
                    'result': {'comment': 'отмена', 'value': '-7'},
                    'time': 300,
                },
            },
            {
                'date': '2019-06-04T08:27:12.468000Z',
                'item': {
                    'code': 'SET_ACTIVITY_MANUAL',
                    'result': {'value': '-8'},
                },
            },
        ][:limit]
    )
