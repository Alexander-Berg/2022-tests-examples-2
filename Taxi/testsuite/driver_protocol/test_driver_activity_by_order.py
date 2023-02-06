import json

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
        'round.kilometers': {'ru': '%(value).0f км', 'en': '%(value).0f km'},
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


def dm_response_prepare(body, event_descriptor_pkey='name'):
    assert body.get('udid') == '5b7b0c694f007eaf8578b531'
    return {
        'items': [
            {
                'id': '5cf62b5f629526419e1b58ed',
                'activity_value_change': -97,
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
                    event_descriptor_pkey: 'user_cancel',
                    'tags': None,
                },
                'dispatch_traits': {'distance': 'medium'},
            },
        ],
    }


@pytest.fixture
def driver_metrics_mockserver(mockserver):
    @mockserver.json_handler('/driver_metrics/v1/activity/history/')
    def mock_driver_metrics_response(request):
        body = json.loads(list(request.form.items())[0][0])
        return dm_response_prepare(body, event_descriptor_pkey='name')


@pytest.mark.translations(**TRANSLATIONS)
@pytest.mark.now('2017-04-29T12:00:00+0300')
@pytest.mark.parametrize(
    'order_id, alias_id, no_dm_proxy_percents, dms_response_code',
    [
        ('2', None, 0, 200),
        ('3', 'alias_4', 0, 200),
        (None, 'alias_4', 0, 200),
        ('2', None, 100, 200),
        ('3', 'alias_4', 100, 200),
        (None, 'alias_4', 100, 200),
        ('2', None, 100, 429),
        ('3', 'alias_4', 100, 429),
        (None, 'alias_4', 100, 429),
    ],
)
def test_driver_activity_with_driver_metrics(
        taxi_driver_protocol,
        order_id,
        alias_id,
        mockserver,
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

    response = taxi_driver_protocol.post(
        '/service/driver/activity_by_order',
        {
            'db': '16de978d526e40c0bf91e847245af741',
            'uuid': '2eaf04fe6dec4330a6f29a6a7701c459',
            'order_id': [order_id],
            'alias_id': [alias_id],
            'raw': 1,
            'limit': 5,
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == dms_response_code
    if dms_response_code != 200:
        return

    response_json = response.json()
    assert len(response_json['activity']) == 1
    if order_id is not None:
        assert response_json['activity'][0]['item']['order_id'] == order_id
    elif alias_id is not None:
        assert response_json['activity'][0]['item']['alias_id'] == alias_id
    assert response_json['activity'][0]['item']['title'] is not None
    assert response_json['activity'][0]['item']['distance'] == 16698
    assert response_json['activity'][0]['item']['result'] is not None
    assert response_json['activity'][0]['item']['result']['value'] == '-97'
