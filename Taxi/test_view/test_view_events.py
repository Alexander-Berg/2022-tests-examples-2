import pytest

from tests_driver_fix import common

HEADERS = common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY.copy()
HEADERS.update({'Accept-Language': 'en'})


def _make_event(event_type, subtype, extra_data, datetime):
    res = {
        'event_id': 'unused_id',
        'type': event_type,
        'order_id': 'unused_id',
        'order_alias': 'unused_alias',
        'park_driver_profile_id': 'dbid_uuid',
        'tariff_zone': 'unused_zone',
        'datetime': datetime,
        'descriptor': {'type': subtype},
        'extra_data': 'unused_extra_data',
    }

    if extra_data:
        res['extra'] = extra_data

    return res


def _order_complete_event():
    return _make_event(
        event_type='order',
        subtype='complete',
        datetime='2019-10-15T10:01:00+03',
        extra_data={'i_am_key': 'i_am_data'},
    )


def _constraints_start_event():
    return _make_event(
        event_type='constraints',
        subtype='start',
        datetime='2019-10-15T10:00:00+03',
        extra_data={
            'constraints_data': [
                {'id': 'id_frozen_timer_constraint', 'name': 'frozen_timer'},
                {'id': 'id_zone_constraint', 'name': 'zone'},
            ],
        },
    )


def _bad_constraint_start_event(constraint_type):
    return _make_event(
        event_type='constraints',
        subtype='start',
        datetime='2019-10-15T10:00:00+03',
        extra_data={
            'constraints_data': [
                {'id': 'id_bad_constraint', 'name': constraint_type},
            ],
        },
    )


CONSTRAINTS_EVENT_TYPE = {'type': 'constraints', 'localized_type': 'Нарушения'}

REPOSITION_EVENT_TYPE = {
    'type': 'reposition',
    'localized_type': 'Задания проводника',
}

ORDER_EVENT_TYPE = {'type': 'order', 'localized_type': 'Заказы'}


def _constraints_end_event():
    return _make_event(
        event_type='constraints',
        subtype='end',
        datetime='2019-10-15T09:56:00+03',
        extra_data={'constraints_data': [{'id': '1111111', 'name': 'zone'}]},
    )


def _constraint_event_more_recent_than_active():
    return _make_event(
        event_type='constraints',
        subtype='end',
        datetime='2019-10-15T10:01:00+03',
        extra_data={'constraints_data': [{'id': 'id11', 'name': 'zone'}]},
    )


def _reposition_start_event():
    return _make_event(
        event_type='reposition',
        subtype='start',
        datetime='2019-10-15T11:00:00+03',
        extra_data={'session_id': 'session_id', 'state_id': 'id2'},
    )


def _reposition_active_id():
    return 'reposition_active_id'


def _reposition_bonus_event():
    return _make_event(
        event_type='reposition',
        subtype='stop',
        datetime='2019-10-15T11:05:00+03',
        extra_data={
            'session_id': 'session_id',
            'state_id': _reposition_active_id(),
            'status': 'bonus',
        },
    )


def _reposition_event_unexpected_type():
    return _make_event(
        event_type='reposition',
        subtype='unexpected_subtype',
        datetime='2019-10-15T11:09:00+03',
        extra_data=None,
    )


def _reposition_event_unexpected_type_with_extra_info():
    return _make_event(
        event_type='reposition',
        subtype='unexpected_subtype',
        datetime='2019-10-15T11:09:00+03',
        extra_data={'something': '1'},
    )


def _check_event_processed_handler(event_processed_handler):
    assert event_processed_handler.times_called == 1
    request = event_processed_handler.next_call()['request'].json
    assert request == {
        'unique_driver_id': 'very_unique_id',
        'event_types': ['constraints', 'reposition', 'order'],
        'datetime_from': '2019-10-15T01:00:00+00:00',
        'datetime_to': '2019-10-15T09:00:00+00:00',
        'with_additional_info': False,
    }


