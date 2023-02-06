from typing import Any
from typing import Dict
from typing import Optional

import pytest

from tests_driver_mode_subscription import driver
from tests_driver_mode_subscription import mode_rules
from tests_driver_mode_subscription import saga_tools
from tests_driver_mode_subscription import scenario


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SEND_SUBSCRIPTION_EVENTS_TO_DMS=True,
)
@pytest.mark.parametrize(
    'unique_driver_id, expected_mode_dbid_uuid, '
    'expected_mode, expected_mode_settings, saga_id',
    (
        pytest.param(
            'udi1',
            'parkid1_uuid1',
            'orders',
            None,
            1,
            id='mode without mode_settings',
        ),
        pytest.param(
            'udi2',
            'parkid2_uuid2',
            'custom_orders',
            {'key': 'value'},
            2,
            id='mode with mode_settings',
        ),
    ),
)
async def test_subscription_saga_metrics_storage(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        mockserver,
        unique_driver_id: str,
        expected_mode_dbid_uuid: str,
        expected_mode: str,
        expected_mode_settings: Optional[Dict[str, Any]],
        saga_id: int,
):
    test_profile = driver.Profile(expected_mode_dbid_uuid)

    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    def metrics_storage_mock(request):
        return {}

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    metrics_storage_request = metrics_storage_mock.next_call()['request']

    metrics_storage_request_json = metrics_storage_request.json

    if expected_mode_settings:
        assert (
            metrics_storage_request_json.pop('extra_data')
            == expected_mode_settings
        )
    assert metrics_storage_request_json == {
        'created': '2020-04-04T11:00:00+00:00',
        'descriptor': {'tags': [expected_mode], 'type': 'subscription'},
        'idempotency_token': saga_tools.make_idempotency_key(
            saga_id, 'metrics_storage_step', False,
        ),
        'park_driver_profile_id': test_profile.dbid_uuid(),
        'type': 'work-mode',
        'unique_driver_id': unique_driver_id,
    }


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SEND_SUBSCRIPTION_EVENTS_TO_DMS=False,
)
async def test_subscription_saga_metrics_storage_disabled(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        mockserver,
):
    test_profile = driver.Profile('parkid1_uuid1')

    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time)

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)


@pytest.mark.pgsql('driver_mode_subscription', files=['sagas.sql'])
@pytest.mark.now('2020-05-01T12:00:00+0300')
@pytest.mark.mode_rules(rules=mode_rules.default_mode_rules())
@pytest.mark.config(
    DRIVER_MODE_SUBSCRIPTION_SEND_SUBSCRIPTION_EVENTS_TO_DMS=True,
)
async def test_subscription_saga_metrics_storage_failed_not_lock_driver(
        pgsql,
        mocked_time,
        taxi_driver_mode_subscription,
        mode_rules_data,
        stq_runner,
        mockserver,
):
    test_profile = driver.Profile('parkid1_uuid1')

    scene = scenario.Scene(profiles={test_profile: driver.Mode('orders')})
    scene.setup(mockserver, mocked_time)

    @mockserver.json_handler('/driver-metrics-storage/v2/event/new')
    def metrics_storage_mock(request):
        raise mockserver.TimeoutError()

    await saga_tools.call_stq_saga_task(stq_runner, test_profile)

    assert metrics_storage_mock.times_called == 3
