import datetime
import random

import aiohttp
import pytest

from supportai_calls.generated.service.swagger import models

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_calls', files=['db.sql']),
]

MAX_BODY_SIZE = 10  # Mb


@pytest.fixture(name='mock_storage')
def _get_mock_storage():
    return {
        'ivr-dispatcher': {
            'ivr_flow_worker/slug1/file1.wav': b'content1_1',
            'ivr_flow_worker/slug1/file2.wav': b'content1_2',
            'ivr_flow_worker/slug2/file1.wav': b'content2_1',
        },
        'supportai-calls': {
            'voximplant/slug1/vox_file.mp3': b'vox_file_content',
            'voximplant/slug2/vox_file_2.mp3': b'vox_file_2_content',
        },
    }


@pytest.fixture(name='mock_mds_s3')
async def _mds_server_mock(mockserver, mock_storage):
    def _path_to_bucket_name_and_key(path):
        chunks = path.rsplit('/', maxsplit=4)
        key = '/'.join(chunks[-3:])
        bucket = chunks[-4]
        return bucket, key

    def _parse_post_delete_body(body):
        chunks = body.split(b'</Key></Object><Object><Key>')
        chunks[0] = chunks[0].split(b'<Object><Key>')[1]
        chunks[-1] = chunks[-1].split(b'</Key></Object>')[0]
        return [chunk.decode() for chunk in chunks]

    @mockserver.handler('/mds-s3/', prefix=True)
    async def _(request):
        path = request.path
        if request.method == 'PUT':
            bucket_name, key = _path_to_bucket_name_and_key(path)
            mock_storage[bucket_name][key] = request.get_data()
            return mockserver.make_response(headers={'ETag': ''})
        if request.method == 'GET':
            bucket_name, key = _path_to_bucket_name_and_key(path)
            body = mock_storage[bucket_name].get(key, None)
            if body is None:
                return mockserver.make_response(
                    status=400,
                    response='<Error><Code>NoSuchKey</Code></Error>',
                )
            return mockserver.make_response(body, headers={'ETag': ''})
        if request.method == 'DELETE':
            bucket_name, key = _path_to_bucket_name_and_key(path)
            mock_storage[bucket_name].pop(key, None)
            return mockserver.make_response(headers={'ETag': ''})
        if request.method == 'POST':
            bucket_name = path.rsplit('/', maxsplit=1)[-1]
            keys = _parse_post_delete_body(request.get_data())
            for key in keys:
                mock_storage[bucket_name].pop(key, None)
            return mockserver.make_response(headers={'ETag': ''})


class DummyOutput:
    class DummyAsyncStream:
        def __init__(self, content):
            self.content = content

        async def read(self):
            return self.content

    def __init__(self, content):
        self.stdout = self.DummyAsyncStream(content)
        self.stderr = self.DummyAsyncStream(b'')


def _metadata_json_to_filenames_set(response_json):
    return {row['filename'] for row in response_json['files_metadata']}


async def test_get_file_metadata(web_app_client):
    async def get_response(project_slug, filename):
        return await web_app_client.get(
            f'v1/files/metadata/audio/{filename}'
            f'?project_slug={project_slug}&user_id=34',
        )

    def check_file_metadata(
            response_json, filename, user_filename, user_comment,
    ):
        assert response_json['filename'] == filename
        for property_name, expected_property_value in zip(
                ['user_filename', 'user_comment'],
                [user_filename, user_comment],
        ):
            response_property_value = response_json.get(property_name)
            if expected_property_value is not None:
                assert response_property_value == expected_property_value
            else:
                assert response_property_value is None

    project_slugs = ['slug1', 'slug2', 'slug2', 'no_such_slug']
    filenames = ['file1.wav', 'file1.wav', 'no_such_file', 'does_not_matter']
    statuses = [200, 200, 404, 400]
    user_filenames = ['file1_user_filename', None, '', '']
    user_comments = ['file1_user_comment', None, '', '']

    for project_slug, filename, status, user_filename, user_comment in zip(
            project_slugs, filenames, statuses, user_filenames, user_comments,
    ):
        response = await get_response(project_slug, filename)
        assert response.status == status
        if response.status > 200:
            continue
        check_file_metadata(
            await response.json(), filename, user_filename, user_comment,
        )