DRIVER_FIX_VIEW_EVENTS_CONFIG = {
    'journal_duration_in_hours': 8,
    'events': [
        {
            'type': 'constraints',
            'descriptor_types': [
                {
                    'descriptor_type': 'start',
                    'button_required': True,
                    'icon_type': 'warning',
                },
                {
                    'descriptor_type': 'end',
                    'button_required': False,
                    'icon_type': 'ok',
                },
            ],
        },
        {
            'type': 'reposition',
            'descriptor_types': [
                {
                    'descriptor_type': 'start',
                    'button_required': True,
                    'icon_type': 'common',
                },
                {
                    'descriptor_type': 'bonus',
                    'button_required': True,
                    'icon_type': 'bonus',
                },
            ],
        },
        {
            'type': 'order',
            'descriptor_types': [
                {
                    'descriptor_type': 'complete',
                    'button_required': True,
                    'icon_type': 'common',
                },
            ],
        },
    ],
}


FROZEN_TIMER_EVENT = {
    'event_type': CONSTRAINTS_EVENT_TYPE,
    'time': '2019-10-15T07:00:00+00:00',
    'title': 'frozen_timer_title',
    'subtitle': 'frozen_timer_subtitle',
    'button_settings': {
        'enabled': True,
        'text': 'frozen_timer_button',
        'link': 'main_screen',
    },
}

ZONE_EVENT = {
    'event_type': CONSTRAINTS_EVENT_TYPE,
    'time': '2019-10-15T07:00:00+00:00',
    'title': 'zone_title',
    'subtitle': 'zone_subtitle',
    'button_settings': {
        'enabled': True,
        'text': 'zone_button',
        'link': 'orders',
    },
}


