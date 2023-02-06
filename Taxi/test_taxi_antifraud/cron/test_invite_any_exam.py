from aiohttp import web
import pytest

from taxi_antifraud.crontasks import invite_any_exam
from taxi_antifraud.generated.cron import run_cron
from test_taxi_antifraud.cron.utils import data as data_module
from test_taxi_antifraud.cron.utils import mock as mock_module
from test_taxi_antifraud.cron.utils import state

CURSOR_STATE_PREFIX = invite_any_exam.CURSOR_STATE_PREFIX

YT_TABLE_DIRECTORY = '//home/taxi-fraud/unittests/kopatel/invite'
YT_TABLE_PATH_STS = YT_TABLE_DIRECTORY + '/sts'
YT_TABLE_PATH_BIOMETRY = YT_TABLE_DIRECTORY + '/biometry'

PG_DATABASE_NAME = 'antifraud_py'


@pytest.mark.config(
    AFS_CRON_CURSOR_USE_PGSQL='enabled',
    AFS_CRON_QC_ANY_INVITES_ENABLED=True,
    AFS_CRON_QC_ANY_INVITES_EXAMS_AND_ENTITY_TYPES_MAPPING={
        '__default__': 'driver',
        'sts': 'car',
        'biometry': 'driver',
    },
    AFS_CRON_QC_ANY_INVITES_INPUT_TABLE_SUFFIX='kopatel/invite',
    AFS_CRON_QC_ANY_INVITES_SLEEP_TIME_BETWEEN_INVITES={
        '__default__': 0.01,
        'sts': 0.01,
        'biometry': 0.01,
    },
    AFS_CRON_QC_ANY_INVITES_SLEEP_TIME_AFTER_READ_ALL_ROWS=1,
)
@pytest.mark.parametrize(
    'data_sts,data_biometry,requests_sts,requests_biometry',
    [
        (
            [
                {
                    'filter': {
                        'car_number': 'AA123AAA777',
                        'park_id': '654321',
                    },
                    'comment': 'strange behaviour',
                },
            ],
            [
                {
                    'filter': {
                        'license_pd_id': 'e434e5d8405845bfbe25cd420e52fd76',
                    },
                    'comment': 'No comments',
                },
                {
                    'filter': {
                        'license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                        'park_id': '123456',
                    },
                    'comment': 'bad behaviour',
                },
                {
                    'filter': {
                        'license_pd_id': 'ca44836f7dd64edb9c43f0408dea4eaf',
                        'park_id': '654321',
                    },
                    'comment': 'for fun',
                },
            ],
            [
                {
                    'comment': 'strange behaviour',
                    'filters': {
                        'car_number': 'AA123AAA777',
                        'park_id': '654321',
                    },
                    'entity_type': 'car',
                    'identity_type': 'service',
                },
            ],
            [
                {
                    'comment': 'No comments',
                    'filters': {
                        'license_pd_id': 'e434e5d8405845bfbe25cd420e52fd76',
                    },
                    'entity_type': 'driver',
                    'identity_type': 'service',
                },
                {
                    'comment': 'bad behaviour',
                    'filters': {
                        'license_pd_id': '06e273a2f46a4f8ca5068ed1ad0b73a0',
                        'park_id': '123456',
                    },
                    'entity_type': 'driver',
                    'identity_type': 'service',
                },
                {
                    'comment': 'for fun',
                    'filters': {
                        'license_pd_id': 'ca44836f7dd64edb9c43f0408dea4eaf',
                        'park_id': '654321',
                    },
                    'entity_type': 'driver',
                    'identity_type': 'service',
                },
            ],
        ),
    ],
)
async def test_cron(
        mock_qc_invites,
        yt_client,
        cron_context,
        data_sts,
        data_biometry,
        requests_sts,
        requests_biometry,
):
    @mock_qc_invites('/admin/qc-invites/v1/sts/invite')
    def _invite_sts_exam(request):
        return web.json_response(data=dict(invite_id='invite_id'))

    @mock_qc_invites('/admin/qc-invites/v1/biometry/invite')
    def _invite_biometry_exam(request):
        return web.json_response(data=dict(invite_id='invite_id'))

    master_pool = cron_context.pg.master_pool

    await data_module.prepare_data(
        data_sts,
        yt_client,
        master_pool,
        CURSOR_STATE_PREFIX + 'sts',
        YT_TABLE_DIRECTORY,
        YT_TABLE_PATH_STS,
    )

    await data_module.prepare_data(
        data_biometry,
        yt_client,
        master_pool,
        CURSOR_STATE_PREFIX + 'biometry',
        YT_TABLE_DIRECTORY,
        YT_TABLE_PATH_BIOMETRY,
    )

    await run_cron.main(
        ['taxi_antifraud.crontasks.invite_any_exam', '-t', '0'],
    )

    assert mock_module.get_requests(_invite_sts_exam) == requests_sts
    assert mock_module.get_requests(_invite_biometry_exam) == requests_biometry

    assert await state.get_all_cron_state(master_pool) == {
        CURSOR_STATE_PREFIX + 'sts': str(len(data_sts)),
        CURSOR_STATE_PREFIX + 'biometry': str(len(data_biometry)),
    }
