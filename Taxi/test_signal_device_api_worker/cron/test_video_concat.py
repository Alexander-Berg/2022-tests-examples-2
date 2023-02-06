# pylint: disable=global-statement
# pylint: disable=import-error
# pylint: disable=import-only-modules
# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=unused-variable
# pylint: disable=W0212
import dataclasses
import functools
import re
import typing

import pytest

from taxi.stq import async_worker_ng

from signal_device_api_worker.stq import video_concat
from signal_device_api_worker.generated.cron import run_cron  # noqa F401

CRON_PARAMS = ['signal_device_api_worker.crontasks.video_concat', '-t', '0']
BIG_VIDEOS_LIMIT = 100

MDS_HOST_INTERNAL = 'https://s3.mock.net'
MDS_HOST_PUBLIC = 'https://s3-private.mock.net'
PARTITIONS_BUCKET = 'sda-video-partitions'
DEVICE_PUBLIC_ID = 'e58e753c44e548ce9edaec0e0ef9c8c1'
FIXED_PATH_SUFFIX = 'videos/partitions'
PARTITION_EXTENSION = '.part'
GET_URL_REGEX = re.compile(
    f'{MDS_HOST_INTERNAL}/{PARTITIONS_BUCKET}/v1/'
    f'{DEVICE_PUBLIC_ID}/{FIXED_PATH_SUFFIX}/'
    + r'(?P<file_id>.+)/(?P<offset>\d+)_(?P<size>\d+)'
    + PARTITION_EXTENSION,
)

S3_PATH_BROKEN = 'BROKEN'


@dataclasses.dataclass(frozen=True)
class VideoPartitionIdentifier:
    file_id: str
    offset: int
    size: int


@dataclasses.dataclass(frozen=True)
class Video:
    device_id: int
    file_id: str
    size_bytes: int
    s3_path: typing.Any


S3_RESPONSE_DEFAULT_HEADERS = {
    'server': 'nginx',
    'date': 'Tue, 10 Mar 2020 13:32:47 GMT',
    'content-type': 'text/plain',
    'content-length': '524288',
    'connection': 'keep-alive',
    'keep-alive': 'timeout=60',
    'accept-ranges': 'bytes',
    'etag': '"0b04369d9db59cff86032fdf0ebb46bb"',
    'last-modified': 'Tue, 10 Mar 2020 13:19:23 GMT',
    'x-amz-request-id': '22f812adec352f0a',
    'x-yc-s3-bucket': PARTITIONS_BUCKET,
    'x-yc-s3-bucket-tags': '{}',
    'x-yc-s3-folder-id': '4975',
    'x-yc-s3-handler': 'GET Object',
    'x-yc-s3-requester': 'uid:1120000000168546',
    'x-yc-s3-storage-class': 'STANDARD',
    'access-control-allow-origin': '*',
    'x-robots-tag': 'noindex, noarchive, nofollow',
}

BROKEN_S3_GET_FILES = [
    {
        'id': VideoPartitionIdentifier('broken_missing_start_s3', 0, 5),
        'body': None,
    },
    {
        'id': VideoPartitionIdentifier('broken_missing_middle_s3', 5, 2),
        'body': None,
    },
]

VIDEOS_BROKEN_S3: typing.List = [
    Video(1, 'broken_missing_middle_s3', 10, S3_PATH_BROKEN),
]
S3_CALLS_BROKEN_S3: typing.Dict = {
    'GET': [
        {'file_id': 'broken_missing_middle_s3', 'offset': '0', 'size': '5'},
        {'file_id': 'broken_missing_middle_s3', 'offset': '0', 'size': '5'},
        {'file_id': 'broken_missing_middle_s3', 'offset': '0', 'size': '5'},
        {'file_id': 'broken_missing_middle_s3', 'offset': '0', 'size': '5'},
    ],
    'PUT': [],
}
VIDEOS_OK: typing.List = [
    Video(
        1, 'not_concatenated_single', 10, 'v1/abc123/not_concatenated_single',
    ),
    Video(1, 'not_concatenated_multi', 10, 'v1/abc123/not_concatenated_multi'),
]
S3_CALLS_OK: typing.Dict = {
    'GET': [
        {'file_id': 'not_concatenated_single', 'offset': '0', 'size': '10'},
        {'file_id': 'not_concatenated_multi', 'offset': '0', 'size': '5'},
        {'file_id': 'not_concatenated_multi', 'offset': '5', 'size': '5'},
    ],
    'PUT': [],
}

# global variables for s3 checks
mds_get_requests: typing.List = []
mds_put_requests: typing.List = []


def sorted_s3_calls(s3_calls):
    return sorted(s3_calls, key=lambda c: (c['file_id'], c['offset']))


def check_field_match(field_name, db_value, expected_value):
    assert (
        db_value == expected_value
    ), f'{field_name} in db = {db_value}, expected = {expected_value}'


