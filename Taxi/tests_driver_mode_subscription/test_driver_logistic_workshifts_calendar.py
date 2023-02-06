import datetime as dt
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scheduled_slots_tools

_PARK_ID = 'parkid'
_DRIVER_ID = 'driverid'

_REQUEST_HEADERS = {
    'Accept-Language': 'ru',
    'Timezone': 'Europe/Moscow',
    'User-Agent': 'Taximeter 8.80 (562)',
    'X-YaTaxi-Park-Id': _PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': _DRIVER_ID,
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '8.80 (562)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'X-Ya-Service-Ticket': common.MOCK_TICKET,
}

_REQUEST_BODY = {
    'contractor_position': {'lon': 30.1, 'lat': 60},
    'viewport_region': {
        'top_left': {'lon': 30.1, 'lat': 60},
        'bottom_right': {'lon': 35.1, 'lat': 65},
    },
}

_OFFER_CALENDAR_RESPONSE = {
    'days': [
        {
            'date_description': {
                'date': '2019-04-30',
                'time_range': {
                    'begin': '2019-04-30T17:00:00+00:00',
                    'end': '2019-04-30T18:30:00+00:00',
                },
            },
            'viewport_suggest': {
                'top_left': {'lon': 30.1, 'lat': 60},
                'bottom_right': {'lon': 35.1, 'lat': 65},
            },
        },
        {
            'date_description': {
                'date': '2019-05-01',
                'time_range': {
                    'begin': '2019-05-01T16:00:00+00:00',
                    'end': '2019-05-01T17:30:00+00:00',
                },
            },
            'viewport_suggest': {
                'top_left': {'lon': 30.54, 'lat': 60.12},
                'bottom_right': {'lon': 35.48, 'lat': 64.94},
            },
        },
        {
            'date_description': {
                'date': '2019-05-02',
                'time_range': {
                    'begin': '2019-05-02T14:00:00+00:00',
                    'end': '2019-05-02T15:30:00+00:00',
                },
            },
            'viewport_suggest': {
                'top_left': {'lon': 29.74, 'lat': 56.94},
                'bottom_right': {'lon': 34.76, 'lat': 64.65},
            },
        },
        {
            'date_description': {
                'date': '2019-05-04',
                'time_range': {
                    'begin': '2019-05-04T19:00:00+00:00',
                    'end': '2019-05-04T20:30:00+00:00',
                },
            },
            'viewport_suggest': {
                'top_left': {'lon': 30.29, 'lat': 60.37},
                'bottom_right': {'lon': 34.77, 'lat': 64.91},
            },
        },
    ],
}

_OFFER_POLYGON = {
    'coordinates': [
        [
            {'lat': 62.0, 'lon': 54.0},
            {'lat': 64.0, 'lon': 54.0},
            {'lat': 64.0, 'lon': 52.0},
            {'lat': 62.0, 'lon': 52.0},
            {'lat': 62.0, 'lon': 54.0},
        ],
    ],
}

_SLOT_CHANGES = {
    'item_view_subtitle': 'slot changes item view subtitle',
    'title': 'slot changes title',
    'title_before': 'slot changes title before',
    'before': [
        {
            'title': 'old offer description title',
            'text': 'old offer description text',
            'value': 'old offer description value',
            'content_code_hint': 'default',
        },
    ],
    'title_after': 'slot changes title after',
    'after': [
        {
            'title': 'new offer description title',
            'text': 'new offer description text',
            'value': 'new offer description value',
            'content_code_hint': 'default',
        },
    ],
}

_QUOTA_ID_1 = '7463f61d-0d9c-4fad-96e4-a06f33dcc9ab'
_QUOTA_ID_2 = '4df83ad6-b97d-4e6a-b29b-44ac61385556'
_QUOTA_ID_3 = 'da310926-ef04-4d67-9688-055c26ce3ea2'
_QUOTA_ID_4 = 'b2746c30-9e93-4297-b61e-b41f48092a73'

_LOGISTIC_WORKSHIFTS = 'logistic_workshifts'
_LOGISTIC_WORKSHIFTS_RULE_ID = 'bd1403c3c41548a88ef1d4e158808f73'

