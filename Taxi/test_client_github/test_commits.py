import pytest


GITHUB_USER = 'taxi'
GITHUB_REPO = 'backend-py3'
BRANCH_MOCK = 'test-branch'
SHA_MOCK = 'e3443502b8fd692b789f9af514b335bce53f0667'


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [pytest.param(None, 'get_commit_object_response_200.json', id='success')],
)
async def test_get_commit_object(
        library_context,
        patch_get_commit_object,
        get_mock_responses,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
):
    commit_sha = SHA_MOCK
    get_commit_handler = patch_get_commit_object(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        commit_sha=commit_sha,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.get_commit_object(
        user=GITHUB_USER, repo=GITHUB_REPO, commit_sha=commit_sha,
    )
    git_commit = await _try_call(call, expected_error)
    if not expected_error:
        assert git_commit.sha == commit_sha

    assert get_commit_handler.times_called == 1


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [pytest.param(None, 'create_commit_response_201.json', id='success')],
)
async def test_create_commit_object(
        library_context,
        patch_create_commit_object,
        get_mock_responses,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
):
    tree_object_sha = 'e7eaa233ce71818b7cf5f40fcfcb73ca99426530'
    create_commit_object_handler = patch_create_commit_object(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.create_commit_object(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        tree_sha=tree_object_sha,
        message='test commit',
        parents=['parent-sha-mock'],
    )
    git_commit = await _try_call(call, expected_error)
    if not expected_error:
        assert git_commit.tree.sha == tree_object_sha

    assert create_commit_object_handler.times_called == 1
    assert create_commit_object_handler.next_call()['request'].json == {
        'tree': tree_object_sha,
        'message': 'test commit',
        'parents': ['parent-sha-mock'],
    }


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [pytest.param(None, 'get_commit_response_200.json', id='success')],
)
async def test_get_commit(
        library_context,
        patch_get_commit,
        get_mock_responses,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
):
    commit_sha = SHA_MOCK
    get_commit_handler = patch_get_commit(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        ref=BRANCH_MOCK,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.get_commit_(
        user=GITHUB_USER, repo=GITHUB_REPO, reference=BRANCH_MOCK,
    )
    github_commit = await _try_call(call, expected_error)
    if not expected_error:
        assert github_commit.sha == commit_sha

    assert get_commit_handler.times_called == 1
