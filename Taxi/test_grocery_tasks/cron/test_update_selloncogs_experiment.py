from aiohttp import web
import pytest

from grocery_tasks.generated.cron import run_cron
from grocery_tasks.selloncogs.modifiers.storekeepers import update_storekeepers


@pytest.mark.translations(wms_items={})
@pytest.mark.config(
    TAXI_EXP_CLIENT_SETTINGS={
        '__default__': {
            '__default__': {
                'num_retries': 0,
                'retry_delay_ms': [50],
                'request_timeout_ms': 10000,
            },
        },
    },
)
@pytest.mark.now('2020-02-03T00:00:00.000000+00:00')
@pytest.mark.yt(
    static_table_data=[
        'yt/normalized_user_phones.yaml',
        'yt/user_phones.yaml',
        'yt/storekeepers_stores.yaml',
    ],
)
async def test_update_storekeepers(
        patch, mockserver, cron_runner, load_json, yt_apply, mock_geobase,
):
    stored_file_id = 'stored_file_id_here'

    @patch(
        'grocery_tasks.selloncogs.update_selloncogs_experiment._get_modifiers_list',  # noqa: E501
    )
    def _get_modifiers_list():
        return [update_storekeepers]

    @mock_geobase('/v1/region_by_id')
    def _handler_region_by_id(request):
        _regions = {
            0: {'en_name': 'Europe'},
            131: {'en_name': 'Israel', 'parent_id': 0},
            10393: {'en_name': 'United Kingdom', 'parent_id': 0},
            10502: {'en_name': 'France', 'parent_id': 0},
            213: {'en_name': 'Russia', 'parent_id': 0},
        }
        return _regions.get(
            int(request.query['id']), mock_geobase.make_response(status=400),
        )

    @mockserver.handler('/taxi-exp/v1/files/')
    async def _exp_files(request):
        assert set(request.get_data().decode('utf-8').split('\n')) == {
            '+444532135351',
            '+79096498967',
            '+972645979637',
        }
        return web.json_response(
            data={'id': stored_file_id, 'lines': 3, 'hash': 'file_hash'},
        )

    @mockserver.json_handler('/taxi-exp/v1/configs/')
    async def _exp_get(request):
        if request.method == 'GET':
            return load_json('exp_couriers_initial.json')
        if request.method == 'PUT':
            for clause in request.json['clauses']:
                if (
                        clause['predicate']['type'] == 'in_file'
                        and clause['value']['type'] == 'storekeepers'
                ):
                    assert (
                        clause['predicate']['init']['file'] == stored_file_id
                    )
                    return {}
        assert False

    await run_cron.main(
        ['grocery_tasks.crontasks.selloncogs_update_experiment', '-t', '0'],
    )

    assert _exp_files.times_called == 1
    assert _exp_get.times_called == 2


# TODO: add tests for update_staff, update_couriers
