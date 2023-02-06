import pytest

from . import models


@pytest.fixture(name='debts_metric_setting_exp')
async def _debts_metric_setting_exp(experiments3, taxi_grocery_user_debts):
    async def wrapper(interval_duration, interval_label):
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='grocery_user_debts_metric_settings',
            consumers=['grocery-user-debts/empty-kwargs'],
            clauses=[],
            default_value={
                'delay_hours': 0,
                'intervals': [
                    {
                        'label_name': interval_label,
                        'duration': interval_duration,
                    },
                ],
            },
        )
        await taxi_grocery_user_debts.invalidate_caches()

    return wrapper


async def test_metric(
        grocery_user_debts_db,
        taxi_grocery_user_debts,
        taxi_grocery_user_debts_monitor,
        debts_metric_setting_exp,
        testpoint,
):
    interval_duration = 24
    interval_label = '1 day'

    await debts_metric_setting_exp(
        interval_duration=interval_duration, interval_label=interval_label,
    )

    grocery_user_debts_db.upsert(models.Debt())

    @testpoint('update-metrics-finished')
    def metric_update_finished(data):
        return

    await taxi_grocery_user_debts.enable_testpoints()

    async with taxi_grocery_user_debts.spawn_task('metrics-collector'):
        await metric_update_finished.wait_call()

    metrics = await taxi_grocery_user_debts_monitor.get_metric(
        'metrics-collector',
    )

    all_debts_metric = metrics['grocery_user_debts_all_debts']

    expected_metric = {
        interval_label: {
            'init': {
                'card': {
                    'grocery': 1,
                    '$meta': {'solomon_children_labels': 'originator'},
                },
                '$meta': {'solomon_children_labels': 'payment_type'},
            },
            '$meta': {'solomon_children_labels': 'status'},
        },
        '$meta': {'solomon_children_labels': 'duration'},
    }

    assert all_debts_metric == expected_metric