_SLOT_ID_1 = '0d2841a3-b966-4a3b-8be4-7e915d3fb995'
_SLOT_ID_2 = '51293c5a-34c0-4a32-a1b0-ae149453888b'
_SLOT_ID_3 = 'c4fec8b6-c95e-4981-819f-cd2a2de16c02'
_SLOT_ID_4 = '0d96469a-bf98-4482-8dba-7c8f71860332'

_OFFER_IDENTITY_1 = {'slot_id': _SLOT_ID_1, 'rule_version': 1}
_OFFER_IDENTITY_2 = {'slot_id': _SLOT_ID_2, 'rule_version': 2}
_OFFER_IDENTITY_3 = {'slot_id': _SLOT_ID_3, 'rule_version': 3}
_OFFER_IDENTITY_4 = {'slot_id': _SLOT_ID_4, 'rule_version': 3}
_OFFER_IDENTITY_ACCEPTED = {'slot_id': _SLOT_ID_4, 'rule_version': 1}

_SLOT_NAME_1 = _SLOT_ID_1.replace('-', '')
_SLOT_NAME_2 = _SLOT_ID_2.replace('-', '')
_SLOT_NAME_3 = _SLOT_ID_3.replace('-', '')
_SLOT_NAME_4 = _SLOT_ID_4.replace('-', '')

_DATE_1 = dt.datetime(2019, 5, 1, 9, 0, tzinfo=dt.timezone.utc)
_DATE_2 = dt.datetime(2019, 5, 2, 23, 0, tzinfo=dt.timezone.utc)
_DATE_3 = dt.datetime(2019, 5, 3, 12, 0, tzinfo=dt.timezone.utc)
_DATE_4 = dt.datetime(2019, 5, 4, 12, 0, tzinfo=dt.timezone.utc)

_POWER_POLICY = {
    'background': 300,
    'full': 100,
    'idle': 400,
    'powersaving': 200,
}


def _unpack_polling_header(header_content: str):
    result = {}

    parts = header_content.split(', ')
    for part in parts:
        line = part.split('=')
        result[line[0]] = int(line[1][:-1])

    return result


def build_slot_info(
        offer_identity: Dict[str, Any],
        slot_start_time: dt.datetime,
        slot_stop_time: dt.datetime,
        quota_id: str,
):
    return {
        'identity': offer_identity,
        'visibility_info': {
            'invisibility_audit_reasons': ['reason1', 'reason2'],
        },
        'time_range': {
            'begin': slot_start_time.isoformat(),
            'end': slot_stop_time.isoformat(),
        },
        'activation_state': 'waiting',
        'item_view': {
            'icon': 'check_ok',
            'captions': {'title': 'title1', 'subtitle': 'subtitle1'},
            'details_captions': {'title': 'title2', 'subtitle': 'subtitle2'},
            'subtitle_highlight': 'warning',
        },
        'description': {
            'icon': 'check_ok',
            'captions': {'title': 'title3', 'subtitle': 'subtitle3'},
            'subtitle_highlight': 'danger',
            'items': [
                {
                    'title': 'title4',
                    'text': 'text4',
                    'content_code_hint': 'expiration_timestamp',
                    'value': '2033-04-06T19:00:00+00:00',
                    'free_time_end': '2033-04-06T19:00:00+00:00',
                    'extra_time_end': '2033-04-06T19:05:00+00:00',
                },
                {'content_code_hint': 'capacity'},
                {
                    'title': 'Сегодня',
                    'value': '7:00 - 12:00',
                    'content_code_hint': 'default',
                },
            ],
        },
        'requirements': [
            {
                'is_satisfied': True,
                'title': 'requirement title',
                'items': [
                    {
                        'is_satisfied': True,
                        'captions': {
                            'title': 'requirement-requirement title',
                            'subtitle': 'requirement-requirement subtitle',
                        },
                        'icon': 'check_ok',
                    },
                ],
                'dissatisfied_audit_reasons': ['reason 1', 'reason 2'],
            },
        ],
        'cancellation_opportunity': {
            'offer': {'fine_value': {'currency_code': 'RUB', 'value': '42'}},
            'short_text': 'Cancelation offer short message',
        },
        'quota_id': quota_id,
        'allowed_transport_types': ['auto'],
        'actions': [
            {
                'action_type': 'stop',
                'label': 'Stop',
                'icon': 'stop',
                'is_active': True,
            },
            {
                'action_type': 'pause',
                'label': 'Pause',
                'icon': 'pause',
                'dialog_title': 'Pause?',
                'dialog_message': 'Are you sure?',
                'dialog_close_button': 'Yes',
            },
        ],
    }


