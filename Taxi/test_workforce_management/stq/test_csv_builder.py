import datetime

import pytest

from taxi.clients import mds_s3
from taxi.stq import async_worker_ng

from workforce_management.stq import setup_jobs

JOB_SET_STATUS_URI = 'v1/job/setup/status'
JOB_SET_URI = 'v1/data/start-export'
HEADERS = {'X-Yandex-UID': 'uid1', 'X-WFM-Domain': 'taxi'}


@pytest.mark.pgsql(
    'workforce_management',
    files=['simple_operators.sql', 'simple_shifts.sql', 'simple_absences.sql'],
)
async def test_base(taxi_workforce_management_web, stq3_context, patch):
    res = await taxi_workforce_management_web.post(
        JOB_SET_URI,
        json={
            'data_to_export': 'quality_control_timetable',
            'filter': {
                'timetable': {
                    'datetime_from': '2020-01-01T00:00:00Z',
                    'datetime_to': '2022-01-01T00:00:00Z',
                    'skill': 'pokemon',
                    'limit': 5000,
                    'offset': 0,
                },
            },
        },
        headers=HEADERS,
    )
    assert res.status == 200
    data = await res.json()
    job_id = data['job_id']

    @patch('taxi.clients.mds_s3.MdsS3Client.upload_content')
    async def _mds_upload(*args, **kwargs):
        return mds_s3.S3Object(Key=kwargs['key'], ETag=None)

    @patch('taxi.clients.mds_s3.MdsS3Client.generate_download_url')
    async def _mds_get_uri(*args, **kwargs):
        return 'url'

    await setup_jobs.task(
        context=stq3_context,
        task_info=async_worker_ng.TaskInfo(
            id=str(job_id),
            exec_tries=0,
            reschedule_counter=0,
            queue='workforce_management_setup_jobs',
        ),
        args=(),
        **{
            'job_type': 'csv/timetable/quality_control_timetable',
            'extra': (
                {
                    'datetime_from': datetime.datetime(
                        2020, 7, 21, tzinfo=datetime.timezone.utc,
                    ).isoformat(),
                    'datetime_to': datetime.datetime(
                        2020, 8, 10, tzinfo=datetime.timezone.utc,
                    ).isoformat(),
                    'limit': 10,
                    'offset': 0,
                    'yandex_uids': ['uid1', 'uid2'],
                    'skill': 'pokemon',
                    'domain': 'taxi',
                }
            ),
        },
    )

    res = await taxi_workforce_management_web.post(
        JOB_SET_STATUS_URI, json={'job_id': job_id},
    )

    assert res.status == 200

    data = await res.json()
    assert data == {
        'message': '{"url_to_download": "url"}',
        'progress': 0,
        'status': 'completed',
    }
