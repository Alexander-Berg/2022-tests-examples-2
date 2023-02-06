import uuid

import pytest


@pytest.mark.parametrize(
    'operation_id, expected_status, '
    'expected_data, expected_approvals_request,'
    'expected_summary, expected_description',
    (
        pytest.param(
            'be109b72119e37321188f84717646b96',
            200,
            {
                'created_at': '2020-01-01T12:00:00+03:00',
                'created_by': 'robot',
                'draft_id': 1,
                'id': 'be109b72119e37321188f84717646b96',
                'meta': {
                    'brand': {
                        'charts': [],
                        'guarantees': [
                            {'count_trips': 1, 'guarantee': 0.0},
                            {'count_trips': 2, 'guarantee': 20.0},
                        ],
                        'result': {
                            'do_x_get_y_subs_fact': 0.0,
                            'fact_nmfg_subs': 0.856,
                            'fact_subs': 0.856,
                            'geo_subs_fact': 34223.0,
                            'gmv': 1635.0,
                            'plan_nmfg_subs': 32423.0,
                            'plan_subs': 23134.0,
                        },
                    },
                },
                'params': {
                    'a1': 5,
                    'a2': 0,
                    'commission': 10,
                    'end_date': '2021-01-01',
                    'hours': [1, 2, 3, 5, 7, 10, 11, 12],
                    'm': 20,
                    'maxtrips': 1,
                    'price_increase': 1.5,
                    'start_date': '2020-01-01',
                    'sub_brand': 170317,
                    'subvenion_end_date': '2021-01-01',
                    'subvenion_start_date': '2020-01-01',
                    'tariff_zone': 'moscow',
                    'tariffs': ['econom'],
                    'type': 'brand-nmfg-subventions',
                    'week_days': ['mon'],
                },
                'status': 'DRAFT_CREATED',
                'updated_at': '2020-01-01T04:00:00+03:00',
                'updated_by': 'cron_task',
            },
            {
                'api_path': 'nmfg_subventions_create',
                'data': {
                    'rules': [
                        {
                            'begin_at': '2020-01-01',
                            'budget': {
                                'id': '31b2df8d-0cbb-49ae-bce7-8469bfc3c487',
                                'rolling': True,
                                'threshold': 120,
                                'weekly': '32423.0',
                            },
                            'end_at': '2021-01-01',
                            'has_commission': False,
                            'hours': [1, 2, 3, 5, 7, 10, 11, 12],
                            'id': 'brandbe109b72119e37321188f84717646b96',
                            'is_net': False,
                            'kind': 'daily_guarantee',
                            'steps': [[1, '0.0'], [2, '20.0']],
                            'tariff_classes': ['econom'],
                            'week_days': ['mon'],
                            'zone': 'moscow',
                        },
                    ],
                },
                'mode': 'push',
                'request_id': 'be109b72119e37321188f84717646b96',
                'run_manually': False,
                'service_name': 'billing_subventions',
            },
            'nMFG-tool /moscow - econom. 01.01.2020-01.01.2021',
            'description.txt',
            id='Ok',
        ),
    ),
)
@pytest.mark.now('2020-01-01T01:00:00')
@pytest.mark.pgsql('operation_calculations', files=['pg.sql'])
async def test_v1_operations_operation_id_create_draft_post(
        web_app_client,
        operation_id,
        expected_status,
        expected_data,
        expected_approvals_request,
        mockserver,
        patch,
        expected_summary,
        expected_description,
        load,
):
    approvals_request = {}

    @patch('uuid.uuid4')
    def _uuid4():
        return uuid.UUID('31b2df8d-0cbb-49ae-bce7-8469bfc3c487')

    @mockserver.json_handler('/taxi-approvals/drafts/create/')
    async def _approvals_handler(request):
        nonlocal approvals_request
        approvals_request = request.json
        return {'id': 1, 'version': 3}

    response = await web_app_client.post(
        f'/v1/operations/{operation_id}/create_draft/',
        headers={'X-Yandex-Login': 'robot'},
    )
    assert response.status == expected_status, await response.text()
    assert await response.json() == expected_data
    tickets = approvals_request.pop('tickets')
    assert approvals_request == expected_approvals_request
    assert tickets['create_data']['summary'] == expected_summary
    assert tickets['create_data']['description'] == (
        load(expected_description).strip()
    )
