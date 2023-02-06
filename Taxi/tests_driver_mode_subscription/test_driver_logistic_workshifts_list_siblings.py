import dataclasses
import datetime as dt
from typing import Any
from typing import Dict
from typing import List

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scheduled_slots_tools

_PARK_ID = 'testparkid'
_DRIVER_ID = 'uuid'

_ORDERS_RULE_ID = 'a883a23977484000b870f0cfcc84e1f9'
_LOGISTIC_WORKSHIFTS_RULE_ID = 'd289e2b8b6ad41f29e0b5dd8aa99b8b3'
_LOGISTIC_WORKSHIFTS = 'logistic_workshifts'

_MOSCOW_TIMEZONE = dt.timezone(dt.timedelta(hours=3))
_DATE_START_1 = dt.datetime(2021, 4, 24, 1, 30, tzinfo=_MOSCOW_TIMEZONE)
_DATE_START_2 = dt.datetime(2021, 4, 24, 23, 30, tzinfo=_MOSCOW_TIMEZONE)
_DATE_START_3 = dt.datetime(2021, 4, 26, 3, 30, tzinfo=_MOSCOW_TIMEZONE)
_DATE_STOP_1 = dt.datetime(2021, 4, 24, 6, 0, tzinfo=_MOSCOW_TIMEZONE)
_DATE_STOP_2 = dt.datetime(2021, 4, 24, 23, 59, tzinfo=_MOSCOW_TIMEZONE)
_DATE_STOP_3 = dt.datetime(2021, 4, 27, 3, 30, tzinfo=_MOSCOW_TIMEZONE)

_SLOT_ID_1 = 'af31c824-066d-46df-981f-a8dc431d64e7'
_SLOT_ID_2 = 'af31c824-066d-46df-981f-a8dc431d64e9'
_SLOT_ID_3 = 'af31c824-066d-46df-981f-a8dc431d64ea'

_QUOTA_ID_1 = '1cda3f51-f805-4f14-968c-f14bbeaabdac'
_QUOTA_ID_2 = 'c9f69949-6c60-44a5-ab90-44af5a0cd21f'
_QUOTA_ID_3 = '147842cb-0e27-42ce-a009-aa7ec2af88be'

_MODE_SETTINGS_1 = {'slot_id': _SLOT_ID_1, 'rule_version': 1}
_MODE_SETTINGS_2 = {'slot_id': _SLOT_ID_2, 'rule_version': 2}
_MODE_SETTINGS_3 = {'slot_id': _SLOT_ID_3, 'rule_version': 3}


@dataclasses.dataclass
class SlotInfo:
    offer_identity: Dict[str, Any]
    quota_id: str


def _build_slots_info(slots: List[SlotInfo]):
    return [
        {
            'info': {
                'identity': slot.offer_identity,
                'visibility_info': {
                    'invisibility_audit_reasons': ['reason1', 'reason2'],
                },
                'time_range': {
                    'begin': '2021-04-26T03:30:00+03:00',
                    'end': '2021-04-26T03:30:00+03:00',
                },
                'activation_state': 'waiting',
                'item_view': {
                    'icon': 'check_ok',
                    'captions': {'title': 'title1', 'subtitle': 'subtitle1'},
                    'details_captions': {
                        'title': 'title2',
                        'subtitle': 'subtitle2',
                    },
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
                            'value': '30:00',
                            'content_code_hint': 'free_minutes',
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
                                    'subtitle': (
                                        'requirement-requirement subtitle'
                                    ),
                                },
                                'icon': 'check_ok',
                            },
                        ],
                        'dissatisfied_audit_reasons': ['reason 1', 'reason 2'],
                    },
                ],
                'cancellation_opportunity': {
                    'offer': {
                        'fine_value': {'currency_code': 'RUB', 'value': '42'},
                    },
                    'short_text': 'Cancelation offer short message',
                },
                'quota_id': slot.quota_id,
                'allowed_transport_types': ['auto'],
            },
        }
        for slot in slots
    ]