async def test_get_files_metadata(web_app_client):
    slug_to_expected_filenames = {
        'slug1': {'file1.wav', 'file2.wav'},
        'slug2': {'file1.wav'},
    }

    for project_slug in ('slug1', 'slug2', 'slug3'):
        response = await web_app_client.get(
            f'v1/files/metadata/audio?project_slug={project_slug}&user_id=34',
        )
        expected_filenames = slug_to_expected_filenames.get(project_slug, None)
        if not expected_filenames:
            assert response.status == 204
            continue
        assert response.status == 200
        response_json = await response.json()
        assert (
            _metadata_json_to_filenames_set(response_json)
            == expected_filenames
        )
        for file_metadata in response_json['files_metadata']:
            response_user_filename = file_metadata.get('user_filename')
            response_user_comment = file_metadata.get('user_comment')
            if project_slug == 'slug2':
                assert response_user_filename is None
                assert response_user_comment is None
            else:
                filename = file_metadata['filename']
                basename = filename.split('.')[0]
                expected_user_filename = f'{basename}_user_filename'
                expected_user_comment = f'{basename}_user_comment'
                assert response_user_filename == expected_user_filename
                if basename == 'file1':
                    assert response_user_comment == expected_user_comment
                else:
                    assert response_user_comment is None
            assert file_metadata['uploaded_at'] == '2020-01-01T03:00:00+03:00'


async def test_get_file(mockserver, web_app_client, mock_mds_s3):
    project_slug = 'slug1'
    filename = 'file1.wav'
    response = await web_app_client.get(
        f'/v1/files/audio/{filename}?project_slug={project_slug}&user_id=34',
    )
    assert response.status == 200
    assert (await response.content.read()) == b'content1_1'

    project_slug = 'slug2'
    filename = 'file1.wav'
    response = await web_app_client.get(
        f'/v1/files/audio/{filename}?project_slug={project_slug}&user_id=34',
    )
    assert response.status == 200
    assert (await response.content.read()) == b'content2_1'

    project_slug = 'slug1'
    filename = 'no_such_filename.wav'
    response = await web_app_client.get(
        f'/v1/files/audio/{filename}?project_slug={project_slug}&user_id=34',
    )
    assert response.status == 404

    project_slug = 'no_such_slug'
    filename = 'file1.wav'
    response = await web_app_client.get(
        f'/v1/files/audio/{filename}?project_slug={project_slug}&user_id=34',
    )
    assert response.status == 400


@pytest.mark.parametrize('project_slug', ['slug1', 'no_such_slug'])
@pytest.mark.parametrize('extension', ['', '.random'])
@pytest.mark.parametrize(
    ('user_filename', 'user_comment'),
    [
        ('Пользовательское имя файла', 'Пользовательский комментарий'),
        (None, None),
    ],
)
async def test_upload_file(
        mockserver,
        web_app_client,
        load_binary,
        patch,
        project_slug,
        extension,
        user_filename,
        user_comment,
        mock_mds_s3,
        mock_storage,
):
    bucket = mock_storage['ivr-dispatcher']
    filename = 'new_file'
    extended_filename = filename + extension
    file_content = b'new_file_content'
    form_data = aiohttp.FormData()
    form_data.add_field(
        name='file',
        value=file_content,
        filename=extended_filename,
        content_type='audio/something',
    )

    if user_filename is not None:
        form_data.add_field(name='user_filename', value=user_filename)
        form_data.add_field(name='user_comment', value=user_comment)

    @patch('supportai_calls.utils.file_helpers._create_ffmpeg_subprocess')
    async def _(*args, **kwargs):
        return DummyOutput(file_content)

    response = await web_app_client.post(
        f'v1/files/audio?project_slug={project_slug}&user_id=34',
        data=form_data,
    )

    if project_slug == 'no_such_slug':
        assert response.status == 400
        return

    assert response.status == 200

    response_json = await response.json()
    assert response_json.get('filename') == f'{filename}.wav'
    if user_filename is not None:
        assert response_json.get('user_filename') == user_filename
        assert response_json.get('user_comment') == user_comment
    else:
        assert response_json.get('user_filename') is None
        assert response_json.get('user_comment') is None

    mds_s3_key = f'ivr_flow_worker/{project_slug}/{filename}.wav'
    assert bucket[mds_s3_key] == file_content

    response = await web_app_client.get(
        f'v1/files/metadata/audio' f'?project_slug={project_slug}&user_id=34',
    )
    assert response.status == 200
    response_json = await response.json()
    assert _metadata_json_to_filenames_set(response_json) == {
        'file1.wav',
        'file2.wav',
        'new_file.wav',
    }
    new_file_user_filename, new_file_user_comment = [
        (file_metadata.get('user_filename'), file_metadata.get('user_comment'))
        for file_metadata in response_json['files_metadata']
        if file_metadata['filename'] == 'new_file.wav'
    ][0]
    if user_filename is not None:
        assert user_filename == new_file_user_filename
        assert user_comment == new_file_user_comment
    else:
        assert new_file_user_filename is None
        assert new_file_user_comment is None

    form_data = aiohttp.FormData()
    file_content = b'overwritten_content'
    form_data.add_field(
        name='file',
        value=file_content,
        filename=extended_filename,
        content_type='audio/random',
    )

    response = await web_app_client.post(
        f'v1/files/audio?project_slug={project_slug}&user_id=34',
        data=form_data,
    )
    assert response.status == 200
    assert bucket[mds_s3_key] == file_content


