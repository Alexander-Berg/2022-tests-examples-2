import datetime as dt
from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario
from tests_driver_mode_subscription import scheduled_slots_tools

_NOW = '2020-05-01T12:05:00+00:00'

_SLOT_ID_1 = '3f5c02925bf24b6894e9cefef91d0bc1'
_SLOT_ID_2 = 'ba033cb256b544b5addfdf9cdb753297'

_OFFER_IDENTITY_1 = {'slot_id': _SLOT_ID_1, 'rule_version': 1}
_OFFER_IDENTITY_2 = {'slot_id': _SLOT_ID_2, 'rule_version': 2}

_TEST_PROFILE = driver.Profile(f'parkid1_uuid1')

_SLOT_MODE = 'prev_work_mode'
_NEXT_MODE = 'next_work_mode'

_SAGA_MEANLESS_REASON = 'some_meanless_reason'


@pytest.mark.now(_NOW)
@pytest.mark.parametrize(
    'prev_mode, '
    'next_mode, '
    'next_mode_settings, '
    'next_mode_has_logistic_workshift, '
    'saga_source, '
    'saga_reason, '
    'expect_scheduled_slots_deleted, '
    'expect_scheduled_slots_deletion_reason, '
    'expect_reserved_count',
    (
        pytest.param(
            _SLOT_MODE,
            _NEXT_MODE,
            _OFFER_IDENTITY_2,
            False,
            saga_tools.SOURCE_SCHEDULED_MODE_CHANGE,
            saga_tools.REASON_SCHEDULED_SLOT_STOP,
            True,
            'planned_stop',
            0,
            id='delete prev slot',
        ),
        pytest.param(
            _SLOT_MODE,
            _NEXT_MODE,
            _OFFER_IDENTITY_1,
            True,
            saga_tools.SOURCE_SCHEDULED_MODE_CHANGE,
            saga_tools.REASON_SCHEDULED_SLOT_RESUBSCRIBE,
            True,
            'planned_start_another_slot',
            0,
            id='start source results in correct deletion reason',
        ),
        pytest.param(
            _SLOT_MODE,
            _SLOT_MODE,
            _OFFER_IDENTITY_1,
            True,
            saga_tools.SOURCE_LOGISTIC_WORKSHIFT_STOP,
            _SAGA_MEANLESS_REASON,
            False,
            None,
            1,
            id='not delete slot if used in same mode',
        ),
        pytest.param(
            _SLOT_MODE,
            _NEXT_MODE,
            _OFFER_IDENTITY_1,
            True,
            saga_tools.SOURCE_LOGISTIC_WORKSHIFT_STOP,
            _SAGA_MEANLESS_REASON,
            True,
            'manual_stop',
            0,
            id='delete slot next mode has logistic feature',
        ),
        pytest.param(
            _SLOT_MODE,
            _NEXT_MODE,
            _OFFER_IDENTITY_1,
            True,
            saga_tools.SOURCE_LOGISTIC_WORKSHIFT_START,
            _SAGA_MEANLESS_REASON,
            True,
            'manual_start_another_slot',
            0,
            id='manual start source results in correct deletion reason',
        ),
        pytest.param(
            _NEXT_MODE,
            _NEXT_MODE,
            _OFFER_IDENTITY_2,
            True,
            saga_tools.SOURCE_LOGISTIC_WORKSHIFT_STOP,
            _SAGA_MEANLESS_REASON,
            False,
            None,
            1,
            id='not crash if slot not exists',
        ),
    ),
)
@pytest.mark.pgsql(
    'driver_mode_subscription',
    queries=[
        scheduled_slots_tools.make_insert_reservation_query(
            _SLOT_ID_1,
            _SLOT_MODE,
            _OFFER_IDENTITY_1,
            _OFFER_IDENTITY_1,
            dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
            dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
            'some_quota',
            1,
            _TEST_PROFILE.park_id(),
            _TEST_PROFILE.profile_id(),
        ),
    ],
)
async def test_subscription_saga_scheduled_slot_remove(
        pgsql,
        mocked_time,
        mode_rules_data,
        stq_runner,
        mockserver,
        prev_mode: str,
        next_mode: str,
        next_mode_settings: Dict[str, Any],
        next_mode_has_logistic_workshift: bool,
        saga_source: str,
        saga_reason: str,
        expect_scheduled_slots_deleted: bool,
        expect_scheduled_slots_deletion_reason: Optional[str],
        expect_reserved_count: int,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name=next_mode,
                    features={'logistic_workshifts': {}}
                    if next_mode_has_logistic_workshift
                    else None,
                ),
                mode_rules.Patch(
                    rule_name=prev_mode, features={'logistic_workshifts': {}},
                ),
            ],
        ),
    )

    with pgsql['driver_mode_subscription'].cursor() as cursor:
        cursor.execute(
            saga_tools.make_insert_saga_query(
                _TEST_PROFILE.park_id(),
                _TEST_PROFILE.profile_id(),
                next_mode=next_mode,
                next_mode_timepoint='2020-04-05 12:00:00+01',
                next_mode_settings=next_mode_settings,
                prev_mode=prev_mode,
                prev_mode_timepoint='2020-04-05 12:00:00+01',
                prev_mode_settings=_OFFER_IDENTITY_1,
                source=saga_source,
                change_reason=saga_reason,
            ),
        )

    @mockserver.json_handler(
        r'/(logistic-supply-conductor/internal/v1/courier/)(?P<name>.+)',
        regex=True,
    )
    def _handlers_mock(request, name):
        return {}

    scene = scenario.Scene(profiles={_TEST_PROFILE: driver.Mode(prev_mode)})
    scene.setup(mockserver, mocked_time)

    await saga_tools.call_stq_saga_task(stq_runner, _TEST_PROFILE)

    assert (
        scheduled_slots_tools.get_reservations_by_profile(
            pgsql, _TEST_PROFILE, is_deleted=expect_scheduled_slots_deleted,
        )
        == [
            (
                _SLOT_ID_1,
                dt.datetime(2021, 2, 4, 4, 1, tzinfo=dt.timezone.utc),
                dt.datetime(2021, 2, 4, 5, 1, tzinfo=dt.timezone.utc),
                _SLOT_MODE,
                _OFFER_IDENTITY_1,
                'some_quota',
                expect_reserved_count,
                _OFFER_IDENTITY_1,
                expect_scheduled_slots_deletion_reason,
            ),
        ]
    )
