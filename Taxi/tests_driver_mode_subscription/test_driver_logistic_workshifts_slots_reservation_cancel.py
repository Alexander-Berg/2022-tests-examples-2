import dataclasses
import datetime as dt
import json
from typing import Any
from typing import Dict


import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import scheduled_resets_tools
from tests_driver_mode_subscription import scheduled_slots_tools

_PARK_ID = 'parkid0'
_DRIVER_ID = 'uuid0'
_QUOTA_NAME = '2762b26d16ab474888f318d0c59e364c'
_LOGISTIC_WORKSHIFTS_RULE_ID = 'e65516264faa4d2ca52fea538cb75bd1'
_LOGISTIC_WORKSHIFTS = 'logistic_workshifts'
_LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS = {
    'slot_id': 'af31c824-066d-46df-981f-a8dc431d64e8',
    'rule_version': 43,
}
_LOGISTIC_WORKSHIFTS_MODE_SETTINGS = {
    'logistic_offer_identity': {
        'slot_id': '7459b0ed-f6fa-494f-a61b-1806c4caa81b',
        'rule_version': 43,
    },
}


@pytest.fixture(name='lsc_check_cancelation_offer')
def _mock_lsc_check_cancelation_offer(mockserver):
    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/'
        'offer/reservation/check-cancellation',
    )
    async def mock_check_cancelation_offer(request):
        return {}

    return mock_check_cancelation_offer


@dataclasses.dataclass
class CancelationOffer:
    value: str
    currency_code: str

    def json(self):
        return {
            'fine_value': {
                'currency_code': self.currency_code,
                'value': self.value,
            },
        }