@pytest.mark.now('2019-10-15T12:00:00+03')
@pytest.mark.config(
    DRIVER_FIX_VIEW_EVENTS=DRIVER_FIX_VIEW_EVENTS_CONFIG,
    DRIVER_FIX_CONSTRAINTS_ON_TAGS={
        'frozen_timer': {
            'violate_if': [],
            'show_in_status_panel': True,
            'should_freeze_timer': True,
        },
    },
)
@pytest.mark.parametrize(
    'active_constraint_id, expected_event, history_constraint_description',
    [
        (
            'id_frozen_timer_constraint',
            FROZEN_TIMER_EVENT,
            'Вы выехали из зоны',
        ),
        ('id_zone_constraint', ZONE_EVENT, 'Таймер заморожен'),
    ],
)
async def test_view_events_ok(
        mockserver,
        taxi_driver_fix,
        taxi_config,
        unique_drivers,
        active_constraint_id,
        expected_event,
        history_constraint_description,
):
    @mockserver.json_handler('/driver-metrics-storage/v3/events/processed')
    async def _events_processed(request):
        # _contraint_event_more_recent_than_active()
        # should not be in v1/view/events response
        return {
            'events': [
                {'event': _constraint_event_more_recent_than_active()},
                {'event': _constraints_end_event()},
                {'event': _constraints_start_event()},
                {'event': _reposition_start_event()},
                {'event': _reposition_bonus_event()},
            ],
        }

    request = {
        'event_ids': [
            {'event_type': 'constraints', 'id': active_constraint_id},
            {'event_type': 'reposition', 'id': _reposition_active_id()},
        ],
    }

    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')

    response = await taxi_driver_fix.post(
        '/driver/v1/driver-fix/v1/view/events',
        json=request,
        params={'park_id': 'dbid'},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['active_events'] == [
        expected_event,
        {
            'event_type': {'type': 'bonus', 'localized_type': 'Бонус'},
            'time': '2019-10-15T08:05:00+00:00',
            'title': 'bonus_title',
            'subtitle': 'bonus_subtitle',
            'button_settings': {
                'enabled': True,
                'text': 'bonus_button',
                'link': 'reposition',
            },
        },
    ]
    assert response_json['events_history'] == [
        {
            'event_type': CONSTRAINTS_EVENT_TYPE,
            'icon_type': 'ok',
            'time': '2019-10-15T06:56:00+00:00',
            'short_description': 'Вы выехали из зоны',
        },
        {
            'event_type': CONSTRAINTS_EVENT_TYPE,
            'icon_type': 'warning',
            'time': '2019-10-15T07:00:00+00:00',
            'short_description': history_constraint_description,
        },
        {
            'event_type': REPOSITION_EVENT_TYPE,
            'icon_type': 'common',
            'time': '2019-10-15T08:00:00+00:00',
            'short_description': 'Двигайтесь по маршруту',
        },
    ]
    _check_event_processed_handler(_events_processed)


@pytest.mark.now('2019-10-15T12:00:00+03')
@pytest.mark.config(DRIVER_FIX_VIEW_EVENTS=DRIVER_FIX_VIEW_EVENTS_CONFIG)
async def test_view_events_type_not_in_request(
        mockserver, taxi_driver_fix, taxi_config, unique_drivers,
):
    @mockserver.json_handler('/driver-metrics-storage/v3/events/processed')
    async def _events_processed(request):
        return {'events': [{'event': _reposition_start_event()}]}

    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')

    response = await taxi_driver_fix.post(
        '/driver/v1/driver-fix/v1/view/events',
        json={'event_ids': []},
        params={'park_id': 'dbid'},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert not response_json['active_events']
    assert response_json['events_history'] == [
        {
            'time': '2019-10-15T08:00:00+00:00',
            'event_type': REPOSITION_EVENT_TYPE,
            'icon_type': 'common',
            'short_description': 'Двигайтесь по маршруту',
        },
    ]
    _check_event_processed_handler(_events_processed)


@pytest.mark.now('2019-10-15T12:00:00+03')
@pytest.mark.config(DRIVER_FIX_VIEW_EVENTS=DRIVER_FIX_VIEW_EVENTS_CONFIG)
async def test_view_events_dms_events_without_id(
        mockserver, taxi_driver_fix, taxi_config, unique_drivers,
):
    @mockserver.json_handler('/driver-metrics-storage/v3/events/processed')
    async def _events_processed(request):
        result = {'events': []}
        for event in [
                _reposition_start_event(),
                _reposition_event_unexpected_type(),
                _reposition_event_unexpected_type_with_extra_info(),
                _order_complete_event(),
        ]:
            result['events'].append({'event': event})
        return result

    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')

    response = await taxi_driver_fix.post(
        '/driver/v1/driver-fix/v1/view/events',
        json={'event_ids': []},
        params={'park_id': 'dbid'},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert not response_json['active_events']
    assert response_json['events_history'] == [
        {
            'time': '2019-10-15T08:00:00+00:00',
            'event_type': REPOSITION_EVENT_TYPE,
            'icon_type': 'common',
            'short_description': 'Двигайтесь по маршруту',
        },
        {
            'time': '2019-10-15T07:01:00+00:00',
            'event_type': ORDER_EVENT_TYPE,
            'icon_type': 'common',
            'short_description': 'Заказ выполнен',
        },
    ]
    _check_event_processed_handler(_events_processed)


@pytest.mark.parametrize(
    'constraint_name',
    ['not_existent_constraint', 'constraint_not_for_status'],
)
@pytest.mark.now('2019-10-15T12:00:00+03')
@pytest.mark.config(
    DRIVER_FIX_VIEW_EVENTS=DRIVER_FIX_VIEW_EVENTS_CONFIG,
    DRIVER_FIX_CONSTRAINTS_ON_TAGS={
        'constraint_not_for_status': {
            'violate_if': [],
            'show_in_status_panel': False,
        },
    },
)
async def test_view_events_bad_constraint(
        mockserver,
        taxi_driver_fix,
        taxi_config,
        unique_drivers,
        constraint_name,
):
    @mockserver.json_handler('/driver-metrics-storage/v3/events/processed')
    async def _events_processed(request):
        result = {'events': []}
        for event in [_bad_constraint_start_event(constraint_name)]:
            result['events'].append({'event': event})
        return result

    unique_drivers.add_driver('dbid', 'uuid', 'very_unique_id')

    response = await taxi_driver_fix.post(
        '/driver/v1/driver-fix/v1/view/events',
        json={'event_ids': []},
        params={'park_id': 'dbid'},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert not response_json['active_events']
    assert response_json['events_history'] == []
    _check_event_processed_handler(_events_processed)