async def test_mds_error_during_upload(
        mockserver, web_app_client, load_binary, patch, mock_storage,
):
    def _path_to_mds_s3_key(path):
        return '/'.join(path.rsplit('/', maxsplit=3)[-3:])

    @mockserver.handler('/mds-s3/', prefix=True)
    async def _(request):
        if request.method == 'PUT':
            return mockserver.make_response(status=400)
        if request.method == 'GET':
            mds_s3_key = _path_to_mds_s3_key(request.path)
            body = mock_storage.get(mds_s3_key, None)
            if body is None:
                return mockserver.make_response(
                    status=400,
                    response='<Error><Code>NoSuchKey</Code></Error>',
                )
            return mockserver.make_response(body, headers={'ETag': ''})

    @patch('supportai_calls.utils.file_helpers._create_ffmpeg_subprocess')
    async def _(*args, **kwargs):
        return DummyOutput(b'')

    project_slug = 'slug1'

    new_file_name = 'new_file.wav'
    form_data = aiohttp.FormData()
    form_data.add_field(
        name='file',
        value=b'',
        filename=new_file_name,
        content_type='audio/random',
    )

    response = await web_app_client.post(
        f'v1/files/audio?project_slug={project_slug}&user_id=34',
        data=form_data,
    )
    assert response.status == 500

    response = await web_app_client.get(
        f'/v1/files/audio/{new_file_name}'
        f'?project_slug={project_slug}&user_id=34',
    )
    assert response.status == 404


async def test_delete_file(web_app_client, patch, mock_mds_s3, mock_storage):
    project_slug = 'slug1'
    filename_to_delete = 'file1.wav'
    bucket = mock_storage['ivr-dispatcher']

    for counter in range(2):
        response = await web_app_client.delete(
            f'v1/files/audio/{filename_to_delete}'
            f'?project_slug={project_slug}&user_id=34',
        )
        assert response.status == (200 if counter == 0 else 404)

        response = await web_app_client.get(
            f'v1/files/metadata/audio?project_slug={project_slug}&user_id=34',
        )
        assert response.status == 200
        assert _metadata_json_to_filenames_set(await response.json()) == {
            'file2.wav',
        }
        assert (
            bucket.get(
                f'ivr_flow_worker/{project_slug}/{filename_to_delete}', None,
            )
            is None
        )

    another_project_slug = 'slug2'
    response = await web_app_client.get(
        f'v1/files/metadata/audio'
        f'?project_slug={another_project_slug}&user_id=34',
    )
    assert response.status == 200
    assert _metadata_json_to_filenames_set(await response.json()) == {
        'file1.wav',
    }


@pytest.mark.parametrize('call_service', ['ivr_framework', 'voximplant'])
async def test_delete_all_files(
        stq3_context, web_app_client, mock_mds_s3, mock_storage, call_service,
):
    bucket = (
        mock_storage['supportai-calls']
        if call_service == 'voximplant'
        else mock_storage['ivr-dispatcher']
    )
    project_slug = 'slug1'

    dispatcher_params_json = {'call_service': call_service}
    if call_service == 'voximplant':
        dispatcher_params_json.update(
            {'api_key': 'ALALA-QOALA', 'account_id': 1, 'rule_id': 1},
        )

    expected_bucket_keys = {
        'ivr_framework': {'ivr_flow_worker/slug2/file1.wav'},
        'voximplant': {'voximplant/slug2/vox_file_2.mp3'},
    }

    assert (
        await web_app_client.put(
            f'v1/project_configs?project_slug={project_slug}&user_id=42',
            json={'dispatcher_params': dispatcher_params_json},
        )
    ).status == 200

    for _ in range(2):
        assert (
            await web_app_client.delete(
                f'v1/files/audio?project_slug={project_slug}&user_id=34',
            )
        ).status == 200

        assert (
            await web_app_client.get(
                f'v1/files/metadata/audio'
                f'?project_slug={project_slug}&user_id=34',
            )
        ).status == 204

        assert set(bucket.keys()) == expected_bucket_keys[call_service]


