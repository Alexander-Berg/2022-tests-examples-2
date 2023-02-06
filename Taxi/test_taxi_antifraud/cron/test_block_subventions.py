from aiohttp import web
import pytest

from taxi_antifraud.crontasks import block_subventions
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import data as data_module
from test_taxi_antifraud.cron.utils import state

CURSOR_STATE_NAME = block_subventions.CURSOR_STATE_NAME

YT_DIRECTORY_PATH = '//home/taxi-fraud/unittests/kopatel'
YT_TABLE_PATH = YT_DIRECTORY_PATH + '/to_block'


@pytest.mark.config(
    AFS_CRON_BLOCK_SUBVENTIONS_ENABLED=True,
    AFS_CRON_BLOCK_SUBVENTIONS_INPUT_TABLE_SUFFIX='kopatel/to_block',
    AFS_CRON_BLOCK_SUBVENTIONS_SLEEP_TIME_SECONDS=0.01,
    AFS_CRON_CURSOR_USE_PGSQL='enabled',
)
async def test_cron(mock_antifraud, yt_apply, yt_client, cron_context, db):
    @mock_antifraud('/v1/subventions/change_billing_status')
    def _change_billing_status(request):
        assert request.method == 'POST'
        assert request.json == {
            'action': 'block',
            'antifraud_id': 'd03b877c8e77446511a40160ddc7c512',
            'billing_id': '1',
            'billing_request': {
                'order': {
                    'due': '2020-01-10T15:52:00.000000+00:00',
                    'license': '1111111111',
                    'order_id': '2bc5bbf2ebe3246ebf83e499ac5434b1',
                },
            },
            'rule_id': 'selforder/phone',
            'subvention_type': 'order',
        }

        return web.json_response(data=dict())

    data = [
        {
            'order_id': '2bc5bbf2ebe3246ebf83e499ac5434b1',
            'reason': 'selforder/phone',
        },
        {'order_id': 'not_in_check_status', 'reason': 'collusion'},
    ]

    master_pool = cron_context.pg.master_pool
    await data_module.prepare_data(
        data,
        yt_client,
        master_pool,
        CURSOR_STATE_NAME,
        YT_DIRECTORY_PATH,
        YT_TABLE_PATH,
    )

    await run_cron.main(
        ['taxi_antifraud.crontasks.block_subventions', '-t', '0'],
    )

    assert _change_billing_status.times_called == 1

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_NAME: str(len(data)),
    }
