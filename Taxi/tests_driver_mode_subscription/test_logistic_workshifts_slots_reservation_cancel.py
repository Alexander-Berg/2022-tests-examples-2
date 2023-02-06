import datetime as dt
import uuid

import pytest

from tests_driver_mode_subscription import common
from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import scheduled_resets_tools
from tests_driver_mode_subscription import scheduled_slots_tools

_PROFILE_1 = driver.Profile(dbid_uuid='parkid1_uuid1')
_PROFILE_2 = driver.Profile(dbid_uuid='parkid2_uuid2')

_QUOTA_NAME_1 = '2762b26d16ab474888f318d0c59e364c'
_LOGISTIC_WORKSHIFTS_RULE_ID = 'e65516264faa4d2ca52fea538cb75bd1'
_LOGISTIC_WORKSHIFTS = 'logistic_workshifts'

_SLOT_ID_1 = uuid.UUID('0ea9b019-27df-4b73-bd98-bd25d8789daa')

_LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1 = {
    'slot_id': str(_SLOT_ID_1),
    'rule_version': 1,
}

_QUOTA_NAME_2 = 'ef48860c96b7442698d3fdbe39134c69'

_SLOT_ID_2 = uuid.UUID('7df8f6b7-cf39-4200-b912-cd80aba3070d')

