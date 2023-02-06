from aiohttp import web
import pytest

from taxi.stq import async_worker_ng

from operation_calculations.stq import doxgety_multidraft

GEO_NODES = [
    {
        'name': 'br_omsk',
        'name_ru': 'Омск',
        'name_en': 'Omsk',
        'node_type': 'agglomeration',
        'tariff_zones': ['omsk'],
        'parent_name': 'br_russia',
        'region_id': '194',
    },
    {
        'name': 'br_russia',
        'name_ru': 'Россия',
        'name_en': 'Russia',
        'node_type': 'country',
        'parent_name': 'br_root',
        'region_id': '225',
    },
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
]


@pytest.mark.geo_nodes(GEO_NODES)
@pytest.mark.pgsql('operation_calculations', files=['pg_doxgety.sql'])
@pytest.mark.config(
    OPERATION_CALCULATIONS_DOXGETY_RESTRICTIONS={
        '__default__': {
            'max_money_multiplier': 1.5,
            'max_proportion': 80,
            'min_aa_difficulty': 0.98,
            'min_money_multiplier': 0.4,
            'min_proportion': 20,
            'bonus': {},
            'bonus_per_goal': {},
            'goal': {},
        },
    },
    OPERATION_CALCULATIONS_DOXGETY_SETTINGS={'budget_table': ''},
)
async def test_doxgety_multidraft_pipeline(
        web_app_client,
        web_context,
        caplog,
        stq3_context,
        mock_geoareas,
        mock_taxi_tariffs,
        mock_billing_subventions_x,
        mock_taxi_agglomerations,
        mock_taxi_approvals,
        mock_tags,
        mockserver,
        patch,
        open_file,
        monkeypatch,
):
    @patch('yt.clickhouse.execute')
    def _execute(*args, **kwargs):
        return [
            {
                'tariff_zone': 'omsk',
                'money_multiplier': 0.8,
                'sum_bonus': 200,
                'budget_conversion': 4,
            },
        ]

    @mock_taxi_approvals('/multidrafts/create/')
    def _multidraft_create(request):
        return web.json_response({'id': 2})

    @mock_taxi_approvals('/drafts/1/')
    async def _get_draft_handler(request):
        return {'id': 1, 'version': 2, 'status': 'need_approval'}

    @mock_taxi_approvals('/drafts/create/')
    def _draft_create(request):
        return web.json_response(
            {
                'id': 1,
                'version': 1,
                'status': 'need_approval',
                'ticket': 'RUPRICING-1',
            },
        )

    @mock_taxi_tariffs('/v1/tariff_settings/bulk_retrieve')
    def _tariff_settings_handler(request):
        return web.json_response(
            {
                'zones': [
                    {
                        'tariff_settings': {'timezone': 'Asia/Omsk'},
                        'zone': 'omsk',
                    },
                ],
            },
        )

    @patch(
        'operation_calculations.generated.stq3.yt_wrapper.'
        'plugin.AsyncYTClient.read_table',
    )
    async def _read_table(*args):
        return [{'unique_driver_id': '12', 'bonus': 12, 'group_id': '1'}]

    @patch('taxi.clients.startrack.StartrackAPIClient.attach_file_to_ticket')
    async def _attach_file_to_ticket(*args, **kwargs):
        return {}

    md_task_creation_response = await web_app_client.post(
        '/v1/doxgety/multidraft/tasks',
        params={'task_id': 'b'},
        json={'ids': [1]},
        headers={'X-Yandex-Login': 'test_robot'},
    )
    md_task_result = await md_task_creation_response.json()
    assert md_task_creation_response.status == 200
    md_task_id = md_task_result.pop('task_id')

    md_task_status_response = await web_app_client.get(
        f'/v1/doxgety/multidraft/tasks/{md_task_id}/status',
    )
    assert md_task_status_response.status == 200
    md_task_status = await md_task_status_response.json()
    assert md_task_status['status'] == 'CREATED'

    await doxgety_multidraft.task(
        stq3_context,
        async_worker_ng.TaskInfo(
            id=md_task_id, exec_tries=0, reschedule_counter=0, queue='',
        ),
    )

    md_task_status_response = await web_app_client.get(
        f'/v1/doxgety/multidraft/tasks/{md_task_id}/status',
    )
    assert md_task_status_response.status == 200
    md_task_status = await md_task_status_response.json()
    assert md_task_status['status'] == 'COMPLETED'

    md_task_result_response = await web_app_client.get(
        f'/v1/doxgety/multidraft/tasks/{md_task_id}/result',
    )
    assert md_task_result_response.status == 200
    md_task_result = await md_task_result_response.json()
    assert md_task_result == {'multidraft_id': 2, 'ticket': 'RUPRICING-1'}
    task_result_response = await web_app_client.get(
        f'/v2/doxgety/result', params={'task_id': 'b'},
    )
    assert task_result_response.status == 200
    task_result_result = await task_result_response.json()
    assert task_result_result == {
        'cities_result': [
            {
                'aa_difficulty': 0.98,
                'aa_difficulty_active': 0.98,
                'bonus': {'max': 6800.0, 'mean': 4498, 'min': 1900},
                'bonus_per_goal': {'max': 81.8, 'mean': 46.6, 'min': 28.9},
                'budget': 100,
                'currency': 'RUB',
                'goal': {'max': 180, 'mean': 108, 'min': 30},
                'whitelist': '//home/taxi_ml/add_whitelist',
                'ttest_pvalue': 0,
            },
        ],
        'draft_id': 2,
        'ticket': 'RUPRICING-1',
        'whitelist': '//home/taxi_ml/add_whitelist_full',
    }
