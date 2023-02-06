import pytest

from taxi.stq import async_worker_ng

import operation_calculations.geosubventions.storage as storage_lib
from operation_calculations.stq import doxgety_nirvana


@pytest.mark.pgsql('operation_calculations', files=['pg_doxgety.sql'])
@pytest.mark.config(
    OPERATION_CALCULATIONS_DOXGETY_RESTRICTIONS={
        '__default__': {
            'min_proportion': 20,
            'max_proportion': 80,
            'min_money_multiplier': 0.4,
            'max_money_multiplier': 1.5,
            'min_aa_difficulty': 0.98,
            'bonus': {
                'max': {
                    'critical': {'max': 5000, 'min': 0},
                    'warning': {'max': 4000, 'min': 2000},
                },
            },
            'bonus_per_goal': {},
            'goal': {
                'mean': {
                    'warning': {'max': 100, 'min': 80},
                    'critical': {'max': 120, 'min': 60},
                },
            },
        },
    },
    OPERATION_CALCULATIONS_DOXGETY_SETTINGS={
        'algorithms': [
            {
                'instance_id': 'd5d246e6-9e64-4f10-a561-380ab1d80a17',
                'name': '__default__',
                'workflow_id': 'f91b237d-21ad-433f-bc1f-3e0e209ccb44',
            },
        ],
        'money_multiplier': 0.8,
        'targets_complexity': '0.97',
        'budget_table': '//home/',
    },
)
async def test_task(stq3_context, mockserver, patch, mock, monkeypatch):
    @patch('yt.clickhouse.execute')
    def _execute(*args, **kwargs):
        query = args[0]
        if 'sum_bonus' in query:
            return [
                {
                    'tariff_zone': 'omsk',
                    'money_multiplier': 0.8,
                    'sum_bonus': 200,
                    'budget_conversion': 4,
                },
            ]
        return [
            {
                'id': '1',
                'aa_difficulty': 0.98,
                'aa_difficulty_active': 0.98,
                'Goal_min_value': 30,
                'Goal_mean_value': 108,
                'Goal_max_value': 180,
                'Bonus_amount_min_value': 1900,
                'Bonus_amount_mean_value': 4498,
                'Bonus_amount_max_value': 6800.0,
                'Bonus_amount_per_goal_min_value': 28.9,
                'Bonus_amount_per_goal_mean_value': 46.6,
                'Bonus_amount_per_goal_max_value': 81.8,
                'description': None,
                'table': '//home/taxi_ml/add_whitelist',
                'version': '2022-04-15T13:33:32.579548Z',
                'budget': 50000,
                'currency': 'RUB',
                'drivers_cnt': 121.0,
                'start_date': '2022-04-16 21:00:00',
                'end_date': '2022-04-23 21:00:00',
                'ticket': 'DXGYTEST-155',
            },
        ]

    @mockserver.json_handler('/nirvana-api/getExecutionState')
    async def _state_handler(request):
        return {'result': {'status': 'COMPLETED', 'result': 'SUCCESS'}}

    @mockserver.json_handler('/nirvana-api/getBlockResults')
    async def _result_handler(request):
        return {
            'result': [
                {
                    'blockGuid': '1e45909c-9526-4382-a540-75bf86239de6',
                    'blockCode': 'do_x_get_y_taxi_atlas',
                    'results': [
                        {
                            'endpoint': 'add_whitelist',
                            'directStoragePath': 'yt_draft_table',
                        },
                        {
                            'endpoint': 'yt_draft_table',
                            'directStoragePath': 'yt_draft_table',
                        },
                    ],
                },
            ],
        }

    @mock
    async def _request_mock(*args, **kwargs):
        class ResponseStub:
            async def read(self):
                return res

        if kwargs['url'] == 'yt_draft_table':
            res = b'{"cluster":"hahn",' b'"table":"//home/taxi_ml"}'
        else:
            res = b'{"cluster":"hahn",' b'"table":"//home/taxi_ml"}'
        return ResponseStub()

    monkeypatch.setattr(stq3_context.client_http, 'get', _request_mock)

    await doxgety_nirvana.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id='1', exec_tries=0, reschedule_counter=1, queue='',
        ),
    )

    storage = storage_lib.DoxgetyStorage(stq3_context)
    status = await storage.get_doxgety_task_status('1')
    assert status['status'] == 'SUCCESS'
    res = await storage.get_doxgety_task_result('1', as_single_city=False)
    assert dict(res) == {
        'draft_id': None,
        'error': None,
        'id': '1',
        'is_multidraft': None,
        'result': {
            'budget': 320.0,
            'whitelist': '//home/taxi_ml',
            'cities_result': [
                {
                    'aa_difficulty': 0.98,
                    'aa_difficulty_active': 0.98,
                    'bonus': {'max': 6800.0, 'mean': 4498, 'min': 1900},
                    'bonus_per_goal': {'max': 81.8, 'mean': 46.6, 'min': 28.9},
                    'budget': 320.0,
                    'currency': 'RUB',
                    'drivers_cnt': 121,
                    'goal': {'max': 180, 'mean': 108, 'min': 30},
                    'id': 1,
                    'warnings': [
                        {
                            'kind': 'critical',
                            'max': 5000,
                            'min': 0,
                            'name': 'bonus',
                            'sub_name': 'max',
                            'value': 6800.0,
                        },
                        {
                            'kind': 'warning',
                            'max': 100,
                            'min': 80,
                            'name': 'goal',
                            'sub_name': 'mean',
                            'value': 108,
                        },
                    ],
                    'whitelist': '//home/taxi_ml/add_whitelist',
                },
            ],
        },
    }
