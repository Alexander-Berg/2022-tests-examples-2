import typing

import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/events/thread'


@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.config(TVM_ENABLED=True)
async def test_ok_thread(taxi_signal_device_api_admin, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    # filter by driver name, ignore device
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 1,
            'query': {'thread_id': utils.to_base64('d1||1').rstrip('=')},
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 200, response.text

    resp = response.json()
    assert resp['cursor_after'] == utils.get_encoded_events_cursor(
        '2020-02-27T13:02:00+00:00', '4f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )
    assert resp['cursor_before'] == resp['cursor_after']
    assert len(resp['events']) == 1

    event = resp['events'][0]
    assert event['comments_info'] == {'comments_count': 0}
    assert event['id'] == '4f5a516f-29ff-4ebe-93eb-465bf0124e85'
    assert event['type'] == 'driver_lost'
    assert event['resolution'] == 'wrong_driver'
    assert not event['is_critical']

    # filter by car
    response2 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 5, 'query': {'thread_id': utils.to_base64('|c1|xx')}},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response2.status_code == 200, response2.text

    resp = response2.json()
    assert resp['cursor_after'] == utils.get_encoded_events_cursor(
        '2020-02-27T13:02:00+00:00', '4f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )
    assert resp['cursor_before'] == utils.get_encoded_events_cursor(
        '2020-02-27T11:05:00+00:00', '6f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )

    assert (
        len(resp['events']) == 5
        and resp['events'][-1]['id'] == '6f5a516f-29ff-4ebe-93eb-465bf0124e85'
    )

    # filter by device
    response3 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 5,
            'query': {
                'thread_id': utils.to_base64(
                    '||d58e753c44e548ce9edaec0e0ef9c8c3',
                ),
            },
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response3.status_code == 200, response3.text

    resp = response3.json()
    assert resp['cursor_after'] == utils.get_encoded_events_cursor(
        '2020-02-27T12:00:00+00:00', '9f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )
    assert resp['cursor_before'] == resp['cursor_after']

    assert len(resp['events']) == 1

    event = resp['events'][0]
    assert event['comments_info'] == {
        'comments_count': 2,
        'last_comment': {
            'text': 'lol, kek, ti uvolen',
            'created_at': '2020-08-11T15:00:00+00:00',
            'id': '2',
        },
    }
    assert event['id'] == '9f5a516f-29ff-4ebe-93eb-465bf0124e85'
    assert event['type'] == 'sleep'
    assert not event['is_critical']

    response4 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 5,
            'query': {
                'thread_id': utils.to_base64(
                    '||d58e753c44e548ce9edaec0e0ef9c8c3',
                ),
            },
            'cursor_before': resp['cursor_before'],
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )

    assert response4.status_code == 200, response4.text
    assert response4.json() == {
        'cursor_after': resp['cursor_before'],
        'cursor_before': resp['cursor_before'],
        'events': [],
    }

    # and now reversed
    response5 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 5,
            'query': {
                'thread_id': utils.to_base64(
                    '||d58e753c44e548ce9edaec0e0ef9c8c1',
                ),
            },
            'cursor_after': utils.get_encoded_events_cursor(
                '2020-02-27T12:00:00+00:00',
                '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
            ),
            'include_border': True,
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response5.status_code == 200, response5.text

    resp = response5.json()
    assert (
        len(resp['events']) == 1
        and resp['events'][0]['event_at'] == '2020-02-27T12:00:00+00:00'
        and resp['events'][0]['id'] == '8f5a516f-29ff-4ebe-93eb-465bf0124e85'
        and resp['events'][0]['type'] == 'sleep'
        and not resp['events'][0]['is_critical']
        and resp['cursor_before']
        == utils.get_encoded_events_cursor(
            '2020-02-27T12:00:00+00:00',
            '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
        )
        and resp['cursor_after'] == resp['cursor_before']
    )

    # And now between cursors
    response6 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 5,
            'query': {
                'thread_id': utils.to_base64(
                    '||d58e753c44e548ce9edaec0e0ef9c8c1',
                ),
            },
            'cursor_before': utils.get_encoded_events_cursor(
                '2020-02-26T23:55:00+00:00',
                '7f5a516f-29ff-4ebe-93eb-465bf0124e85',
            ),
            'cursor_after': utils.get_encoded_events_cursor(
                '2020-02-27T12:00:00+00:00',
                '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
            ),
            'include_border': True,
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response6.status_code == 200, response6.text

    resp = response6.json()
    assert (
        len(resp['events']) == 3
        and resp['events'][0]['event_at'] == '2020-02-27T12:00:00+00:00'
        and resp['events'][0]['id'] == '8f5a516f-29ff-4ebe-93eb-465bf0124e85'
        and resp['events'][0]['type'] == 'sleep'
        and not resp['events'][0]['is_critical']
        and resp['events'][-1]['event_at'] == '2020-02-26T23:55:00+00:00'
        and resp['events'][-1]['id'] == '7f5a516f-29ff-4ebe-93eb-465bf0124e85'
        and resp['events'][-1]['type'] == 'distraction'
        and resp['events'][-1]['is_critical']
        and resp['cursor_before']
        == utils.get_encoded_events_cursor(
            '2020-02-26T23:55:00+00:00',
            '7f5a516f-29ff-4ebe-93eb-465bf0124e85',
        )
        and resp['cursor_after']
        == utils.get_encoded_events_cursor(
            '2020-02-27T12:00:00+00:00',
            '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
        )
    )


EXPECTED_EVENT_SHORT_FORM1 = {
    'event_at': '2020-02-27T12:00:00+00:00',
    'id': '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
    'type': 'sleep',
    'is_critical': False,
}
EXPECTED_EVENT_SHORT_FORM2 = {
    'event_at': '2020-02-27T11:02:00+00:00',
    'id': '5f5a516f-29ff-4ebe-93eb-465bf0124e85',
    'type': 'driver_lost',
    'is_critical': False,
}
EXPECTED_EVENT_SHORT_FORM3 = {
    'event_at': '2020-02-26T23:55:00+00:00',
    'id': '7f5a516f-29ff-4ebe-93eb-465bf0124e85',
    'type': 'distraction',
    'is_critical': True,
}
EXPECTED_EVENT_SHORT_FORM4 = {
    'event_at': '2020-02-27T12:00:00+00:00',
    'id': '3f5a516f-29ff-4ebe-93eb-465bf0124e85',
    'type': 'sleep',
    'is_critical': False,
}
EXPECTED_EVENT_SHORT_FORM5 = {
    'event_at': '2020-02-27T11:05:00+00:00',
    'id': '6f5a516f-29ff-4ebe-93eb-465bf0124e85',
    'type': 'driver_lost',
    'is_critical': False,
}

EXPECTED_EVENTS_SHORT_FORM1 = [
    EXPECTED_EVENT_SHORT_FORM1,
    EXPECTED_EVENT_SHORT_FORM2,
]
EXPECTED_EVENTS_SHORT_FORM2 = [
    EXPECTED_EVENT_SHORT_FORM1,
    EXPECTED_EVENT_SHORT_FORM3,
]
EXPECTED_EVENTS_SHORT_FORM3 = [EXPECTED_EVENT_SHORT_FORM2]
EXPECTED_EVENTS_SHORT_FORM4: typing.List[typing.Dict] = []
EXPECTED_EVENTS_SHORT_FORM5 = [
    EXPECTED_EVENT_SHORT_FORM1,
    EXPECTED_EVENT_SHORT_FORM4,
    EXPECTED_EVENT_SHORT_FORM5,
    EXPECTED_EVENT_SHORT_FORM2,
]

THREAD_ID = utils.to_base64('||d58e753c44e548ce9edaec0e0ef9c8c1')


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=[
        {
            'event_type': 'sleep',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'distraction',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'driver_lost',
            'is_critical': False,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'tired',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
        {
            'event_type': 'eyeclose',
            'is_critical': True,
            'is_violation': False,
            'fixation_config_path': 'some_path',
        },
    ],
)
@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.parametrize(
    'thread_id, event_types, group_id, group_by,'
    'period, expected_code, expected_events',
    [
        (
            THREAD_ID,
            ['distraction', 'sleep'],
            None,
            None,
            {
                'from': '2021-04-10T00:00:00+03:00',
                'to': '2020-04-10T00:00:00+03:00',
            },
            400,
            None,
        ),
        (
            THREAD_ID,
            ['distraction', 'sleep', 'driver_lost', 'tired'],
            None,
            None,
            {
                'from': '2020-02-27T06:00:00+03:00',
                'to': '2020-03-10T00:00:00+03:00',
            },
            200,
            EXPECTED_EVENTS_SHORT_FORM1,
        ),
        (
            THREAD_ID,
            ['distraction', 'sleep'],
            None,
            None,
            {
                'from': '2020-02-10T00:00:00+03:00',
                'to': '2020-03-10T00:00:00+03:00',
            },
            200,
            EXPECTED_EVENTS_SHORT_FORM2,
        ),
        (
            THREAD_ID,
            ['driver_lost'],
            None,
            None,
            {
                'from': '2020-02-10T00:00:00+03:00',
                'to': '2020-03-10T00:00:00+03:00',
            },
            200,
            EXPECTED_EVENTS_SHORT_FORM3,
        ),
        (
            THREAD_ID,
            ['eyeclose', 'tired'],
            None,
            None,
            {
                'from': '2020-02-10T00:00:00+03:00',
                'to': '2020-03-10T00:00:00+03:00',
            },
            200,
            EXPECTED_EVENTS_SHORT_FORM4,
        ),
        (
            None,
            ['eyeclose', 'tired'],
            '12bb68a6-aae3-421d-9119-ca1c14fd4862',
            None,
            {
                'from': '2020-02-10T00:00:00+03:00',
                'to': '2020-03-10T00:00:00+03:00',
            },
            400,
            None,
        ),
        (
            None,
            ['distraction', 'sleep', 'driver_lost', 'tired'],
            '3bd269aa-3aca-494b-8bbb-88f99847464a',
            'driver_profile_id',
            {
                'from': '2020-02-27T06:00:00+03:00',
                'to': '2020-03-10T00:00:00+03:00',
            },
            200,
            EXPECTED_EVENTS_SHORT_FORM1,
        ),
        (
            None,
            None,
            '3bd269aa-3aca-494b-8bbb-88f99847464a',
            None,
            {
                'from': '2020-02-27T06:00:00+03:00',
                'to': '2020-03-10T00:00:00+03:00',
            },
            200,
            EXPECTED_EVENTS_SHORT_FORM1,
        ),
        (
            None,
            ['distraction', 'sleep', 'driver_lost', 'tired'],
            None,
            None,
            {
                'from': '2020-02-27T06:00:00+03:00',
                'to': '2020-03-10T00:00:00+03:00',
            },
            200,
            EXPECTED_EVENTS_SHORT_FORM5,
        ),
    ],
)
async def test_events_thread_filter(
        taxi_signal_device_api_admin,
        thread_id,
        event_types,
        group_id,
        group_by,
        period,
        expected_code,
        expected_events,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    filter_ = {}
    if event_types:
        filter_['event_types'] = event_types
    if group_id:
        filter_['group_id'] = group_id

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 5,
            'period': period,
            'query': {'thread_id': thread_id, 'filter': filter_},
            'cursor_before': utils.get_encoded_events_cursor(
                '2020-02-26T23:55:00+00:00',
                '7f5a516f-29ff-4ebe-93eb-465bf0124e85',
            ),
            'cursor_after': utils.get_encoded_events_cursor(
                '2020-02-27T12:00:00+00:00',
                '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
            ),
            'include_border': True,
            'group_by': group_by,
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == expected_code, response.text

    if response.status_code != 200:
        return
    response_json = response.json()
    response_events = response_json['events']
    assert len(response_events) == len(expected_events)
    for event, expected_event in zip(response_events, expected_events):
        assert (
            event['event_at'] == expected_event['event_at']
            and event['id'] == expected_event['id']
            and event['type'] == expected_event['type']
            and event['is_critical'] == expected_event['is_critical']
        )


async def test_events_thread_bad_event_types(taxi_signal_device_api_admin):
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 5,
            'query': {
                'thread_id': utils.to_base64(
                    '||d58e753c44e548ce9edaec0e0ef9c8c1',
                ),
                'filter': {
                    'event_types': ['distraction', 'unreal_event_type'],
                },
            },
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response.status_code == 400, response.text
    assert response.json() == {
        'code': 'bad_event_types',
        'message': 'filter event_types provided incorrectly',
    }


@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.config(TVM_ENABLED=True)
async def test_ok_without_thread(taxi_signal_device_api_admin, mockserver):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    response1 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 2, 'query': {}},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response1.status_code == 200, response1.text

    resp = response1.json()
    assert resp['cursor_after'] == utils.get_encoded_events_cursor(
        '2020-02-27T13:02:00+00:00', '4f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )
    assert resp['cursor_before'] == utils.get_encoded_events_cursor(
        '2020-02-27T12:00:00+00:00', '9f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )

    assert len(resp['events']) == 2
    assert [event['id'] for event in resp['events']] == [
        '4f5a516f-29ff-4ebe-93eb-465bf0124e85',
        '9f5a516f-29ff-4ebe-93eb-465bf0124e85',
    ]

    response2 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 5, 'query': {}, 'cursor_before': resp['cursor_before']},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response2.status_code == 200, response2.text

    resp = response2.json()
    assert resp['cursor_before'] == utils.get_encoded_events_cursor(
        '2020-02-26T23:55:00+00:00', '7f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )
    assert resp['cursor_after'] == utils.get_encoded_events_cursor(
        '2020-02-27T12:00:00+00:00', '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )

    assert len(resp['events']) == 5
    assert [event['id'] for event in resp['events']] == [
        '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
        '3f5a516f-29ff-4ebe-93eb-465bf0124e85',
        '6f5a516f-29ff-4ebe-93eb-465bf0124e85',
        '5f5a516f-29ff-4ebe-93eb-465bf0124e85',
        '7f5a516f-29ff-4ebe-93eb-465bf0124e85',
    ]


@pytest.mark.pgsql('signal_device_api_meta_db', files=['events.sql'])
@pytest.mark.config(TVM_ENABLED=True)
async def test_ok_without_thread_but_with_group_by(
        taxi_signal_device_api_admin, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(),
                    'specifications': ['signalq'],
                },
            ],
        }

    response1 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 2, 'query': {}, 'group_by': 'driver_profile_id'},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response1.status_code == 200, response1.text

    resp = response1.json()
    assert resp['cursor_after'] == utils.get_encoded_events_cursor(
        '2020-02-27T13:02:00+00:00', '4f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )
    assert resp['cursor_before'] == utils.get_encoded_events_cursor(
        '2020-02-27T12:00:00+00:00', '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )

    assert len(resp['events']) == 2
    assert [event['id'] for event in resp['events']] == [
        '4f5a516f-29ff-4ebe-93eb-465bf0124e85',
        '8f5a516f-29ff-4ebe-93eb-465bf0124e85',
    ]

    response2 = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 5,
            'query': {},
            'cursor_before': resp['cursor_before'],
            'group_by': 'driver_profile_id',
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'p1'},
    )
    assert response2.status_code == 200, response2.text

    resp = response2.json()
    assert resp['cursor_after'] == utils.get_encoded_events_cursor(
        '2020-02-27T12:00:00+00:00', '3f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )
    assert resp['cursor_before'] == utils.get_encoded_events_cursor(
        '2020-02-26T23:55:00+00:00', '7f5a516f-29ff-4ebe-93eb-465bf0124e85',
    )

    assert len(resp['events']) == 4
    assert [event['id'] for event in resp['events']] == [
        '3f5a516f-29ff-4ebe-93eb-465bf0124e85',
        '6f5a516f-29ff-4ebe-93eb-465bf0124e85',
        '5f5a516f-29ff-4ebe-93eb-465bf0124e85',
        '7f5a516f-29ff-4ebe-93eb-465bf0124e85',
    ]


def _get_demo_event_id(event_id):
    return utils.get_decoded_cursor(event_id).split('|')[1]


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': web_common.DEMO_DEVICES,
        'events': web_common.DEMO_EVENTS,
        'vehicles': web_common.DEMO_VEHICLES,
        'groups': web_common.DEMO_GROUPS,
        'drivers': web_common.DEMO_DRIVERS,
    },
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=web_common.get_demo_whitelist(  # noqa: E501 line too long
        ['tired', 'seatbelt'],
    ),
)
async def test_demo_events_thread_cursor(
        taxi_signal_device_api_admin, mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('no such park'),
                    'specifications': ['taxi'],
                },
            ],
        }

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'limit': 1, 'query': {}},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    response_events1 = response.json()['events']
    assert (
        len(response_events1) == 1
        and _get_demo_event_id(response_events1[0]['id'])
        == web_common.DEMO_EVENTS[0]['id']
        and response_events1[0]['type']
        == web_common.DEMO_EVENTS[0]['event_type']
        and response_events1[0]['device_serial_number']
        == web_common.DEMO_DEVICES[0]['serial_number']
    )

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 1,
            'query': {},
            'include_border': False,
            'cursor_before': response.json()['cursor_before'],
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    response_events2 = response.json()['events']
    assert (
        len(response_events2) == 1
        and _get_demo_event_id(response_events2[0]['id'])
        == web_common.DEMO_EVENTS[1]['id']
        and response_events2[0]['type']
        == web_common.DEMO_EVENTS[1]['event_type']
        and response_events2[0]['device_serial_number']
        == web_common.DEMO_DEVICES[1]['serial_number']
    )

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 1,
            'query': {},
            'include_border': True,
            'cursor_after': response.json()['cursor_after'],
            'cursor_before': response.json()['cursor_before'],
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    event = response.json()['events'][0]
    del event['comments_info']['last_comment']
    del response_events2[0]['comments_info']['last_comment']
    assert event == response_events2[0]

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 1,
            'query': {},
            'cursor_after': response.json()['cursor_after'],
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    event = response.json()['events'][0]
    assert event == response_events1[0]


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': web_common.DEMO_DEVICES,
        'events': web_common.DEMO_EVENTS,
        'vehicles': web_common.DEMO_VEHICLES,
        'groups': web_common.DEMO_GROUPS,
        'drivers': web_common.DEMO_DRIVERS,
    },
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=web_common.get_demo_whitelist(  # noqa: E501 line too long
        ['tired', 'seatbelt'],
    ),
)
@pytest.mark.parametrize(
    'thread_id, event_types, group_id, group_by,'
    'expected_code, expected_events',
    [
        (
            utils.to_base64('||dev2'),
            ['tired', 'ushel v edu', 'seatbelt', 'brosil signalq'],
            None,
            None,
            200,
            [web_common.DEMO_EVENTS[1], web_common.DEMO_EVENTS[3]],
        ),
        (
            None,
            [
                'brosil signalq',
                'ushel v edu',
                'sleep',
                'tired',
                'kak teper zhit',
            ],
            'g1',
            'driver_profile_id',
            200,
            [web_common.DEMO_EVENTS[5]] * 2,
        ),
        (utils.to_base64('||dev1'), ['ushel v edu'], None, None, 200, []),
    ],
)
async def test_demo_events_thread_filter(
        taxi_signal_device_api_admin,
        thread_id,
        event_types,
        group_id,
        group_by,
        expected_code,
        expected_events,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('no such park'),
                    'specifications': ['taxi'],
                },
            ],
        }

    filter_ = {}
    if event_types:
        filter_['event_types'] = event_types
    if group_id:
        filter_['group_id'] = group_id

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={
            'limit': 2,
            'query': {'thread_id': thread_id, 'filter': filter_},
            'group_by': group_by,
        },
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == expected_code, response.text

    response_json = response.json()
    response_events = response_json['events']
    assert len(response_events) == len(expected_events)
    for event, expected_event in zip(response_events, expected_events):
        assert (
            _get_demo_event_id(event['id']) == expected_event['id']
            and event['type'] == expected_event['event_type']
        )