def build_expected_slot_info(
        offer_identity: Dict[str, Any],
        previous_offer_identity: Optional[Dict[str, Any]],
        slot_start_time: dt.datetime,
        slot_stop_time: dt.datetime,
        booking_state: str,
        slot_available: str,
):
    slot_info = {
        'mode_rule_id': _LOGISTIC_WORKSHIFTS_RULE_ID,
        'mode_rule_settings': {'logistic_offer_identity': offer_identity},
        'time_range': {
            'begin': slot_start_time.isoformat(),
            'end': slot_stop_time.isoformat(),
        },
        'activation_state': 'waiting',
        'booking_state': booking_state,
        'availability_state': 'booked',
        'item_view': {
            'icon': 'check_ok',
            'captions': {'title': 'title1', 'subtitle': 'subtitle1'},
            'details_captions': {'title': 'title2', 'subtitle': 'subtitle2'},
            'subtitle_highlight': 'warning',
        },
        'description': {
            'icon': 'check_ok',
            'captions': {'title': 'title3', 'subtitle': 'subtitle3'},
            'subtitle_highlight': 'danger',
            'items': [
                {
                    'title': 'title4',
                    'text': 'text4',
                    'content_type': 'expiration_timestamp',
                    'value': '2033-04-06T19:00:00+00:00',
                    'paused_until': '2033-04-06T19:00:00+00:00',
                    'pause_penalty_deadline': '2033-04-06T19:05:00+00:00',
                },
                {'title': 'Свободных мест', 'value': slot_available},
                {'title': 'Сегодня', 'value': '7:00 - 12:00'},
            ],
        },
        'requirements': [
            {
                'is_satisfied': True,
                'title': 'requirement title',
                'items': [
                    {
                        'is_satisfied': True,
                        'captions': {
                            'title': 'requirement-requirement title',
                            'subtitle': 'requirement-requirement subtitle',
                        },
                        'icon': 'check_ok',
                    },
                ],
            },
        ],
        'cancellation_opportunity': {
            'offer': {'fine_value': {'currency_code': 'RUB', 'value': '42'}},
            'short_text': 'Cancelation offer short message',
        },
        'actions': [
            {
                'action_type': 'stop',
                'label': 'Stop',
                'icon': 'stop',
                'is_active': True,
            },
            {
                'action_type': 'pause',
                'label': 'Pause',
                'icon': 'pause',
                'dialog': {
                    'title': 'Pause?',
                    'message': 'Are you sure?',
                    'buttons': [{'type': 'close', 'text': 'Yes'}],
                },
            },
        ],
    }

    if previous_offer_identity:
        slot_info['changes'] = {
            'previous_mode_rule_id': _LOGISTIC_WORKSHIFTS_RULE_ID,
            'previous_mode_rule_settings': {
                'logistic_offer_identity': previous_offer_identity,
            },
            'item_view_subtitle': 'slot changes item view subtitle',
            'title': 'slot changes title',
            'title_before': 'slot changes title before',
            'before': [
                {
                    'title': 'old offer description title',
                    'text': 'old offer description text',
                    'value': 'old offer description value',
                },
            ],
            'title_after': 'slot changes title after',
            'after': [
                {
                    'title': 'new offer description title',
                    'text': 'new offer description text',
                    'value': 'new offer description value',
                },
            ],
        }

    return {'slot_info': slot_info, 'polygon': _OFFER_POLYGON}


