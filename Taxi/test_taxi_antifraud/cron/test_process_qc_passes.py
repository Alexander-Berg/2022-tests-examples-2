from aiohttp import web
import pytest

from taxi_antifraud.crontasks import process_qc_passes
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import state

CURSOR_STATE_NAME = process_qc_passes.CURSOR_STATE_NAME


@pytest.mark.config(
    AFS_CRON_PROCESS_QC_PASSES_ENABLED=True,
    AFS_CHECK_QC_PASSES_EXAMS_TO_PROCESS=['dkk'],
    AFS_CRON_CURSOR_USE_PGSQL='disabled',
)
async def test_cron(mock_quality_control_py3, mock_antifraud_py, cron_context):
    @mock_quality_control_py3('/api/v1/pass/list')
    async def api_v1_pass_list(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == 'end':
            return web.json_response(
                data=dict(
                    modified='2020-01-01T00:00:00', cursor='end', items=[],
                ),
            )
        return web.json_response(
            data=dict(
                modified='2020-01-01T00:00:00',
                cursor='end',
                items=[
                    {
                        'id': '',
                        'status': 'NEW',
                        'entity_id': '',
                        'exam': 'dkk',
                        'entity_type': '',
                        'modified': '2020-01-01T00:00:00',
                        'media': [{'url': '', 'code': '', 'required': True}],
                    },
                    {
                        'id': '',
                        'status': 'NEW',
                        'entity_id': '',
                        'exam': 'dkk',
                        'entity_type': '',
                        'modified': '2020-01-01T00:00:00',
                        'media': [{'url': '', 'code': '', 'required': True}],
                    },
                    {
                        'id': '',
                        'status': 'NEW',
                        'entity_id': '',
                        'exam': 'dkk',
                        'entity_type': '',
                        'modified': '2020-01-01T00:00:00',
                        'media': [{'code': '', 'required': True}],
                    },
                ],
            ),
        )

    @mock_antifraud_py('/v1/check_qc_pass')
    async def api_v1_check_qc_pass(request):
        assert request.method == 'POST'
        return web.json_response(data=dict())

    master_pool = cron_context.pg.master_pool
    await state.initialize_state_table(master_pool, CURSOR_STATE_NAME)

    await run_cron.main(
        ['taxi_antifraud.crontasks.process_qc_passes', '-t', '0'],
    )

    assert api_v1_pass_list.times_called == 2
    assert api_v1_check_qc_pass.times_called == 2
