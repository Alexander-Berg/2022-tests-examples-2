import datetime
import os.path
from typing import Union

import pytest

from scripts.stuff.make_repo_archive import do_stuff


NOW = datetime.datetime.now()


@pytest.fixture(name='tmp_dir')
def _tmp_dir(tmpdir, patch):
    @patch('scripts.lib.utils.os.TempDir._make_temp_dir')
    async def _make_temp_dir():
        return tmpdir

    return tmpdir


@pytest.fixture(name='mock_arc')
def _mock_arc(tmp_dir, patch):
    def _wrapper():
        @patch('scripts.lib.vcs_utils.arc.Arc.mount')
        async def _arc_mount():
            pass

        @patch('scripts.lib.vcs_utils.arc.Arc.unmount')
        async def _arc_unmount():
            pass

        @patch('scripts.lib.vcs_utils.arc.Arc.try_checkout')
        async def _arc_try_checkout():
            pass

        @patch('scripts.lib.vcs_utils.arc.Arc.prefetch_files')
        async def _arc_prefetch_files():
            pass

        @patch('scripts.lib.vcs_utils.arc.Arc.mk_archive')
        async def _arc_mk_archive(extra_paths=None):
            with open(os.path.join(tmp_dir, 'script.zip'), 'wb') as fp:
                fp.write(b'some archive content')

        return {
            'mount': _arc_mount,
            'unmount': _arc_unmount,
            'try_checkout': _arc_try_checkout,
            'prefetch_files': _arc_prefetch_files,
            'mk_archive': _arc_mk_archive,
        }

    return _wrapper


@pytest.fixture(name='mock_s3')
def _mock_s3(mockserver):
    def _wrapper(key: str, upload_fail_cond: callable = None):
        @mockserver.handler(f'/archive-s3/scripts-archive/{key}')
        def _s3_object_handler(request):
            if request.method == 'PUT':
                part_number = request.query.get('partNumber')
                if part_number is None:
                    # upload whole file
                    return mockserver.make_response(headers={'ETag': '123'})

                if upload_fail_cond and upload_fail_cond():
                    # fail on uploading one part
                    return mockserver.make_response(status=500)

                return mockserver.make_response(headers={'ETag': '123'})

            if request.method == 'POST' and 'uploads' in request.query:
                # start multipart upload
                return mockserver.make_response(
                    f"""
<?xml version="1.0" encoding="UTF-8"?>
<InitiateMultipartUploadResult>
    <Bucket>scripts-archive</Bucket>
    <Key>{key}</Key>
    <UploadId>upload_id</UploadId>
</InitiateMultipartUploadResult>
""".strip(),
                )

            if request.method == 'POST' and 'uploadId' in request.query:
                # complete multipart upload
                return mockserver.make_response(
                    f"""
<?xml version="1.0" encoding="UTF-8"?>
<CompleteMultipartUploadResult>
    <Location>string</Location>
    <Bucket>scripts-archive</Bucket>
    <Key>{key}</Key>
    <ETag>123</ETag>
    <ChecksumCRC32>string</ChecksumCRC32>
    <ChecksumCRC32C>string</ChecksumCRC32C>
    <ChecksumSHA1>string</ChecksumSHA1>
    <ChecksumSHA256>string</ChecksumSHA256>
</CompleteMultipartUploadResult>
    """.strip(),
                )

            if request.method == 'DELETE' and 'uploadId' in request.query:
                # abort multipart upload
                return mockserver.make_response()

            raise NotImplementedError()

        return _s3_object_handler

    return _wrapper


class DtInEpsilon:
    def __init__(self, value: datetime.datetime, epsilon: datetime.timedelta):
        self._value = value
        self._epsilon = epsilon

    def __repr__(self) -> str:
        return f'DtInEpsilon({self._value} +- {self._epsilon})'

    def __eq__(self, other):
        if not isinstance(other, datetime.datetime):
            return False
        return (
            self._value - self._epsilon <= other <= self._value + self._epsilon
        )


