import datetime

import pytest


ASSIGNMENT_METRIC_PREFIX = (
    'alt_offer_discount_metrics.dolgoprudniy.assignment.'
)

PROCESSING_METRIC_PREFIX = (
    'alt_offer_discount_metrics.dolgoprudniy.processing.'
)


@pytest.mark.parametrize(
    'testcase_name',
    ['created', 'assigned', 'complete', 'failed', 'long_search/assigned'],
)
@pytest.mark.now('2021-12-27T16:38:00.000000+0000')
async def test_stq_metrics(
        testcase_name,
        stq_runner,
        taxi_alt_offer_discount,
        taxi_alt_offer_discount_monitor,
        load_json,
        mocked_time,
):
    for kwargs in load_json(f'{testcase_name}_stq_kwargs.json'):
        await stq_runner.alt_offer_discount_metrics.call(
            task_id='alt_offer_discount_metrics', args=[], kwargs=kwargs,
        )
    mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=15))
    await taxi_alt_offer_discount.tests_control(invalidate_caches=False)

    metrics = await taxi_alt_offer_discount_monitor.get_metric(
        'alt_offer_discount_metrics',
    )

    assert metrics == load_json(f'{testcase_name}_metrics.json')


@pytest.mark.parametrize(
    'params, alternative_type, expected_metrics',
    [
        ({'chain_supply_time_s': 177}, 'perfect_chain', 'error'),
        ({'chain_supply_time_s': 176}, 'perfect_chain', 'success'),
        ({'chain_supply_time_s': 177}, 'long_search', None),
        ({'chain_supply_time_s': 176}, 'long_search', None),
        ({'chain_supply_time_s': 177}, 'unknown_type', None),
        ({'chain_supply_time_s': 176}, 'unknown_type', None),
        (None, 'perfect_chain', None),
        (None, 'long_search', None),
        (None, 'unknown_type', None),
    ],
)
@pytest.mark.now('2021-12-27T16:38:00.000000+0000')
@pytest.mark.experiments3(
    filename='alt_offer_discount_check_assignment_exp3.json',
)
async def test_check_assignment(
        stq_runner,
        taxi_alt_offer_discount,
        load_json,
        mocked_time,
        params,
        alternative_type,
        expected_metrics,
        statistics,
):
    kwargs = load_json('assigned_stq_kwargs.json')[0]
    kwargs['order_event'].update({'alternative_type': alternative_type})
    if params is not None:
        kwargs['order_event'].update({'params': params})
    else:
        kwargs['order_event'].pop('params')

    async with statistics.capture(taxi_alt_offer_discount) as capture:
        await stq_runner.alt_offer_discount_metrics.call(
            task_id='alt_offer_discount_metrics', args=[], kwargs=kwargs,
        )
    await taxi_alt_offer_discount.tests_control(invalidate_caches=True)
    if expected_metrics is not None:
        metric_name = ASSIGNMENT_METRIC_PREFIX + expected_metrics
        assert metric_name in capture.statistics
        assert capture.statistics[metric_name] == 1
    else:
        assert (ASSIGNMENT_METRIC_PREFIX + 'success') not in capture.statistics
        assert (ASSIGNMENT_METRIC_PREFIX + 'error') not in capture.statistics


@pytest.mark.parametrize(
    'params, expected_metrics',
    [
        ({'chain_supply_time_s': 177}, 'success'),
        ({'qwerty': 176}, 'error'),
        (None, 'error'),
        ({'chain_supply_time_s': 177, 'is_long_search': True}, None),
    ],
)
@pytest.mark.now('2021-12-27T16:38:00.000000+0000')
@pytest.mark.experiments3(
    filename='alt_offer_discount_check_assignment_exp3.json',
)
async def test_check_processing(
        stq_runner,
        taxi_alt_offer_discount,
        load_json,
        mocked_time,
        params,
        expected_metrics,
        statistics,
):
    kwargs = load_json('assigned_stq_kwargs.json')[0]
    if params is not None:
        kwargs['order_event'].update({'params': params})
    else:
        kwargs['order_event'].pop('params')

    async with statistics.capture(taxi_alt_offer_discount) as capture:
        await stq_runner.alt_offer_discount_metrics.call(
            task_id='alt_offer_discount_metrics', args=[], kwargs=kwargs,
        )
    await taxi_alt_offer_discount.tests_control(invalidate_caches=True)
    if expected_metrics is not None:
        metric_name = PROCESSING_METRIC_PREFIX + expected_metrics
        assert metric_name in capture.statistics
        assert capture.statistics[metric_name] == 1
    else:
        assert (PROCESSING_METRIC_PREFIX + 'success') not in capture.statistics
        assert (PROCESSING_METRIC_PREFIX + 'error') not in capture.statistics
