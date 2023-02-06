import pytest

from crons.lib import descriptions


CONST_DESCRIPTION = descriptions.TASK_DEFAULT_DESCRIPTION


@pytest.mark.config(
    DEV_TEAMS={
        'antifraud': {
            'description': 'Группа разработки антифрода Яндекс.Такси',
            'staff_groups': [
                'yandex_distproducts_browserdev_mobile_taxi_9720_3001',
            ],
        },
    },
)
@pytest.mark.parametrize(
    'params,data,expected_code,expected_data',
    [
        (
            {'name': 'logs_errors_filters-crontasks-juggler_synchronizer'},
            {
                'is_enabled': False,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'crit_threshold': 4,
                'last_launches_count': 7,
            },
            200,
            {
                'change_doc_id': (
                    'crons_tasks_logs_errors_filters-crontasks-juggler_'
                    'synchronizer'
                ),
                'data': {
                    'is_enabled': False,
                    'name': (
                        'logs_errors_filters-crontasks-juggler_synchronizer'
                    ),
                    'dev_team': 'antifraud',
                    'warn_threshold': 1,
                    'crit_threshold': 4,
                    'last_launches_count': 7,
                },
                'description': CONST_DESCRIPTION,
                'diff': {
                    'current': {
                        'crit_threshold': 4,
                        'dev_team': 'platform',
                        'is_enabled': True,
                        'monitoring_status': 'warn',
                        'name': (
                            'logs_errors_filters-crontasks-'
                            'juggler_synchronizer'
                        ),
                        'warn_threshold': 2,
                        'service': 'logs_errors_filters',
                    },
                    'new': {
                        'crit_threshold': 4,
                        'dev_team': 'antifraud',
                        'is_enabled': False,
                        'last_launches_count': 7,
                        'monitoring_status': 'warn',
                        'name': (
                            'logs_errors_filters-crontasks-'
                            'juggler_synchronizer'
                        ),
                        'warn_threshold': 1,
                        'service': 'logs_errors_filters',
                    },
                },
            },
        ),
        (
            {'name': 'logs_errors_filters-crontasks-juggler_synchronizer'},
            {
                'is_enabled': False,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'crit_threshold': 4,
                'warn_time_threshold': '20h30m15s',
                'crit_time_threshold': '1d15h',
                'last_launches_count': 7,
            },
            200,
            {
                'change_doc_id': (
                    'crons_tasks_logs_errors_filters-crontasks-juggler_'
                    'synchronizer'
                ),
                'data': {
                    'is_enabled': False,
                    'name': (
                        'logs_errors_filters-crontasks-juggler_synchronizer'
                    ),
                    'dev_team': 'antifraud',
                    'warn_threshold': 1,
                    'crit_threshold': 4,
                    'warn_time_threshold': '20h30m15s',
                    'crit_time_threshold': '1d15h',
                    'last_launches_count': 7,
                },
                'description': CONST_DESCRIPTION,
                'diff': {
                    'current': {
                        'crit_threshold': 4,
                        'dev_team': 'platform',
                        'is_enabled': True,
                        'monitoring_status': 'warn',
                        'name': (
                            'logs_errors_filters-crontasks-'
                            'juggler_synchronizer'
                        ),
                        'warn_threshold': 2,
                        'service': 'logs_errors_filters',
                    },
                    'new': {
                        'crit_threshold': 4,
                        'crit_time_threshold': '1d15h',
                        'dev_team': 'antifraud',
                        'is_enabled': False,
                        'last_launches_count': 7,
                        'monitoring_status': 'warn',
                        'name': (
                            'logs_errors_filters-crontasks-'
                            'juggler_synchronizer'
                        ),
                        'warn_threshold': 1,
                        'warn_time_threshold': '20h30m15s',
                        'service': 'logs_errors_filters',
                    },
                },
            },
        ),
        (
            {'name': 'logs_errors_filters-crontasks-juggler_synchronizer'},
            {
                'is_enabled': False,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'crit_threshold': 4,
                'warn_time_threshold': '1200m1815s',
                'crit_time_threshold': '24h900m',
                'last_launches_count': 7,
            },
            200,
            {
                'change_doc_id': (
                    'crons_tasks_logs_errors_filters-crontasks-juggler_'
                    'synchronizer'
                ),
                'data': {
                    'is_enabled': False,
                    'name': (
                        'logs_errors_filters-crontasks-juggler_synchronizer'
                    ),
                    'dev_team': 'antifraud',
                    'warn_threshold': 1,
                    'crit_threshold': 4,
                    'warn_time_threshold': '20h30m15s',
                    'crit_time_threshold': '1d15h',
                    'last_launches_count': 7,
                },
                'description': CONST_DESCRIPTION,
                'diff': {
                    'current': {
                        'crit_threshold': 4,
                        'dev_team': 'platform',
                        'is_enabled': True,
                        'monitoring_status': 'warn',
                        'name': (
                            'logs_errors_filters-crontasks-'
                            'juggler_synchronizer'
                        ),
                        'warn_threshold': 2,
                        'service': 'logs_errors_filters',
                    },
                    'new': {
                        'crit_threshold': 4,
                        'crit_time_threshold': '1d15h',
                        'dev_team': 'antifraud',
                        'is_enabled': False,
                        'last_launches_count': 7,
                        'monitoring_status': 'warn',
                        'name': (
                            'logs_errors_filters-crontasks-'
                            'juggler_synchronizer'
                        ),
                        'warn_threshold': 1,
                        'warn_time_threshold': '20h30m15s',
                        'service': 'logs_errors_filters',
                    },
                },
            },
        ),
        (
            {'name': 'logs_errors_filters-crontasks-juggler_synchronizer'},
            {
                'is_enabled': False,
                'dev_team': 'unknown_team',
                'warn_threshold': 2,
                'crit_threshold': 5,
            },
            400,
            {
                'code': 'DEV_TEAM_IS_NOT_FOUND',
                'message': 'team "unknown_team" is not found',
            },
        ),
        (
            {'name': 'unknown_task'},
            {
                'is_enabled': False,
                'dev_team': 'antifraud',
                'warn_threshold': 2,
                'crit_threshold': 5,
            },
            404,
            {
                'code': 'TASK_IS_NOT_FOUND',
                'message': 'task "unknown_task" is not found',
            },
        ),
        (
            {'name': 'logs_errors_filters-crontasks-juggler_synchronizer'},
            {
                'is_enabled': False,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'crit_threshold': 4,
                'last_launches_count': 2,
            },
            400,
            {
                'code': 'THRESHOLDS_VALIDATION_ERROR',
                'message': (
                    'crit threshold (4) must not be greater than '
                    'last launches count (2)'
                ),
            },
        ),
        (
            {'name': 'logs_errors_filters-crontasks-juggler_synchronizer'},
            {
                'is_enabled': False,
                'dev_team': 'antifraud',
                'warn_threshold': 7,
                'crit_threshold': 8,
            },
            400,
            {
                'code': 'THRESHOLDS_VALIDATION_ERROR',
                'message': (
                    'warn threshold (7) must not be greater than '
                    'last launches count (6)'
                ),
            },
        ),
        (
            {'name': 'logs_errors_filters-crontasks-juggler_synchronizer'},
            {
                'is_enabled': False,
                'dev_team': 'antifraud',
                'warn_threshold': 6,
            },
            400,
            {
                'code': 'THRESHOLDS_VALIDATION_ERROR',
                'message': (
                    'warn threshold (6) must not be greater than '
                    'crit threshold (5)'
                ),
            },
        ),
    ],
)
async def test_tasks_check_and_apply(
        web_app_client,
        web_context,
        params,
        data,
        expected_code,
        expected_data,
):
    response = await web_app_client.post(
        '/v1/tasks/check/', params=params, json=data,
    )
    assert response.status == expected_code
    response_data = await response.json()
    assert response_data == expected_data
    if expected_code == 200:
        response = await web_app_client.post(
            '/v1/tasks/apply/', json=response_data['data'],
        )
        assert response.status == 200
        doc = await web_context.mongo_wrapper.primary.cron_monitor.find_one(
            {'_id': params['name']},
        )
        assert doc
        assert doc['is_enabled'] == data['is_enabled']
        assert doc['dev_team'] == data['dev_team']
        assert doc['last_launches_count'] == data['last_launches_count']
        assert doc['warn_threshold'] == data['warn_threshold']
        assert doc['crit_threshold'] == data['crit_threshold']
