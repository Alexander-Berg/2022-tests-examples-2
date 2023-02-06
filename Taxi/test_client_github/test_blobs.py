import pytest

from client_github import components as github


GITHUB_USER = 'taxi'
GITHUB_REPO = 'backend-py3'
CONTENT_MOCK = 'SGVsbG8gd29ybGQ='
SHA_MOCK = '6b584e8ece562ebffc15d38808cd6b98fc3d97ea'


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [pytest.param(None, 'get_blob_response_200.json', id='success')],
)
async def test_get_blob(
        library_context,
        patch_blobs_handler,
        get_mock_responses,
        load_json,
        _try_call,
        expected_error,
        responses_filename,
):
    get_blob_handler = patch_blobs_handler(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        sha=SHA_MOCK,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.get_blob(
        user=GITHUB_USER, repo=GITHUB_REPO, sha=SHA_MOCK,
    )
    blob = await _try_call(call, expected_error)
    if not expected_error:
        assert blob.sha == SHA_MOCK
        assert blob.url == (
            'https://github.yandex-team.ru/api/v3/repos/taxi/'
            f'backend-py3/git/blobs/{SHA_MOCK}'
        )

    assert get_blob_handler.times_called == 1


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [pytest.param(None, 'create_blob_response_201.json', id='success')],
)
async def test_create_blob(
        library_context,
        patch_blobs_handler,
        get_mock_responses,
        load_json,
        _try_call,
        expected_error,
        responses_filename,
):
    create_blob_handler = patch_blobs_handler(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        sha=None,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.create_blob(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        content=CONTENT_MOCK,
        encoding=github.FileEncoding.BASE_64.value,
    )

    blob = await _try_call(call, expected_error)
    if not expected_error:
        assert blob.sha == SHA_MOCK
        assert blob.url == (
            'https://github.yandex-team.ru/api/v3/repos/taxi/'
            f'backend-py3/git/blobs/{SHA_MOCK}'
        )

    assert create_blob_handler.times_called == 1
    assert create_blob_handler.next_call()['request'].json == {
        'content': CONTENT_MOCK,
        'encoding': 'base64',
    }