_EXPECTED_RESPONSE = {
    'days': [
        {
            'date_description': {
                'date': '2019-04-30',
                'time_range': {
                    'begin': '2019-04-30T17:00:00+00:00',
                    'end': '2019-04-30T18:30:00+00:00',
                },
                'captions': {'title': 'Вторник', 'subtitle': '30 апреля'},
            },
            'booked_slots': [],
            'viewport_suggest': {
                'top_left': {'lon': 30.1, 'lat': 60.0},
                'bottom_right': {'lon': 35.1, 'lat': 65.0},
            },
            'can_add_slots': True,
        },
        {
            'date_description': {
                'date': '2019-05-01',
                'time_range': {
                    'begin': '2019-05-01T16:00:00+00:00',
                    'end': '2019-05-01T17:30:00+00:00',
                },
                'captions': {'title': 'Сегодня', 'subtitle': '1 мая'},
            },
            'booked_slots': [
                build_expected_slot_info(
                    _OFFER_IDENTITY_1,
                    _OFFER_IDENTITY_ACCEPTED,
                    _DATE_1,
                    _DATE_2,
                    'ready',
                    '99 из 100',
                ),
            ],
            'viewport_suggest': {
                'top_left': {'lon': 30.54, 'lat': 60.12},
                'bottom_right': {'lon': 35.48, 'lat': 64.94},
            },
            'can_add_slots': True,
        },
        {
            'date_description': {
                'date': '2019-05-02',
                'time_range': {
                    'begin': '2019-05-02T14:00:00+00:00',
                    'end': '2019-05-02T15:30:00+00:00',
                },
                'captions': {'title': 'Завтра', 'subtitle': '2 мая'},
            },
            'booked_slots': [],
            'viewport_suggest': {
                'top_left': {'lon': 29.74, 'lat': 56.94},
                'bottom_right': {'lon': 34.76, 'lat': 64.65},
            },
            'can_add_slots': True,
        },
        {
            'date_description': {
                'date': '2019-05-03',
                'time_range': {
                    'begin': '2019-05-02T21:00:00+00:00',
                    'end': '2019-05-03T21:00:00+00:00',
                },
                'captions': {'title': 'Пятница', 'subtitle': '3 мая'},
            },
            'booked_slots': [
                build_expected_slot_info(
                    _OFFER_IDENTITY_2,
                    None,
                    _DATE_2,
                    _DATE_3,
                    'booked',
                    '99 из 100',
                ),
                # missing in cache
                build_expected_slot_info(
                    _OFFER_IDENTITY_3,
                    None,
                    _DATE_3,
                    _DATE_4,
                    'booked',
                    '0 из 0',
                ),
            ],
            'viewport_suggest': {
                'top_left': {'lon': 30.1, 'lat': 60.0},
                'bottom_right': {'lon': 35.1, 'lat': 65.0},
            },
            'can_add_slots': False,
        },
        {
            'date_description': {
                'date': '2019-05-04',
                'time_range': {
                    'begin': '2019-05-04T19:00:00+00:00',
                    'end': '2019-05-04T20:30:00+00:00',
                },
                'captions': {'title': 'Суббота', 'subtitle': '4 мая'},
            },
            'booked_slots': [],
            'viewport_suggest': {
                'top_left': {'lon': 30.29, 'lat': 60.37},
                'bottom_right': {'lon': 34.77, 'lat': 64.91},
            },
            'can_add_slots': True,
        },
    ],
}


