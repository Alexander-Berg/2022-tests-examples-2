import pytest

from crons.lib import thresholds


@pytest.mark.parametrize(
    'params,expected_data,expected_task_names',
    [
        (
            {'limit': 1},
            [
                {
                    'is_enabled': True,
                    'service': 'logs_errors_filters',
                    'last_launches': [
                        {
                            'id': '02ab142d3bdd48fc86b3ebe43bbeae37',
                            'launch_status': 'finished',
                            'start_time': '2020-09-25T14:00:00+03:00',
                        },
                        {
                            'id': '6a1521398371463d8d6ed4cbc376fac6',
                            'launch_status': 'finished',
                            'start_time': '2020-09-25T14:01:00+03:00',
                        },
                        {
                            'id': '7a796a3a110247a1bdae267b7b4a427f',
                            'launch_status': 'finished',
                            'start_time': '2020-09-25T14:02:00+03:00',
                        },
                        {
                            'id': 'eca90d072bbc465996ef10246c5fe64e',
                            'launch_status': 'finished',
                            'start_time': '2020-09-25T14:03:00+03:00',
                        },
                        {
                            'id': '7be7e0029c034006a4aa3e58ff8a6a91',
                            'launch_status': 'finished',
                            'start_time': '2020-09-25T14:04:00+03:00',
                        },
                    ],
                    'name': (
                        'logs_errors_filters-crontasks-juggler_synchronizer'
                    ),
                    'monitoring_status': thresholds.CheckStatus.WARN.value,
                },
            ],
            None,
        ),
        (
            {'service': 'taxi_corp'},
            None,
            ['taxi_corp-stuff-send_csv_order_report'],
        ),
        (
            {'service': 'replication'},
            None,
            [
                'replication-mysql-eda_bigfood_promo_requirement_items',
                'replication-postgres-cargo_dispatch_waybill_performers',
                'replication-queue_mongo-order_offers',
            ],
        ),
        (
            {'service': 'replication', 'offset': 2},
            None,
            ['replication-queue_mongo-order_offers'],
        ),
        (
            {'name': 'cargo'},
            None,
            ['replication-postgres-cargo_dispatch_waybill_performers'],
        ),
        (
            {'service': 'replication', 'name': 'offers'},
            None,
            ['replication-queue_mongo-order_offers'],
        ),
        (
            {'monitoring_status': thresholds.CheckStatus.SUCCESS.value},
            None,
            [
                'replication-mysql-eda_bigfood_promo_requirement_items',
                'replication-postgres-cargo_dispatch_waybill_performers',
                'replication-queue_mongo-order_offers',
                'taxi_corp-stuff-send_csv_order_report',
            ],
        ),
        (
            {'monitoring_status': thresholds.CheckStatus.WARN.value},
            None,
            ['logs_errors_filters-crontasks-juggler_synchronizer'],
        ),
        (
            {'monitoring_status': thresholds.CheckStatus.CRIT.value},
            None,
            ['logs_warnings_filters-crontasks-juggler_synchronizer'],
        ),
        (
            {'is_enabled': 'true'},
            None,
            [
                'logs_errors_filters-crontasks-juggler_synchronizer',
                'logs_warnings_filters-crontasks-juggler_synchronizer',
                'replication-mysql-eda_bigfood_promo_requirement_items',
                'replication-postgres-cargo_dispatch_waybill_performers',
                'taxi_corp-stuff-send_csv_order_report',
            ],
        ),
    ],
)
async def test_tasks_list_get(
        web_app_client, params, expected_data, expected_task_names,
):
    response = await web_app_client.get('/v1/tasks/list/', params=params)
    assert response.status == 200
    data = (await response.json())['tasks']
    if expected_data is not None:
        assert data == expected_data
    if expected_task_names is not None:
        assert [task['name'] for task in data] == expected_task_names
