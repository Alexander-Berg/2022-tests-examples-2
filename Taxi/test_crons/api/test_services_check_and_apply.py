import pytest

from crons.lib import descriptions


CONST_DESCRIPTION = descriptions.SERVICE_DEFAULT_DESCRIPTION


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
            {'name': 'logs_errors_filters'},
            {
                'crit_threshold': 4,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'last_launches_count': 7,
            },
            200,
            {
                'change_doc_id': 'crons_services_logs_errors_filters',
                'data': {
                    'warn_threshold': 1,
                    'crit_threshold': 4,
                    'name': 'logs_errors_filters',
                    'dev_team': 'antifraud',
                    'last_launches_count': 7,
                },
                'description': CONST_DESCRIPTION,
                'diff': {
                    'current': {
                        'crit_threshold': 5,
                        'crit_time_threshold': '0s',
                        'dev_team': 'platform',
                        'last_launches_count': 6,
                        'name': 'logs_errors_filters',
                        'warn_threshold': 2,
                        'warn_time_threshold': '0s',
                    },
                    'new': {
                        'crit_threshold': 4,
                        'crit_time_threshold': '0s',
                        'dev_team': 'antifraud',
                        'last_launches_count': 7,
                        'name': 'logs_errors_filters',
                        'warn_threshold': 1,
                        'warn_time_threshold': '0s',
                    },
                },
            },
        ),
        (
            {'name': 'logs_errors_filters'},
            {
                'crit_threshold': 5,
                'dev_team': 'unknown_team',
                'warn_threshold': 2,
                'last_launches_count': 7,
            },
            400,
            {
                'code': 'DEV_TEAM_IS_NOT_FOUND',
                'message': 'team "unknown_team" is not found',
            },
        ),
        (
            {'name': 'unknown_service'},
            {
                'crit_threshold': 5,
                'dev_team': 'antifraud',
                'warn_threshold': 2,
                'last_launches_count': 7,
            },
            404,
            {
                'code': 'SERVICE_IS_NOT_FOUND',
                'message': 'service "unknown_service" is not found',
            },
        ),
        (
            {'name': 'logs_errors_filters'},
            {
                'crit_threshold': 2,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'last_launches_count': 3,
            },
            400,
            {
                'code': 'THRESHOLDS_VALIDATION_ERROR',
                'message': (
                    'crit threshold (4) must not be greater than '
                    'last launches count (3) for task "logs_errors_'
                    'filters-crontasks-juggler_synchronizer"'
                ),
            },
        ),
        (
            {'name': 'logs_errors_filters'},
            {
                'crit_threshold': 4,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'last_launches_count': 7,
                'warn_time_threshold': '2m30s',
                'crit_time_threshold': '1h2m30s',
            },
            200,
            {
                'change_doc_id': 'crons_services_logs_errors_filters',
                'data': {
                    'warn_threshold': 1,
                    'crit_threshold': 4,
                    'warn_time_threshold': '2m30s',
                    'crit_time_threshold': '1h2m30s',
                    'name': 'logs_errors_filters',
                    'dev_team': 'antifraud',
                    'last_launches_count': 7,
                },
                'description': CONST_DESCRIPTION,
                'diff': {
                    'current': {
                        'crit_threshold': 5,
                        'crit_time_threshold': '0s',
                        'dev_team': 'platform',
                        'last_launches_count': 6,
                        'name': 'logs_errors_filters',
                        'warn_threshold': 2,
                        'warn_time_threshold': '0s',
                    },
                    'new': {
                        'crit_threshold': 4,
                        'crit_time_threshold': '1h2m30s',
                        'dev_team': 'antifraud',
                        'last_launches_count': 7,
                        'name': 'logs_errors_filters',
                        'warn_threshold': 1,
                        'warn_time_threshold': '2m30s',
                    },
                },
            },
        ),
        (
            {'name': 'logs_errors_filters'},
            {
                'crit_threshold': 4,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'last_launches_count': 7,
                'warn_time_threshold': '1h2m30s',
                'crit_time_threshold': '2m30s',
            },
            400,
            {
                'code': 'THRESHOLDS_VALIDATION_ERROR',
                'message': (
                    'warn time threshold (1h2m30s) must not be greater '
                    'than crit time threshold (2m30s) for task "logs_errors_'
                    'filters-crontasks-juggler_synchronizer"'
                ),
            },
        ),
        (
            {'name': 'logs_errors_filters'},
            {
                'crit_threshold': 4,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'last_launches_count': 7,
                'warn_time_threshold': '2m 65s',
                'crit_time_threshold': ' 80m 100s ',
            },
            200,
            {
                'change_doc_id': 'crons_services_logs_errors_filters',
                'data': {
                    'warn_threshold': 1,
                    'crit_threshold': 4,
                    'warn_time_threshold': '3m5s',
                    'crit_time_threshold': '1h21m40s',
                    'name': 'logs_errors_filters',
                    'dev_team': 'antifraud',
                    'last_launches_count': 7,
                },
                'description': CONST_DESCRIPTION,
                'diff': {
                    'current': {
                        'crit_threshold': 5,
                        'crit_time_threshold': '0s',
                        'dev_team': 'platform',
                        'last_launches_count': 6,
                        'name': 'logs_errors_filters',
                        'warn_threshold': 2,
                        'warn_time_threshold': '0s',
                    },
                    'new': {
                        'crit_threshold': 4,
                        'crit_time_threshold': '1h21m40s',
                        'dev_team': 'antifraud',
                        'last_launches_count': 7,
                        'name': 'logs_errors_filters',
                        'warn_threshold': 1,
                        'warn_time_threshold': '3m5s',
                    },
                },
            },
        ),
        (
            {'name': 'logs_errors_filters'},
            {
                'crit_threshold': 4,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'last_launches_count': 7,
                'warn_time_threshold': '0s',
                'crit_time_threshold': '0s',
            },
            200,
            {
                'change_doc_id': 'crons_services_logs_errors_filters',
                'data': {
                    'warn_threshold': 1,
                    'crit_threshold': 4,
                    'warn_time_threshold': '0s',
                    'crit_time_threshold': '0s',
                    'name': 'logs_errors_filters',
                    'dev_team': 'antifraud',
                    'last_launches_count': 7,
                },
                'description': CONST_DESCRIPTION,
                'diff': {
                    'current': {
                        'crit_threshold': 5,
                        'crit_time_threshold': '0s',
                        'dev_team': 'platform',
                        'last_launches_count': 6,
                        'name': 'logs_errors_filters',
                        'warn_threshold': 2,
                        'warn_time_threshold': '0s',
                    },
                    'new': {
                        'crit_threshold': 4,
                        'crit_time_threshold': '0s',
                        'dev_team': 'antifraud',
                        'last_launches_count': 7,
                        'name': 'logs_errors_filters',
                        'warn_threshold': 1,
                        'warn_time_threshold': '0s',
                    },
                },
            },
        ),
        (
            {'name': 'logs_errors_filters'},
            {
                'crit_threshold': 4,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'last_launches_count': 7,
                'warn_time_threshold': '2m 65s',
                'crit_time_threshold': ' 100s 80m ',
            },
            400,
            {
                'code': 'THRESHOLDS_VALIDATION_ERROR',
                'message': (
                    'wrong format for crit time threshold: " 100s 80m " '
                    'for task "logs_errors_filters-crontasks-juggler_'
                    'synchronizer"'
                ),
            },
        ),
        (
            {'name': 'logs_errors_filters'},
            {
                'crit_threshold': 4,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'last_launches_count': 7,
                'warn_time_threshold': '',
                'crit_time_threshold': '',
            },
            400,
            {
                'code': 'THRESHOLDS_VALIDATION_ERROR',
                'message': (
                    'wrong format for warn time threshold: "" for task '
                    '"logs_errors_filters-crontasks-juggler_synchronizer"'
                ),
            },
        ),
        (
            {'name': 'logs_errors_filters'},
            {
                'crit_threshold': 4,
                'dev_team': 'antifraud',
                'warn_threshold': 1,
                'last_launches_count': 7,
                'warn_time_threshold': '2m 65s',
                'crit_time_threshold': '4r',
            },
            400,
            {
                'code': 'THRESHOLDS_VALIDATION_ERROR',
                'message': (
                    'wrong format for crit time threshold: "4r" '
                    'for task "logs_errors_filters-crontasks-juggler_'
                    'synchronizer"'
                ),
            },
        ),
    ],
)
async def test_services_check_and_apply(
        web_app_client,
        web_context,
        params,
        data,
        expected_code,
        expected_data,
):
    response = await web_app_client.post(
        '/v1/services/check/', params=params, json=data,
    )
    assert response.status == expected_code
    response_data = await response.json()
    assert response_data == expected_data
    if expected_code != 200:
        return
    response = await web_app_client.post(
        '/v1/services/apply/', json=response_data['data'],
    )
    assert response.status == 200
    doc = await web_context.mongo_wrapper.primary.cron_services.find_one(
        {'_id': params['name']},
    )
    assert doc
    assert doc['dev_team'] == data['dev_team']
    assert doc['last_launches_count'] == data['last_launches_count']
    assert doc['warn_threshold'] == data['warn_threshold']
    assert doc['crit_threshold'] == data['crit_threshold']
    assert doc.get('warn_time_threshold') == expected_data['data'].get(
        'warn_time_threshold',
    )
    assert doc.get('crit_time_threshold') == expected_data['data'].get(
        'crit_time_threshold',
    )

    if expected_data['data'].get('warn_time_threshold'):
        response_data['data']['warn_time_threshold'] = data[
            'warn_time_threshold'
        ]
        response_data['data']['crit_time_threshold'] = data[
            'crit_time_threshold'
        ]
        response = await web_app_client.post(
            '/v1/services/apply/', json=response_data['data'],
        )
        assert response.status == 200
        doc = await web_context.mongo_wrapper.primary.cron_services.find_one(
            {'_id': params['name']},
        )
        assert doc.get('warn_time_threshold') == expected_data['data'].get(
            'warn_time_threshold',
        )
        assert doc.get('crit_time_threshold') == expected_data['data'].get(
            'crit_time_threshold',
        )
        assert response_data['description'] == CONST_DESCRIPTION