def select_video_pg(pgsql, device_id, file_id, fields):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT {} FROM signal_device_api.videos '
        'WHERE device_id={} AND file_id=\'{}\''.format(
            ','.join(fields), device_id, file_id,
        ),
    )
    return {k: v for (k, v) in zip(fields, list(db)[0])}


def check_video_pg(pgsql, expected):
    fields = ['device_id', 'file_id', 'size_bytes', 's3_path']
    expected_video = dataclasses.asdict(expected)
    db_video = select_video_pg(
        pgsql, expected_video['device_id'], expected_video['file_id'], fields,
    )
    for field in [f for f in fields]:
        check_field_match(field, db_video[field], expected_video[field])


def check_videos_state(pgsql, videos):
    def check_videos_state_dec(func):
        @functools.wraps(func)
        async def function_wrapper():
            await func()
            for video in videos:
                check_video_pg(pgsql, video)

        return function_wrapper

    return check_videos_state_dec


def check_s3_calls(expected_calls):
    def check_s3_calls_dec(func):
        global mds_get_requests, mds_put_requests
        mds_get_requests = []
        mds_put_requests = []

        @functools.wraps(func)
        async def function_wrapper():
            await func()
            assert sorted_s3_calls(mds_get_requests) == sorted_s3_calls(
                expected_calls['GET'],
            )
            assert sorted_s3_calls(mds_put_requests) == sorted_s3_calls(
                expected_calls['PUT'],
            )

        return function_wrapper

    return check_s3_calls_dec


@pytest.fixture
def mock_s3_requests(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(MDS_HOST_INTERNAL, 'GET')
    def patch_request_get(method, url, headers, **kwargs):
        global mds_get_requests
        parse = re.search(GET_URL_REGEX, url)
        assert parse, (
            f'Failed to parse GET request url: '
            + f'method = {str(method)}, '
            + f'url = {str(url)}, '
            + f'headers = {str(headers)}, '
            + f'kwargs = {str(kwargs)}'
        )
        params = parse.groupdict()
        mds_get_requests.append(params)
        response_raw = b'1' * int(params['size'])
        for broken in BROKEN_S3_GET_FILES:
            broken_id_dict = dataclasses.asdict(broken['id'])
            if (
                    params['file_id'] == broken_id_dict['file_id']
                    and params['size'] == broken_id_dict['size']
                    and params['offset_bytes']
                    == broken_id_dict['offset_bytes']
            ):
                response_raw = broken['body']
        s3_response_headers = S3_RESPONSE_DEFAULT_HEADERS
        s3_response_headers['content-length'] = str(params['size'])
        response = response_mock(headers=s3_response_headers)
        response.status_code = response.status
        response.raw_headers = [
            (k.encode(), v.encode()) for k, v in response.headers.items()
        ]
        response.raw = response_raw
        return response

    @patch_aiohttp_session(MDS_HOST_INTERNAL, 'PUT')
    def patch_request_put(method, url, headers, **kwargs):
        global mds_put_requests
        print(
            f'Failed to parse PUT request url: '
            f'method={str(method)}, '
            f'url={str(url)}, '
            f'headers = {str(headers)}, '
            f'kwargs = {str(kwargs)}',
        )
        raise Exception('kek')

    return [patch_request_get, patch_request_put]


@pytest.mark.pgsql('signal_device_api_meta_db', files=['stq_test.sql'])
async def test_run_cron(
        mockserver, taxi_config, simple_secdist, mock_s3_requests, pgsql,
):
    await run_cron.main(CRON_PARAMS)


TEST_CHUNK = {
    'public_id': 'e58e753c44e548ce9edaec0e0ef9c8c1',
    'device_id': 1,
    'file_id': 'broken_missing_middle_s3',
    'offset_bytes': 7,
    'chunk_size_bytes': 3,
    'video_size_bytes': 10,
    'created_at': '2021-07-01T00:00:00+00:00',
}


@pytest.mark.pgsql('signal_device_api_meta_db', files=['stq_test.sql'])
async def test_stq_task(stq3_context, pgsql, mock_s3_requests):
    @check_videos_state(pgsql, VIDEOS_BROKEN_S3)
    @check_s3_calls(S3_CALLS_BROKEN_S3)
    async def run():
        task_info = async_worker_ng.TaskInfo(
            id='task_id',
            exec_tries=3,
            reschedule_counter=0,
            queue='signal_device_api_worker_video_concat',
        )
        await video_concat.task(stq3_context, task_info, [TEST_CHUNK])

    await run()

    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT concat_status, COUNT(*) AS amount '
        'FROM signal_device_api.video_chunks '
        'GROUP BY concat_status '
        'ORDER BY amount DESC',
    )
    assert list(db) == [('not_concatenated', 4), ('concatenated', 1)]
