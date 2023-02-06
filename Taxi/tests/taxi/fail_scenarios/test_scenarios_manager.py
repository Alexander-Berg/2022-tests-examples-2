import datetime

import pytest

from taxi import config as config_module
from taxi.fail_scenarios import fail_scenarios


@pytest.mark.parametrize(
    ('time', 'expected_active'),
    [
        pytest.param(
            datetime.datetime(
                2019, 7, 19, 8, 59, tzinfo=fail_scenarios.SERVER_TIMEZONE,
            ),
            False,
            marks=[pytest.mark.now('2019-07-19T12:00:00+0300')],
        ),
        pytest.param(
            datetime.datetime(
                2019, 7, 19, 9, 00, tzinfo=fail_scenarios.SERVER_TIMEZONE,
            ),
            True,
            marks=[pytest.mark.now('2019-07-19T12:00:00+0300')],
        ),
        pytest.param(
            datetime.datetime(
                2019, 7, 19, 18, 59, tzinfo=fail_scenarios.SERVER_TIMEZONE,
            ),
            True,
            marks=[pytest.mark.now('2019-07-19T12:00:00+0300')],
        ),
        pytest.param(
            datetime.datetime(
                2019, 7, 19, 19, 00, tzinfo=fail_scenarios.SERVER_TIMEZONE,
            ),
            True,
            marks=[pytest.mark.now('2019-07-19T12:00:00+0300')],
        ),
        pytest.param(
            datetime.datetime(
                2019, 7, 19, 23, 00, tzinfo=fail_scenarios.SERVER_TIMEZONE,
            ),
            False,
            marks=[pytest.mark.now('2019-07-19T12:00:00+0300')],
        ),
        pytest.param(
            datetime.datetime(
                2019, 7, 20, 12, 00, tzinfo=fail_scenarios.SERVER_TIMEZONE,
            ),
            False,
            marks=[pytest.mark.now('2019-07-20T12:00:00+0300')],
        ),  # Weekend
        pytest.param(
            datetime.datetime(
                2019, 7, 21, 12, 00, tzinfo=fail_scenarios.SERVER_TIMEZONE,
            ),
            False,
            marks=[pytest.mark.now('2019-07-21T12:00:00+0300')],
        ),  # Weekend
    ],
)
async def test_fail_manager(time, expected_active, db, stub):
    class MockConfig(config_module.Config):
        FAIL_SCENARIOS_MANAGER_CONFIG = [
            {
                'enabled': True,
                'desc': 'for tests',
                'start_hour': 9,
                'end_hour': 19,
                'only_weekdays': True,
                'type': 'postgres_unavailable',
                'times_per_day': 1,
                'min_duration_seconds': datetime.timedelta(hours=10).seconds,
                'max_duration_seconds': datetime.timedelta(hours=10).seconds,
                'metric_name': 'integration_auth_fail_scenario_active',
            },
        ]

    async def _mock_push_data(*args):
        pass

    mock_solomon_client = stub(push_data=_mock_push_data)
    config = MockConfig(db)
    context = stub(config=config, client_solomon=mock_solomon_client)
    fail_manager = fail_scenarios.FailScenariosManager(
        config_name='FAIL_SCENARIOS_MANAGER_CONFIG',
        context=context,
        app_name='test_app',
    )
    await fail_manager.refresh_cache()
    is_active = fail_manager.is_active_at(
        time, fail_type=fail_scenarios.FailType.POSTGRES_UNAVAILABLE,
    )
    assert is_active == expected_active
