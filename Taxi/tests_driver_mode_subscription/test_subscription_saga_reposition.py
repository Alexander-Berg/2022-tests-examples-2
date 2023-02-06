from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


def check_reposition_request(
        http_request, expected_profile: driver.Profile, expected_mode: str,
):
    assert http_request.query == {
        'driver_profile_id': expected_profile.profile_id(),
        'park_id': expected_profile.park_id(),
    }
    assert http_request.json == {'work_mode': expected_mode}


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'prev_mode_features, next_mode_features, expect_reposition_mode',
    (
        pytest.param(None, None, None, id='no feature, no repositon calls'),
        pytest.param(
            {'reposition': {}},
            None,
            'orders',
            id='stop repositon from prev mode',
        ),
        pytest.param(
            None,
            {'reposition': {}},
            'next_work_mode',
            id='start repositon in next mode',
        ),
        pytest.param(
            {'reposition': {}},
            {'reposition': {}},
            'next_work_mode',
            id='stop start order check',
        ),
        pytest.param(
            {'reposition': {}},
            {'reposition': {'profile': 'some_profile'}},
            'some_profile',
            id='stop start order check with profile',
        ),
        pytest.param(
            {'reposition': {}},
            None,
            'prev_work_mode',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['blocked_state.sql'],
                ),
            ],
            id='compensate stop repositon from prev mode',
        ),
        pytest.param(
            None,
            {'reposition': {}},
            'orders',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['blocked_state.sql'],
                ),
            ],
            id='compensate start repositon in next mode',
        ),
        pytest.param(
            {'reposition': {}},
            {'reposition': {}},
            'prev_work_mode',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['blocked_state.sql'],
                ),
            ],
            id='compensate stop start order check',
        ),
        pytest.param(
            {'reposition': {'profile': 'some_profile_1'}},
            {'reposition': {'profile': 'some_profile_2'}},
            'some_profile_1',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['blocked_state.sql'],
                ),
            ],
            id='compensate stop start order check with profile',
        ),
    ),
)
async def test_subscription_saga_reposition(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        prev_mode_features: Optional[Dict[str, Any]],
        next_mode_features: Optional[Dict[str, Any]],
        expect_reposition_mode: Optional[str],
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='next_work_mode', features=next_mode_features,
                ),
                mode_rules.Patch(
                    rule_name='prev_work_mode', features=prev_mode_features,
                ),
            ],
        ),
    )

    taxi_config.set_values(
        dict(
            DRIVER_MODE_SUBSCRIPTION_SAGA_SETTINGS=(
                saga_tools.SAGA_SETTINGS_ENABLE_COMPENSATION
            ),
        ),
    )
    await taxi_driver_mode_subscription.invalidate_caches()

    test_profile = driver.Profile(f'parkid1_uuid1')

    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('prev_work_mode')},
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler(
        '/reposition-api/internal/reposition-api/v1/service/driver_work_mode',
    )
    def _reposition_driver_mode(request):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    if expect_reposition_mode:
        reposition_request = _reposition_driver_mode.next_call()['request']

        check_reposition_request(
            reposition_request,
            test_profile,
            expect_reposition_mode or 'next_work_mode',
        )

    assert not _reposition_driver_mode.has_calls