_LOGISTIC_WORKSHIFTS_MODE_SETTINGS_2 = {
    'slot_id': str(_SLOT_ID_2),
    'rule_version': 1,
}


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
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
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_1.hex,
            _LOGISTIC_WORKSHIFTS,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
            dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
            _QUOTA_NAME_1,
            2,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            _LOGISTIC_WORKSHIFTS, _SLOT_ID_1.hex, _PROFILE_1,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            _LOGISTIC_WORKSHIFTS, _SLOT_ID_1.hex, _PROFILE_2,
        ),
        scheduled_resets_tools.insert_scheduled_resets(
            [
                scheduled_resets_tools.ScheduledReset(
                    _PROFILE_1.park_id(),
                    _PROFILE_1.profile_id(),
                    'test_reason',
                    dt.datetime.fromisoformat('2021-02-05T01:00:00+00:00'),
                    source=_SLOT_ID_1.hex,
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2021-02-04T4:01:00+00:00')
async def test_logistic_workshifts_reservation_cancel_all(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        pgsql,
):
    scene = scenario.Scene(
        profiles={
            _PROFILE_1: driver.Mode(
                _LOGISTIC_WORKSHIFTS,
                mode_settings=_LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
            ),
            _PROFILE_2: driver.Mode('orders'),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    request = {'cancel_reason': 'emergency', 'slot_id': str(_SLOT_ID_1)}
    headers = {'X-Ya-Service-Ticket': common.MOCK_TICKET}

    response = await taxi_driver_mode_subscription.post(
        'v1/logistic-workshifts/slots/cancel-all-reservations',
        json=request,
        headers=headers,
    )

    assert response.status_code == 200

    assert (
        scheduled_slots_tools.get_reservations_by_slot(pgsql, _SLOT_ID_1.hex)
        == []
    )

    expected_slot_reservation = (
        _SLOT_ID_1.hex,
        dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
        dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
        _LOGISTIC_WORKSHIFTS,
        _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
        _QUOTA_NAME_1,
        0,
        None,
        'emergency_cancel',
    )

    assert scheduled_slots_tools.get_reservations_by_profile(
        pgsql, _PROFILE_1, is_deleted=True,
    ) == [expected_slot_reservation]

    assert scheduled_slots_tools.get_reservations_by_profile(
        pgsql, _PROFILE_2, is_deleted=True,
    ) == [expected_slot_reservation]

    assert scheduled_slots_tools.get_scheduled_quota(pgsql, _QUOTA_NAME_1) == [
        (_QUOTA_NAME_1, 0),
    ]

    assert scheduled_resets_tools.get_scheduled_mode_resets(pgsql) == [
        scheduled_resets_tools.ScheduledReset(
            park_id=_PROFILE_1.park_id(),
            driver_id=_PROFILE_1.profile_id(),
            reason='scheduled_slot_cancel_all',
            scheduled_at=dt.datetime.fromisoformat(
                '2021-02-04T04:01:00+00:00',
            ),
            source=_SLOT_ID_1.hex,
        ),
    ]


@pytest.mark.mode_rules(
    rules=mode_rules.patched(
        [
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
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_1.hex,
            _LOGISTIC_WORKSHIFTS,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
            dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
            _QUOTA_NAME_1,
            2,
        ),
        scheduled_slots_tools.make_insert_slot_quota_query(
            _SLOT_ID_2.hex,
            _LOGISTIC_WORKSHIFTS,
            _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_2,
            dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
            _QUOTA_NAME_2,
            1,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            _LOGISTIC_WORKSHIFTS, _SLOT_ID_1.hex, _PROFILE_1,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            _LOGISTIC_WORKSHIFTS, _SLOT_ID_2.hex, _PROFILE_1,
        ),
        scheduled_slots_tools.make_slot_reservation_query(
            _LOGISTIC_WORKSHIFTS, _SLOT_ID_1.hex, _PROFILE_2,
        ),
        scheduled_resets_tools.insert_scheduled_resets(
            [
                scheduled_resets_tools.ScheduledReset(
                    _PROFILE_1.park_id(),
                    _PROFILE_1.profile_id(),
                    'test_reason',
                    dt.datetime.fromisoformat('2021-02-05T01:00:00+00:00'),
                    source=_SLOT_ID_1.hex,
                ),
                scheduled_resets_tools.ScheduledReset(
                    _PROFILE_2.park_id(),
                    _PROFILE_2.profile_id(),
                    'test_reason',
                    dt.datetime.fromisoformat('2021-02-05T01:00:00+00:00'),
                    source=_SLOT_ID_1.hex,
                ),
            ],
        ),
    ],
)
@pytest.mark.now('2021-02-04T4:01:00+00:00')
async def test_logistic_workshifts_reservation_cancel(
        taxi_driver_mode_subscription,
        mockserver,
        mocked_time,
        driver_authorizer,
        mode_rules_data,
        pgsql,
):
    scene = scenario.Scene(
        profiles={
            _PROFILE_1: driver.Mode(
                _LOGISTIC_WORKSHIFTS,
                mode_settings=_LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
            ),
            _PROFILE_2: driver.Mode('orders'),
        },
    )
    scene.setup(mockserver, mocked_time, driver_authorizer)

    request = {
        'cancel_reason': 'workshift_violations',
        'slot_id': str(_SLOT_ID_1),
        'contractors': [
            {
                'contractor_id': {
                    'park_id': _PROFILE_1.park_id(),
                    'driver_profile_id': _PROFILE_1.profile_id(),
                },
            },
            {
                'contractor_id': {
                    'park_id': 'unknown',
                    'driver_profile_id': 'unknown',
                },
            },
        ],
    }
    headers = {'X-Ya-Service-Ticket': common.MOCK_TICKET}

    response = await taxi_driver_mode_subscription.post(
        'v1/logistic-workshifts/slots/cancel-reservations',
        json=request,
        headers=headers,
    )

    assert response.status_code == 200

    assert (
        scheduled_slots_tools.get_reservations_by_profile(pgsql, _PROFILE_1)
        == [
            (
                _SLOT_ID_2.hex,
                dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
                dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
                _LOGISTIC_WORKSHIFTS,
                _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_2,
                _QUOTA_NAME_2,
                1,
                None,
                None,
            ),
        ]
    )

    assert (
        scheduled_slots_tools.get_reservations_by_profile(
            pgsql, _PROFILE_1, is_deleted=True,
        )
        == [
            (
                _SLOT_ID_1.hex,
                dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
                dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
                _LOGISTIC_WORKSHIFTS,
                _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
                _QUOTA_NAME_1,
                1,
                None,
                'violations',
            ),
        ]
    )

    assert (
        scheduled_slots_tools.get_reservations_by_profile(pgsql, _PROFILE_2)
        == [
            (
                _SLOT_ID_1.hex,
                dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
                dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
                _LOGISTIC_WORKSHIFTS,
                _LOGISTIC_WORKSHIFTS_MODE_SETTINGS_1,
                _QUOTA_NAME_1,
                1,
                None,
                None,
            ),
        ]
    )

    assert scheduled_slots_tools.get_scheduled_quota(pgsql, _QUOTA_NAME_1) == [
        (_QUOTA_NAME_1, 1),
    ]

    assert scheduled_slots_tools.get_scheduled_quota(pgsql, _QUOTA_NAME_2) == [
        (_QUOTA_NAME_2, 1),
    ]

    assert scheduled_resets_tools.get_scheduled_mode_resets(pgsql) == [
        scheduled_resets_tools.ScheduledReset(
            park_id=_PROFILE_1.park_id(),
            driver_id=_PROFILE_1.profile_id(),
            reason='scheduled_slot_cancel_by_violations',
            scheduled_at=dt.datetime.fromisoformat(
                '2021-02-04T04:01:00+00:00',
            ),
            source=_SLOT_ID_1.hex,
        ),
        scheduled_resets_tools.ScheduledReset(
            _PROFILE_2.park_id(),
            _PROFILE_2.profile_id(),
            'test_reason',
            dt.datetime.fromisoformat('2021-02-05T01:00:00+00:00'),
            source=_SLOT_ID_1.hex,
        ),
    ]