@pytest.mark.config(
    API_OVER_DATA_ENABLE_CACHES=True,
    API_OVER_DATA_ENABLE_SPECIFIC_CACHE={'__default__': {'__default__': True}},
    API_OVER_DATA_OPENING_LAG_MS={'__default__': {'__default__': -1}},
    TAXIMETER_POLLING_POWER_POLICY_DELAYS={
        '__default__': {
            'background': 1200,
            'full': 600,
            'idle': 1800,
            'powersaving': 1200,
        },
        '/driver/v1/logistic-workshifts/calendar': _POWER_POLICY,
    },
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        patches=[
            mode_rules.Patch(
                rule_name=_LOGISTIC_WORKSHIFTS,
                rule_id=_LOGISTIC_WORKSHIFTS_RULE_ID,
                features={_LOGISTIC_WORKSHIFTS: {}},
            ),
        ],
    ),
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_reservation_query(
            _SLOT_NAME_1,
            _LOGISTIC_WORKSHIFTS,
            _OFFER_IDENTITY_1,
            _OFFER_IDENTITY_ACCEPTED,
            _DATE_1,
            _DATE_2,
            _QUOTA_ID_1.replace('-', ''),
            1,
            _PARK_ID,
            _DRIVER_ID,
        ),
        scheduled_slots_tools.make_insert_reservation_query(
            _SLOT_NAME_2,
            _LOGISTIC_WORKSHIFTS,
            _OFFER_IDENTITY_2,
            _OFFER_IDENTITY_2,
            _DATE_2,
            _DATE_3,
            _QUOTA_ID_2.replace('-', ''),
            1,
            _PARK_ID,
            _DRIVER_ID,
        ),
        scheduled_slots_tools.make_insert_reservation_query(
            _SLOT_NAME_3,
            _LOGISTIC_WORKSHIFTS,
            _OFFER_IDENTITY_3,
            _OFFER_IDENTITY_3,
            _DATE_3,
            _DATE_4,
            _QUOTA_ID_3.replace('-', ''),
            1,
            _PARK_ID,
            _DRIVER_ID,
        ),
        # This reservation will be ignored
        scheduled_slots_tools.make_insert_reservation_query(
            _SLOT_NAME_4,
            _LOGISTIC_WORKSHIFTS,
            _OFFER_IDENTITY_4,
            _OFFER_IDENTITY_4,
            _DATE_3,
            _DATE_3,
            _QUOTA_ID_4.replace('-', ''),
            1,
            _PARK_ID,
            _DRIVER_ID,
            is_deleted=True,
        ),
    ],
)
@pytest.mark.now('2019-05-01T12:00:00+0300')
async def test_get(
        mockserver,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
):

    await taxi_driver_mode_subscription.invalidate_caches()

    @mockserver.json_handler('/driver-mode-index/v1/mode/history')
    def _driver_mode_index_mode_history(request):
        return common.mode_history_response(request, 'driver_fix', mocked_time)

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/offer/calendar',
    )
    def _logistic_supply_conductor_offer_calendar(request):
        return _OFFER_CALENDAR_RESPONSE

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/offer/info/list',
    )
    def _slot_info_list_handler(request):
        slots = []

        for offer_identity, start_time, stop_time, quota_id, need_changes in [
                (_OFFER_IDENTITY_1, _DATE_1, _DATE_2, _QUOTA_ID_1, True),
                (_OFFER_IDENTITY_2, _DATE_2, _DATE_3, _QUOTA_ID_2, False),
                (_OFFER_IDENTITY_3, _DATE_3, _DATE_4, _QUOTA_ID_3, False),
        ]:
            slot = {
                'info': build_slot_info(
                    offer_identity, start_time, stop_time, quota_id,
                ),
            }

            if need_changes:
                slot['changes'] = _SLOT_CHANGES

            slots.append(slot)

        return {'slots': slots}

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/offer/geoarea-by-slot',
    )
    def _logistic_supply_conductor_offer_geoarea_by_slot(request):
        return {
            'polygons': [
                {'polygon': _OFFER_POLYGON, 'offer_identity': offer_identity}
                for offer_identity in [
                    _OFFER_IDENTITY_1,
                    _OFFER_IDENTITY_2,
                    _OFFER_IDENTITY_3,
                ]
            ],
        }

    response = await taxi_driver_mode_subscription.post(
        '/driver/v1/logistic-workshifts/calendar',
        json=_REQUEST_BODY,
        headers=_REQUEST_HEADERS,
    )

    assert _slot_info_list_handler.has_calls == 1

    info_list_request = _slot_info_list_handler.next_call()['request'].json

    assert info_list_request.pop('contractor_id') == {
        'driver_profile_id': _DRIVER_ID,
        'park_id': _PARK_ID,
    }

    info_list_request_slots = info_list_request.pop('slots')
    info_list_request_slots.sort(
        key=lambda slot: (slot['actual_offer']['slot_id']),
    )

    assert info_list_request_slots == [
        {
            'actual_offer': _OFFER_IDENTITY_1,
            'previous_offer': _OFFER_IDENTITY_ACCEPTED,
        },
        {'actual_offer': _OFFER_IDENTITY_2},
        {'actual_offer': _OFFER_IDENTITY_3},
    ]

    assert info_list_request == {}

    assert response.status_code == 200, str(response.reason)
    assert response.json() == _EXPECTED_RESPONSE

    assert (
        _unpack_polling_header(response.headers['X-Polling-Power-Policy'])
        == _POWER_POLICY
    )