async def call_cancel_reservation(
        taxi_driver_mode_subscription,
        current_rule_id: str,
        current_mode_settings: Dict[str, Any],
        cancelation_offer: CancelationOffer,
        park_id: str,
        driver_profile_id: str,
):
    params: Dict[str, Any] = {
        'mode_rule_id': current_rule_id,
        'mode_rule_settings': current_mode_settings,
        'cancellation_offer': {
            'logistic_cancelation_offer': cancelation_offer.json(),
        },
    }

    return await taxi_driver_mode_subscription.post(
        'driver/v1/logistic-workshifts/offers/reservation/cancel',
        json=params,
        headers={
            'Accept-Language': 'ru',
            'Timezone': 'Europe/Moscow',
            'User-Agent': 'Taximeter 8.80 (562)',
            'X-Idempotency-Token': 'idempotency_key',
            'X-YaTaxi-Park-Id': park_id,
            'X-YaTaxi-Driver-Profile-Id': driver_profile_id,
            'X-Request-Application-Version': '8.80 (562)',
            'X-Request-Application': 'taximeter',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'android',
            'X-Ya-Service-Ticket': common.MOCK_TICKET,
        },
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
            '7459b0edf6fa494fa61b1806c4caa81b',
            _LOGISTIC_WORKSHIFTS,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS,
            dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
            _QUOTA_NAME,
            110,  # test on overbooked slot just in case
            _PARK_ID,
            _DRIVER_ID,
        ),
    ],
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_driver_logistic_workshifts_reservation_cancel(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        lsc_check_cancelation_offer,
        pgsql,
):
    profile = driver.Profile(dbid_uuid=f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            profile: driver.Mode(
                _LOGISTIC_WORKSHIFTS,
                mode_settings=_LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    assert (
        len(scheduled_slots_tools.get_reservations_by_profile(pgsql, profile))
        == 1
    )

    cancelation_offer = CancelationOffer('43', 'RUB')

    response = await call_cancel_reservation(
        taxi_driver_mode_subscription,
        _LOGISTIC_WORKSHIFTS_RULE_ID,
        _LOGISTIC_WORKSHIFTS_MODE_SETTINGS,
        cancelation_offer,
        _PARK_ID,
        _DRIVER_ID,
    )

    assert response.status_code == 200
    assert response.text == ''

    assert lsc_check_cancelation_offer.has_calls
    lsc_request = lsc_check_cancelation_offer.next_call()['request']
    assert lsc_request.headers['Accept-Language'] == 'ru'
    assert lsc_request.json == {
        'cancellation_offer': cancelation_offer.json(),
        'contractor_id': {'driver_profile_id': 'uuid0', 'park_id': 'parkid0'},
        'actual_offer': {
            'slot_id': '7459b0ed-f6fa-494f-a61b-1806c4caa81b',
            'rule_version': 43,
        },
        'last_accepted_offer': {
            'slot_id': '7459b0ed-f6fa-494f-a61b-1806c4caa81b',
            'rule_version': 43,
        },
    }

    assert (
        scheduled_slots_tools.get_reservations_by_profile(
            pgsql, profile, is_deleted=True,
        )
        == [
            (
                '7459b0edf6fa494fa61b1806c4caa81b',
                dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
                dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
                _LOGISTIC_WORKSHIFTS,
                _LOGISTIC_WORKSHIFTS_MODE_SETTINGS,
                _QUOTA_NAME,
                109,
                _LOGISTIC_WORKSHIFTS_MODE_SETTINGS,
                'manual_cancel',
            ),
        ]
    )

    assert scheduled_slots_tools.get_scheduled_quota(pgsql, _QUOTA_NAME) == [
        (_QUOTA_NAME, 109),
    ]


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
            '7459b0edf6fa494fa61b1806c4caa81b',
            _LOGISTIC_WORKSHIFTS,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS,
            dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
            _QUOTA_NAME,
            110,
            _PARK_ID,
            _DRIVER_ID,
        ),
    ],
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_reservation_cancel_check_error(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        pgsql,
):
    profile = driver.Profile(dbid_uuid=f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            profile: driver.Mode(
                _LOGISTIC_WORKSHIFTS,
                mode_settings=_LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    @mockserver.json_handler(
        '/logistic-supply-conductor/internal/v1/'
        'offer/reservation/check-cancellation',
    )
    async def check_cancelation_offer_handler(request):
        return mockserver.make_response(
            json.dumps(
                {
                    'code': '400',
                    'message': 'Don' 't want to check offer',
                    'details': {
                        'title': 'Нельзя',
                        'subtitle': 'Ошибка проверки оффера',
                        'text': 'Отменить бронирование стоит дороже',
                    },
                },
            ),
            409,
        )

    cancelation_offer = CancelationOffer('43', 'RUB')

    response = await call_cancel_reservation(
        taxi_driver_mode_subscription,
        _LOGISTIC_WORKSHIFTS_RULE_ID,
        _LOGISTIC_WORKSHIFTS_MODE_SETTINGS,
        cancelation_offer,
        _PARK_ID,
        _DRIVER_ID,
    )

    assert response.status_code == 409
    assert response.json() == {
        'code': '400',
        'message': 'Don' 't want to check offer',
        'details': {
            'title': 'Нельзя',
            'subtitle': 'Ошибка проверки оффера',
            'text': 'Отменить бронирование стоит дороже',
        },
    }

    assert check_cancelation_offer_handler.has_calls

    assert (
        len(scheduled_slots_tools.get_reservations_by_profile(pgsql, profile))
        == 1
    )


_LOGISTIC_MODE_2_SCHEDULED_RESET = scheduled_resets_tools.ScheduledReset(
    _PARK_ID,
    _DRIVER_ID,
    'reason',
    dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
    'af31c824066d46df981fa8dc431d64e8',
)

_LOGISTIC_WORKSHIFTS_MODE_SETTINGS_2 = {
    'logistic_offer_identity': _LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS,
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
        ],
    ),
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_reservation_query(
            'af31c824066d46df981fa8dc431d64e8',
            _LOGISTIC_WORKSHIFTS,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_2,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_2,
            dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
            _QUOTA_NAME,
            110,  # test on overbooked slot just in case
            _PARK_ID,
            _DRIVER_ID,
        ),
        scheduled_resets_tools.insert_scheduled_resets(
            [_LOGISTIC_MODE_2_SCHEDULED_RESET],
        ),
    ],
)
@pytest.mark.parametrize(
    'dmi_current_mode_settings, expect_http_error, expected_scheduled_reset',
    [
        pytest.param(
            _LOGISTIC_WORKSHIFTS_ACTUAL_MODE_SETTINGS,
            True,
            _LOGISTIC_MODE_2_SCHEDULED_RESET,
            id='dmi_check_failed',
        ),
        pytest.param(
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS['logistic_offer_identity'],
            False,
            scheduled_resets_tools.ScheduledReset(
                _PARK_ID,
                _DRIVER_ID,
                'scheduled_slot_cancel_by_manual_cancel',
                dt.datetime(2020, 5, 5, 10, 1, tzinfo=dt.timezone.utc),
                'af31c824066d46df981fa8dc431d64e8',
            ),
            id='dmi_check_passed',
        ),
    ],
)
@pytest.mark.now('2020-05-05T13:01:00+03:00')
async def test_reservation_cancel_check_current_slot(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        lsc_check_cancelation_offer,
        pgsql,
        dmi_current_mode_settings: Dict[str, Any],
        expect_http_error: bool,
        expected_scheduled_reset: scheduled_resets_tools.ScheduledReset,
):
    profile = driver.Profile(dbid_uuid=f'{_PARK_ID}_{_DRIVER_ID}')
    scene = scenario.Scene(
        profiles={
            profile: driver.Mode(
                _LOGISTIC_WORKSHIFTS, mode_settings=dmi_current_mode_settings,
            ),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    assert (
        len(scheduled_slots_tools.get_reservations_by_profile(pgsql, profile))
        == 1
    )

    assert scheduled_resets_tools.get_scheduled_mode_resets(pgsql) == [
        _LOGISTIC_MODE_2_SCHEDULED_RESET,
    ]

    cancelation_offer = CancelationOffer('43', 'RUB')

    response = await call_cancel_reservation(
        taxi_driver_mode_subscription,
        _LOGISTIC_WORKSHIFTS_RULE_ID,
        _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_2,
        cancelation_offer,
        _PARK_ID,
        _DRIVER_ID,
    )

    if expect_http_error:
        assert response.status_code == 409
        assert response.json() == {
            'code': 'ALREADY_STARTED',
            'message': 'Cannot cancel active slot',
        }
    else:
        assert response.status_code == 200
        assert response.text == ''

    assert lsc_check_cancelation_offer.has_calls != expect_http_error

    db_slots = scheduled_resets_tools.get_scheduled_mode_resets(pgsql)
    for slot in db_slots:
        slot.scheduled_at = slot.scheduled_at.astimezone(tz=dt.timezone.utc)
    assert db_slots == [expected_scheduled_reset]
