# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines

from aiohttp import web
import pytest

from taxi_qc_exams.generated.cron import run_cron
from test_taxi_qc_exams import utils


@pytest.mark.config(
    QC_JOB_SETTINGS=dict(import_drivers=utils.job_settings()),
    API_OVER_DATA_MIN_PROVIDER_POLLING_TIME_MS=dict(
        __default__=dict(__default__=0),
    ),
)
async def test_qc_import(simple_secdist, mock_qc_exams_admin, driver_profiles):
    @mock_qc_exams_admin('/v1/update/drivers')
    def mock_udpate(request):
        items = sorted(
            request.json['items'],
            key=lambda x: '{}_{}'.format(x['park_id'], x['driver_id']),
        )
        return web.json_response(
            data=dict(
                modified=items[0:2], unmodified=items[2:3], failed=items[3:],
            ),
        )

    # crontask
    await run_cron.main(['taxi_qc_exams.crontasks.imports.drivers', '-t', '0'])

    assert mock_udpate.times_called == 2
    items = sorted(
        mock_udpate.next_call()['request'].json.get('items'),
        key=lambda x: '{}_{}'.format(x['park_id'], x['driver_id']),
    )
    assert items == [
        dict(park_id='1', driver_id='2'),
        dict(park_id='1', driver_id='3'),
        dict(park_id='3', driver_id='1'),
        dict(park_id='3', driver_id='2'),
        dict(park_id='3', driver_id='3'),
    ]
    items = sorted(
        mock_udpate.next_call()['request'].json.get('items'),
        key=lambda x: '{}_{}'.format(x['park_id'], x['driver_id']),
    )
    assert items == [
        dict(park_id='3', driver_id='2'),
        dict(park_id='3', driver_id='3'),
    ]