async def test_delete_batch_files(
        stq3_context, web_app_client, patch, mock_mds_s3, mock_storage,
):
    bucket = mock_storage['ivr-dispatcher']
    bucket.clear()
    project_slug = 'slug3'

    @patch('supportai_calls.utils.file_helpers._create_ffmpeg_subprocess')
    # pylint: disable=unused-variable
    async def mock_ffmpeg(*args, **kwargs):
        return DummyOutput(b'')

    filenames = [f'file{i}.wav' for i in range(20)]
    for filename in filenames:
        form_data = aiohttp.FormData()
        form_data.add_field(
            name='file',
            value=b'',
            content_type='audio/random',
            filename=filename,
        )
        await web_app_client.post(
            f'v1/files/audio?project_slug={project_slug}&user_id=34',
            data=form_data,
        )

    filenames_to_delete = random.sample(filenames, 10)
    expected_left_filenames = [
        filename
        for filename in filenames
        if filename not in filenames_to_delete
    ]
    expected_mds_s3_keys = [
        f'ivr_flow_worker/{project_slug}/{filename}'
        for filename in expected_left_filenames
    ]

    for _ in range(2):
        response = await web_app_client.post(
            f'v1/files/delete_batch/audio'
            f'?project_slug={project_slug}&user_id=34',
            json={'filenames': filenames_to_delete},
        )
        assert response.status == 200

        response = await web_app_client.get(
            f'v1/files/metadata/audio'
            f'?project_slug={project_slug}&user_id=34',
        )
        assert response.status == 200
        assert _metadata_json_to_filenames_set(await response.json()) == set(
            expected_left_filenames,
        )

        assert set(expected_mds_s3_keys) == set(bucket.keys())


@pytest.mark.parametrize('size_deviation', [-10, 10])
async def test_post_large_file(
        web_app_client, patch, mock_mds_s3, mock_storage, size_deviation,
):
    bucket = mock_storage['ivr-dispatcher']
    project_slug = 'slug1'
    file_content = b'\x00' * (MAX_BODY_SIZE * (1024 ** 2) + size_deviation)
    is_too_large = size_deviation > 0

    @patch('supportai_calls.utils.file_helpers._create_ffmpeg_subprocess')
    async def _(*args, **kwargs):
        return DummyOutput(file_content)

    form_data = aiohttp.FormData()
    form_data.add_field(
        name='file',
        value=file_content,
        filename='new_file.wav',
        content_type='audio/wav',
    )

    response = await web_app_client.post(
        f'v1/files/audio?project_slug={project_slug}&user_id=34',
        data=form_data,
    )
    if is_too_large:
        assert response.status == 413
    else:
        assert response.status == 200
        assert (
            bucket[f'ivr_flow_worker/{project_slug}/new_file.wav']
            == file_content
        )


async def test_update_upload_datetime_and_user_filename(
        web_app_client, patch, mock_mds_s3, mock_storage,
):
    now = datetime.datetime.now().astimezone()
    time_delta = datetime.timedelta(minutes=10)
    nows = [now, now + time_delta]

    @patch('datetime.datetime.now')
    def _():
        return nows[0]

    @patch('supportai_calls.utils.file_helpers._create_ffmpeg_subprocess')
    async def _(*args, **kwargs):
        return DummyOutput(b'')

    filename = 'new_file.wav'
    form_data = aiohttp.FormData()
    form_data.add_field(
        name='file',
        value=b'',
        content_type='audio/something',
        filename=filename,
    )

    async def check_file_metadata(filename, upload_time, user_filename):
        response = await web_app_client.get(
            f'v1/files/metadata/audio/{filename}'
            f'?project_slug=slug1&user_id=34',
        )
        response_json = await response.json()
        file_metadata = models.api.AudioFileMetadata.deserialize(response_json)
        assert (
            file_metadata.uploaded_at.replace(tzinfo=datetime.timezone.utc)
            == upload_time
        )
        if user_filename is not None:
            assert file_metadata.user_filename == user_filename
        else:
            assert file_metadata.user_filename is None

    await web_app_client.post(
        'v1/files/audio?project_slug=slug1&user_id=34', data=form_data,
    )
    await check_file_metadata(filename, now, None)

    nows.pop(0)

    new_user_filename = 'huraaay, now I have a user_filename!'

    form_data = aiohttp.FormData()
    form_data.add_field(
        name='file',
        value=b'',
        content_type='audio/something',
        filename=filename,
    )
    form_data.add_field(name='user_filename', value=new_user_filename)

    await web_app_client.post(
        'v1/files/audio?project_slug=slug1&user_id=34', data=form_data,
    )
    await check_file_metadata(filename, now + time_delta, new_user_filename)