def item(
        id_: str,
        vcs: str,
        status='pending',
        ref='some',
        path='',
        user='taxi',
        repo='tools-py3',
        updated: Union[datetime.datetime, DtInEpsilon] = NOW,
        created: Union[datetime.datetime, DtInEpsilon] = NOW,
        retries=0,
):
    return {
        '_id': id_,
        'vcs': vcs,
        'status': status,
        'user': user,
        'repo': repo,
        'path': path,
        'ref': ref,
        'updated': updated,
        'created': created,
        'retries': retries,
    }


def case(
        queue_items,
        expected_queue_result,
        id_=None,
        bb_archive_mock_called_times=0,
        s3_object_called_times=0,
        arc_used=False,
        marks=None,
        arc_s3_mock_file_name='arc-tools-py3--some',
):
    return pytest.param(
        queue_items,
        expected_queue_result,
        bb_archive_mock_called_times,
        s3_object_called_times,
        arc_used,
        arc_s3_mock_file_name,
        id=id_,
        marks=marks or [],
    )


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    [
        'queue_items',
        'expected_queue_result',
        'bb_archive_mock_called_times',
        's3_object_called_times',
        'arc_used',
        'arc_s3_mock_file_name',
    ],
    [
        case(
            [item('non-supported-gh', 'gh')],
            [
                item(
                    'non-supported-gh',
                    'gh',
                    'failed',
                    updated=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                    created=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                ),
            ],
            id_='fails cause gh is not supported',
        ),
        case(
            [item('succeeded-bb', 'bb')],
            [
                item(
                    'succeeded-bb',
                    'bb',
                    'success',
                    updated=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                    created=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                ),
            ],
            bb_archive_mock_called_times=1,
            s3_object_called_times=1,
            id_='success bb repo archiving',
        ),
        case(
            [item('retryable-bb-error', 'bb', ref='will-500')],
            [
                item(
                    'retryable-bb-error',
                    'bb',
                    ref='will-500',
                    updated=DtInEpsilon(
                        NOW + datetime.timedelta(minutes=5),
                        datetime.timedelta(seconds=30),
                    ),
                    created=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                    retries=1,
                ),
            ],
            bb_archive_mock_called_times=1,
            id_='retryable error on bb repo archiving',
        ),
        case(
            [item('non-retryable-bb-error', 'bb', ref='will-404')],
            [
                item(
                    'non-retryable-bb-error',
                    'bb',
                    ref='will-404',
                    status='failed',
                    updated=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                    created=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                ),
            ],
            bb_archive_mock_called_times=1,
            id_='non retryable error on bb repo archiving cause of 404',
        ),
        case(
            [item('retryable-bb-error-for-rate-limit', 'bb', ref='will-429')],
            [
                item(
                    'retryable-bb-error-for-rate-limit',
                    'bb',
                    ref='will-429',
                    updated=DtInEpsilon(
                        NOW + datetime.timedelta(minutes=5),
                        datetime.timedelta(seconds=30),
                    ),
                    created=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                    retries=1,
                ),
            ],
            bb_archive_mock_called_times=1,
            id_='retryable error on bb repo archiving cause of 429',
        ),
        case(
            [item('succeeded-bb-with-multipart', 'bb')],
            [
                item(
                    'succeeded-bb-with-multipart',
                    'bb',
                    'success',
                    updated=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                    created=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                ),
            ],
            bb_archive_mock_called_times=1,
            s3_object_called_times=4,
            id_='success bb repo archiving with multipart',
            marks=[pytest.mark.config(TAXI_SCRIPT_LOG_UPLOAD_CHUNK_SIZE=10)],
        ),
        case(
            [item('retryable-bb-error-on-uploading', 'bb')],
            [
                item(
                    'retryable-bb-error-on-uploading',
                    'bb',
                    updated=DtInEpsilon(
                        NOW + datetime.timedelta(minutes=5),
                        datetime.timedelta(seconds=30),
                    ),
                    created=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                    retries=1,
                ),
            ],
            bb_archive_mock_called_times=1,
            s3_object_called_times=3,
            id_='retryable error on archive uploading',
            marks=[pytest.mark.config(TAXI_SCRIPT_LOG_UPLOAD_CHUNK_SIZE=10)],
        ),
        case(
            [item('success-for-arc', 'arc')],
            [
                item(
                    'success-for-arc',
                    'arc',
                    'success',
                    updated=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                    created=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                ),
            ],
            s3_object_called_times=1,
            arc_used=True,
            id_='success for arc',
        ),
        case(
            [item('success-for-arc-with-path', 'arc', path='taxi_scripts')],
            [
                item(
                    'success-for-arc-with-path',
                    'arc',
                    'success',
                    path='taxi_scripts',
                    updated=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                    created=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                ),
            ],
            s3_object_called_times=1,
            arc_used=True,
            arc_s3_mock_file_name='arc-tools-py3-taxi_scripts-some',
            id_='success for arc with path',
        ),
        case(
            [
                item(
                    'success-for-dwh',
                    'arc',
                    repo='dwh-migrations',
                    user='taxi-dwh',
                ),
            ],
            [
                item(
                    'success-for-dwh',
                    'arc',
                    'success',
                    repo='dwh-migrations',
                    user='taxi-dwh',
                    updated=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                    created=DtInEpsilon(NOW, datetime.timedelta(seconds=30)),
                ),
            ],
            arc_s3_mock_file_name='arc-dwh-migrations--some',
            s3_object_called_times=1,
            arc_used=True,
        ),
    ],
)
async def test_do_stuff(
        monkeypatch,
        tmp_dir,
        loop,
        mockserver,
        patch,
        db,
        scripts_tasks_app,
        mock_arc,
        mock_s3,
        queue_items,
        expected_queue_result,
        bb_archive_mock_called_times,
        s3_object_called_times,
        arc_used,
        arc_s3_mock_file_name,
):
    arc_mocks = mock_arc()

    monkeypatch.setattr(
        'taxi.clients.bitbucket._BB_API_V1_HOST',
        mockserver.url('/bitbucket-api'),
    )

    @mockserver.handler('/bitbucket-api/projects/taxi/repos/tools-py3/archive')
    def _bb_archive_handler(request):
        if request.query['at'] == 'will-500':
            return mockserver.make_response(status=500)
        if request.query['at'] == 'will-404':
            return mockserver.make_response(status=404)
        if request.query['at'] == 'will-429':
            return mockserver.make_response(status=429)
        return mockserver.make_response(b'some archive content')

    bb_s3_mock = mock_s3(
        'bb-tools-py3--some',
        lambda: queue_items[0]['_id'] == 'retryable-bb-error-on-uploading',
    )
    arc_s3_mock = mock_s3(arc_s3_mock_file_name)

    await db.queue_archives_from_arcadia.insert_many(queue_items)

    class StuffContext:
        data = scripts_tasks_app

    await do_stuff.do_stuff(StuffContext(), loop)

    items = await db.queue_archives_from_arcadia.find().to_list(None)
    assert items == expected_queue_result
    assert _bb_archive_handler.times_called == bb_archive_mock_called_times
    assert (
        bb_s3_mock.times_called + arc_s3_mock.times_called
    ) == s3_object_called_times

    arc_calls = {
        mock_name: mock.calls for mock_name, mock in arc_mocks.items()
    }
    for mock_name, calls in arc_calls.items():
        if arc_used:
            assert calls, f'mock {mock_name!r} not used'
        else:
            assert not calls, f'mock {mock_name!r} used'

    if queue_items[0]['path'] and arc_used:
        assert arc_calls['mk_archive'][0]['extra_paths'] == [
            queue_items[0]['path'],
            'libraries',
        ]
