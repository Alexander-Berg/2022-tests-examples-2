from aiohttp import web
import pytest

from taxi_antifraud.crontasks import block_subventions_by_doc_id
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import data as data_module
from test_taxi_antifraud.cron.utils import state

CURSOR_STATE_NAME = block_subventions_by_doc_id.CURSOR_STATE_NAME

YT_DIRECTORY_PATH = '//home/taxi-fraud/unittests/kopatel'
YT_TABLE_PATH = YT_DIRECTORY_PATH + '/to_block'


@pytest.mark.config(
    AFS_CRON_BLOCK_SUBVENTIONS_BY_DOC_ID_ENABLED=True,
    AFS_CRON_BLOCK_SUBVENTIONS_BY_DOC_ID_INPUT_TABLE_SUFFIX='kopatel/to_block',
    AFS_CRON_BLOCK_SUBVENTIONS_BY_DOC_ID_SLEEP_TIME_SECONDS=0.01,
    AFS_CRON_CURSOR_USE_PGSQL='enabled',
)
async def test_cron(mock_antifraud, yt_apply, yt_client, db, cron_context):
    requests = {
        'doc_id/2781835550168': {
            'action': 'block',
            'antifraud_id': 'f600da767b678b930243ea21b23e3e0b',
            'billing_id': 'doc_id/2781835550168',
            'billing_request': {
                'order': {
                    'due': '2020-01-10T15:52:00.000000+00:00',
                    'license': '1111111111',
                    'order_id': '2bc5bbf2ebe3246ebf83e499ac5434b1',
                },
            },
            'rule_id': 'some reason',
            'subvention_type': 'personal',
        },
        'doc_id/2775753150057': {
            'action': 'block',
            'antifraud_id': '9b7ce376f11bc92d6c04b35d68d5ff8a',
            'billing_id': 'doc_id/2775753150057',
            'billing_request': {
                'order': {
                    'due': '2020-01-10T15:52:00.000000+00:00',
                    'license': '1111111111',
                    'order_id': '2bc5bbf2ebe3246ebf83e499ac5434b1',
                },
            },
            'rule_id': 'another reason',
            'subvention_type': 'personal',
        },
        'doc_id/2776142670190': {
            'action': 'block',
            'antifraud_id': 'd6fd17bb8234cb2a46e5400ab415baa3',
            'billing_id': 'doc_id/2776142670190',
            'billing_request': {'driver': {'licenses': ['9904436232']}},
            'rule_id': 'yet another reason',
            'subvention_type': 'daily_guarantee',
        },
    }

    data = [
        {'billing_id': 'doc_id/2781835550168', 'reason': 'some reason'},
        {'billing_id': 'doc_id/2775753150057', 'reason': 'another reason'},
        {'billing_id': 'doc_id/2776142670190', 'reason': 'yet another reason'},
    ]

    @mock_antifraud('/v1/subventions/change_billing_status')
    def _change_billing_status(request):
        assert request.method == 'POST'

        assert request.json == requests.pop(request.json['billing_id'], None)

        return web.json_response(data=dict())

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
        ['taxi_antifraud.crontasks.block_subventions_by_doc_id', '-t', '0'],
    )

    assert _change_billing_status.times_called == 3

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_NAME: str(len(data)),
    }
