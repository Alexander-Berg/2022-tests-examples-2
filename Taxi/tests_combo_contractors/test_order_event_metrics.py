import datetime

import pytest


@pytest.mark.parametrize(
    'testcase_name',
    [
        'econom_created',
        'econom_transporting',
        'econom_matched',
        'econom_finished',
    ],
)
@pytest.mark.now('2018-12-27T16:38:00.000000+0000')
async def test_combo_order_metrics(
        testcase_name,
        stq_runner,
        taxi_combo_contractors,
        taxi_combo_contractors_monitor,
        load_json,
        mocked_time,
):
    for kwargs in load_json(f'v2_{testcase_name}.json'):
        await stq_runner.combo_order_metrics.call(
            task_id='combo_order_metrics', args=[], kwargs=kwargs,
        )

    mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=15))
    await taxi_combo_contractors.tests_control(invalidate_caches=False)
    metrics = await taxi_combo_contractors_monitor.get_metric(
        'combo_contractors_metrics',
    )
    assert metrics == load_json(f'v2_{testcase_name}_metrics.json')
