import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.parametrize(
    'prev_mode_features, next_mode_features, expect_active_transport',
    (
        pytest.param(
            None, None, None, id='no feature, no active_transport calls',
        ),
        pytest.param(
            {'active_transport': {'type': 'pedestrian'}},
            None,
            None,
            id='no next_mode feature, no active_transport calls',
        ),
        pytest.param(
            None,
            {'active_transport': {'type': 'bicycle'}},
            'bicycle',
            id='next_mode feature',
        ),
        pytest.param(
            {'active_transport': {'type': 'pedestrian'}},
            {'active_transport': {'type': 'electric_bicycle'}},
            'electric_bicycle',
            id='prev_mode and next_mode feature',
        ),
        pytest.param(
            None,
            {'active_transport': {'type': 'bicycle'}},
            None,
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['blocked_state.sql'],
                ),
            ],
            id='compensate next_mode feature',
        ),
        pytest.param(
            {'active_transport': {'type': 'pedestrian'}},
            {'active_transport': {'type': 'electric_bicycle'}},
            'pedestrian',
            marks=[
                pytest.mark.pgsql(
                    'driver_mode_subscription', files=['blocked_state.sql'],
                ),
            ],
            id='compensate prev_mode and next_mode feature',
        ),
    ),
)
async def test_subscription_saga_active_transport(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        taxi_config,
        mockserver,
        prev_mode_features,
        next_mode_features,
        expect_active_transport,
):
    mode_rules_data.set_mode_rules(
        rules=mode_rules.patched(
            [
                mode_rules.Patch(
                    rule_name='prev_work_mode', features=prev_mode_features,
                ),
                mode_rules.Patch(
                    rule_name='next_work_mode', features=next_mode_features,
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

    test_profile = driver.Profile(f'parkid1_uuid1')

    scene = scenario.Scene(
        profiles={test_profile: driver.Mode('prev_work_mode')},
    )
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler(
        '/contractor-transport/internal/v1/transport-active',
    )
    def _contractor_transport_mock(request):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    if expect_active_transport:
        http_request = _contractor_transport_mock.next_call()['request']
        assert http_request.query == {'contractor_id': 'parkid1_uuid1'}
        assert http_request.json == {'type': expect_active_transport}

    assert not _contractor_transport_mock.has_calls