async def test_update_file_user_custom_metadata(
        web_app_client, mock_mds_s3, mock_storage,
):
    async def test_file(
            project_slug,
            filename,
            new_user_filename,
            new_user_comment,
            expected_status,
    ):
        request_json = {}
        if new_user_filename is not None:
            request_json['user_filename'] = new_user_filename
        if new_user_comment is not None:
            request_json['user_comment'] = new_user_comment
        if not request_json:
            request_json = None

        response = await web_app_client.put(
            f'v1/files/metadata/user_custom/audio/{filename}'
            f'?project_slug={project_slug}&user_id=34',
            json=request_json,
        )
        assert response.status == expected_status
        if expected_status > 300:
            return
        response = await web_app_client.get(
            f'v1/files/metadata/audio/{filename}'
            f'?project_slug={project_slug}&user_id=34',
        )
        response_json = await response.json()
        assert response.status == 200
        response_user_filename = response_json.get('user_filename')
        response_user_comment = response_json.get('user_comment')
        if new_user_filename:
            assert response_user_filename == new_user_filename
        else:
            assert response_user_filename is None
        if new_user_comment:
            assert response_user_comment == new_user_comment
        else:
            assert response_user_comment is None

    await test_file('slug1', 'file1.wav', 'new_name', 'new_comment', 200)
    await test_file(
        'slug1', 'file1.wav', 'rewritten_name', 'rewritten_comment', 200,
    )
    await test_file('slug1', 'file1.wav', None, None, 200)
    await test_file('slug2', 'file1.wav', 'new_file2_user_filename', None, 200)
    await test_file('slug1', 'no_such_file', '', '', 404)
    await test_file('no_such_project', 'whatever', '', '', 400)


@pytest.mark.parametrize('call_service', ['voximplant', 'ivr_framework'])
async def test_upload_audio_files_for_other_call_services(
        web_app_client,
        mockserver,
        patch,
        mock_mds_s3,
        mock_storage,
        call_service,
):
    vox_bucket = mock_storage['supportai-calls']
    ivr_framework_bucket = mock_storage['ivr-dispatcher']

    expected_bucket, unexpected_bucket = (
        (vox_bucket, ivr_framework_bucket)
        if call_service == 'voximplant'
        else (ivr_framework_bucket, vox_bucket)
    )

    file_data = b'DANNYE UDALENY'
    random_secret = '1234567890'

    @patch('supportai_calls.utils.file_helpers._create_ffmpeg_subprocess')
    async def _(*args, **kwargs):
        return DummyOutput(file_data)

    @patch(
        'supportai_calls.utils.project_config_helpers.generate_random_secret',
    )
    def _():
        return random_secret

    project_slug = 'project_with_another_call_service'

    assert (
        await web_app_client.post(
            f'v1/project_configs?project_slug={project_slug}&user_id=34',
            json={
                'dispatcher_params': (
                    {
                        'call_service': 'voximplant',
                        'api_key': '',
                        'account_id': 0,
                        'rule_id': 0,
                    }
                    if call_service == 'voximplant'
                    else {'call_service': 'ivr_framework'}
                ),
            },
        )
    ).status == 200

    basename = 'some_name'
    filename = f'{basename}.wav'

    form_data = aiohttp.FormData()
    form_data.add_field(
        name='file',
        value=file_data,
        filename=filename,
        content_type='audio/something',
    )

    assert (
        await web_app_client.post(
            f'v1/files/audio?project_slug={project_slug}&user_id=34',
            data=form_data,
        )
    ).status == 200

    expected_key = (
        f'voximplant/{project_slug}/{basename}{random_secret}.mp3'
        if call_service == 'voximplant'
        else f'ivr_flow_worker/{project_slug}/{basename}.wav'
    )

    assert expected_key in expected_bucket
    assert expected_key not in unexpected_bucket
    assert expected_bucket[expected_key] == file_data
