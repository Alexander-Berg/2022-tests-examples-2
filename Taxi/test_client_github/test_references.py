import pytest

from client_github import components as github


GITHUB_USER = 'taxi'
GITHUB_REPO = 'backend-py3'
BRANCH_MOCK = 'test-branch'
SHA_MOCK = 'e3443502b8fd692b789f9af514b335bce53f0667'


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [
        pytest.param(
            None, 'get_reference_response_200.json', id='branch_exists',
        ),
        pytest.param(
            github.NotFoundError,
            'get_reference_response_404.json',
            id='branch_not_exists',
        ),
    ],
)
async def test_get_reference(
        library_context,
        patch_refs_handler,
        get_mock_responses,
        load_json,
        _try_call,
        expected_error,
        responses_filename,
):
    ref = f'heads/{BRANCH_MOCK}'
    get_ref_handler = patch_refs_handler(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        ref=ref,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.get_reference(
        user=GITHUB_USER, repo=GITHUB_REPO, ref=ref,
    )

    git_ref = await _try_call(call, expected_error)
    if not expected_error:
        assert git_ref.ref == f'refs/{ref}'
        assert git_ref.object.sha == SHA_MOCK

    assert get_ref_handler.times_called == 1


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [
        pytest.param(
            None, 'create_ref_response_201.json', id='branch_created',
        ),
        pytest.param(
            github.AlreadyExistsError,
            'create_ref_response_422.json',
            id='branch_already_exists',
        ),
    ],
)
async def test_create_reference(
        library_context,
        patch_refs_handler,
        get_mock_responses,
        load_json,
        _try_call,
        expected_error,
        responses_filename,
):
    ref = f'heads/{BRANCH_MOCK}'
    create_ref_handler = patch_refs_handler(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        ref=None,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.create_reference(
        user=GITHUB_USER, repo=GITHUB_REPO, ref=ref, sha=SHA_MOCK,
    )

    git_ref = await _try_call(call, expected_error)
    if not expected_error:
        assert git_ref.ref == f'refs/{ref}'

    assert create_ref_handler.times_called == 1
    assert create_ref_handler.next_call()['request'].json == {
        'ref': ref,
        'sha': SHA_MOCK,
    }


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [
        pytest.param(None, 'update_reference_response_200.json', id='success'),
        pytest.param(
            github.NoFastForwardError,
            'update_reference_response_422.json',
            id='dangerous_update_error',
        ),
    ],
)
async def test_update_reference(
        library_context,
        patch_refs_handler,
        get_mock_responses,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
):
    ref = f'heads/{BRANCH_MOCK}'
    update_ref_handler = patch_refs_handler(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        ref=ref,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.update_reference(
        user=GITHUB_USER, repo=GITHUB_REPO, ref=ref, commit_sha=SHA_MOCK,
    )

    git_ref = await _try_call(call, expected_error)
    if not expected_error:
        assert git_ref.ref == f'refs/{ref}'

    assert update_ref_handler.times_called == 1
    assert update_ref_handler.next_call()['request'].json == {'sha': SHA_MOCK}


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [
        pytest.param(None, 'delete_reference_response_200.json', id='success'),
        pytest.param(
            github.NotFoundError,
            'delete_reference_response_422.json',
            id='already_deleted',
        ),
    ],
)
async def test_delete_reference(
        library_context,
        patch_refs_handler,
        get_mock_responses,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
):
    ref = f'heads/{BRANCH_MOCK}'
    delete_ref_handler = patch_refs_handler(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        ref=ref,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.delete_reference(
        user=GITHUB_USER, repo=GITHUB_REPO, ref=ref,
    )
    await _try_call(call, expected_error)

    assert delete_ref_handler.times_called == 1