@pytest.mark.config(
    API_OVER_DATA_ENABLE_CACHES=True,
    API_OVER_DATA_ENABLE_SPECIFIC_CACHE={'__default__': {'__default__': True}},
    API_OVER_DATA_OPENING_LAG_MS={'__default__': {'__default__': -1}},
)
@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_LOGISTIC_WORKSHIFTS,
                rule_id=_LOGISTIC_WORKSHIFTS_RULE_ID,
                display_mode=_LOGISTIC_WORKSHIFTS,
                features={_LOGISTIC_WORKSHIFTS: {}},
            ),
        ],
    ),
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_reservation_query(
            slot_name=_SLOT_ID_1.replace('-', ''),
            mode=_LOGISTIC_WORKSHIFTS,
            mode_settings=_MODE_SETTINGS_1,
            starts_at=_DATE_START_1,
            stops_at=_DATE_STOP_1,
            quota_name=_QUOTA_ID_1.replace('-', ''),
            quota_count=1,
            park_id=_PARK_ID,
            driver_id=_DRIVER_ID,
            accepted_mode_settings=_MODE_SETTINGS_1,
        ),
        scheduled_slots_tools.make_insert_reservation_query(
            slot_name=_SLOT_ID_2.replace('-', ''),
            mode=_LOGISTIC_WORKSHIFTS,
            mode_settings=_MODE_SETTINGS_2,
            starts_at=_DATE_START_2,
            stops_at=_DATE_STOP_2,
            quota_name=_QUOTA_ID_2.replace('-', ''),
            quota_count=1,
            park_id=_PARK_ID,
            driver_id=_DRIVER_ID,
            is_deleted=True,
            accepted_mode_settings=_MODE_SETTINGS_2,
        ),
        scheduled_slots_tools.make_insert_slot_quota_query(
            name=_SLOT_ID_3.replace('-', ''),
            mode=_LOGISTIC_WORKSHIFTS,
            mode_settings=_MODE_SETTINGS_3,
            starts_at=_DATE_START_3,
            stops_at=_DATE_STOP_3,
            quota_name=_QUOTA_ID_3.replace('-', ''),
            quota_count=100,
        ),
    ],
)
@pytest.mark.now('2021-04-24T12:00:00+0300')
async def test_logistic_workshifts_list_siblings(
        taxi_driver_mode_subscription,
        mockserver,
        mode_rules_data,
        driver_authorizer,
):
    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/offer/list-siblings',
    )
    def lsc_list_siblings_handler(request):
        return {
            'title': 'title',
            'items': [
                {
                    'captions': {
                        'title': '3 руб/час',
                        'subtitle': '4 руб/час',
                    },
                    'offer_identity': {
                        'slot_id': _SLOT_ID_3,
                        'rule_version': 3,
                    },
                    'time_range': {
                        'begin': _DATE_START_3.isoformat(),
                        'end': _DATE_STOP_3.isoformat(),
                    },
                    'quota_id': _QUOTA_ID_3,
                },
                {
                    'captions': {'title': '1 руб/час'},
                    'offer_identity': {
                        'slot_id': _SLOT_ID_1,
                        'rule_version': 1,
                    },
                    'time_range': {
                        'begin': _DATE_START_1.isoformat(),
                        'end': _DATE_STOP_1.isoformat(),
                    },
                    'quota_id': _QUOTA_ID_1,
                },
                {
                    'captions': {'subtitle': '2 руб/час'},
                    'offer_identity': {
                        'slot_id': _SLOT_ID_2,
                        'rule_version': 2,
                    },
                    'time_range': {
                        'begin': _DATE_START_2.isoformat(),
                        'end': _DATE_STOP_2.isoformat(),
                    },
                    'quota_id': _QUOTA_ID_2,
                },
            ],
        }

    response = await taxi_driver_mode_subscription.post(
        'driver/v1/logistic-workshifts/slots/list-siblings',
        json={
            'mode_rule_id': _LOGISTIC_WORKSHIFTS_RULE_ID,
            'mode_rule_settings': {
                'logistic_offer_identity': {
                    'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
                    'rule_version': 43,
                },
            },
        },
        headers={
            'Accept-Language': 'ru',
            'Timezone': 'Europe/Samara',
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-YaTaxi-Park-Id': _PARK_ID,
            'X-YaTaxi-Driver-Profile-Id': _DRIVER_ID,
            'X-Request-Application-Version': '8.80 (562)',
            'X-Request-Application': 'taximeter',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'android',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
    )

    assert lsc_list_siblings_handler.has_calls
    lsc_request = lsc_list_siblings_handler.next_call()['request']
    assert lsc_request.headers['timezone'] == 'Europe/Samara'
    assert lsc_request.headers['Accept-Language'] == 'ru'
    assert lsc_request.json == {
        'contractor_id': {
            'driver_profile_id': 'uuid',
            'park_id': 'testparkid',
        },
        'offer_identity': {
            'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
            'rule_version': 43,
        },
    }

    assert response.status_code == 200
    assert response.json() == {
        'title': 'title',
        'items': [
            {
                'left_captions': {
                    'title': 'Сегодня, 24 апр',
                    'subtitle': '99 мест',
                },
                'right_captions': {'title': '1 руб/час'},
                'mode_rule_settings': {
                    'logistic_offer_identity': {
                        'slot_id': _SLOT_ID_1,
                        'rule_version': 1,
                    },
                },
                'mode_rule_id': _LOGISTIC_WORKSHIFTS_RULE_ID,
                'divider_type': 'bottom_bold',
                'availability_state': 'booked',
            },
            {
                'left_captions': {
                    'title': 'Вс, 25 апр',
                    'subtitle': '99 мест',
                },
                'right_captions': {'subtitle': '2 руб/час'},
                'mode_rule_settings': {
                    'logistic_offer_identity': {
                        'slot_id': _SLOT_ID_2,
                        'rule_version': 2,
                    },
                },
                'mode_rule_id': _LOGISTIC_WORKSHIFTS_RULE_ID,
                'divider_type': 'bottom_gap',
                'availability_state': 'available',
            },
            {
                'left_captions': {
                    'title': 'Пн, 26 апр',
                    'subtitle': 'Места закончились',
                },
                'right_captions': {
                    'title': '3 руб/час',
                    'subtitle': '4 руб/час',
                },
                'mode_rule_settings': {
                    'logistic_offer_identity': {
                        'slot_id': _SLOT_ID_3,
                        'rule_version': 3,
                    },
                },
                'mode_rule_id': _LOGISTIC_WORKSHIFTS_RULE_ID,
                'divider_type': 'none',
                'availability_state': 'quota_is_over',
            },
        ],
    }


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
            mode_rules.Patch(
                rule_name=_LOGISTIC_WORKSHIFTS,
                rule_id=_LOGISTIC_WORKSHIFTS_RULE_ID,
                display_mode=_LOGISTIC_WORKSHIFTS,
                features={_LOGISTIC_WORKSHIFTS: {}},
            ),
            mode_rules.Patch(rule_name='orders', rule_id=_ORDERS_RULE_ID),
        ],
    ),
)
@pytest.mark.now('2021-04-24T12:00:00+0300')
async def test_logistic_workshifts_list_siblings_check_feature(
        taxi_driver_mode_subscription, mode_rules_data, driver_authorizer,
):
    response = await taxi_driver_mode_subscription.post(
        'driver/v1/logistic-workshifts/slots/list-siblings',
        json={
            'mode_rule_id': _ORDERS_RULE_ID,
            'mode_rule_settings': {
                'logistic_offer_identity': {
                    'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
                    'rule_version': 43,
                },
            },
        },
        headers={
            'Accept-Language': 'ru',
            'Timezone': 'Europe/Samara',
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-YaTaxi-Park-Id': _PARK_ID,
            'X-YaTaxi-Driver-Profile-Id': _DRIVER_ID,
            'X-Request-Application-Version': '8.80 (562)',
            'X-Request-Application': 'taximeter',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'android',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Not logistic mode rule',
    }
