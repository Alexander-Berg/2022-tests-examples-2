import pytest

from generated.clients import github as gh_api

from client_github import components as github


FILE_CONTENT_MOCK = 'test data'
GITHUB_USER = 'taxi'
GITHUB_REPO = 'backend-py3'
BRANCH_MOCK = 'test-branch'
SHA_MOCK = 'e3443502b8fd692b789f9af514b335bce53f0667'


async def test_read_file(library_context, patch):
    @patch('taxi.clients.github.GithubClient.get_single_file')
    async def _get_single_file(**kwargs):
        try:
            return FILE_CONTENT_MOCK.encode('utf-8')
        except FileNotFoundError:
            raise github.BaseError('Client error')

    file = await library_context.client_github.get_single_file(
        user='taxi', repo='backend-py3', reference='develop', path='README.md',
    )
    assert file.decode('utf-8') == FILE_CONTENT_MOCK
    assert len(_get_single_file.calls) == 1


@pytest.mark.parametrize(
    'expected_error, server_error, responses_filename',
    [
        pytest.param(github.ApiError, False, None, id='client_error'),
        pytest.param(
            github.AuthorizationError,
            True,
            'github_handler_response_403.json',
            id='authorization_error',
        ),
        pytest.param(
            github.NotFoundError,
            True,
            'github_handler_response_404.json',
            id='not_found_error',
        ),
        pytest.param(
            github.Unprocessable,
            True,
            'github_handler_response_422.json',
            id='unprocessable_error',
        ),
        pytest.param(
            github.BadResponseError,
            True,
            'github_handler_responses_500.json',
            id='server_error',
        ),
    ],
)
@pytest.mark.parametrize(
    'method_name, kwargs',
    [
        pytest.param(
            github.GithubClient.get_reference.__name__,
            {
                'user': GITHUB_USER,
                'repo': GITHUB_REPO,
                'ref': f'heads/{BRANCH_MOCK}',
            },
            id=github.GithubClient.get_reference.__name__,
        ),
        pytest.param(
            github.GithubClient.create_reference.__name__,
            {
                'user': GITHUB_USER,
                'repo': GITHUB_REPO,
                'ref': f'heads/{BRANCH_MOCK}',
                'sha': SHA_MOCK,
            },
            id=github.GithubClient.create_reference.__name__,
        ),
        pytest.param(
            github.GithubClient.update_reference.__name__,
            {
                'user': GITHUB_USER,
                'repo': GITHUB_REPO,
                'ref': f'heads/{BRANCH_MOCK}',
                'commit_sha': SHA_MOCK,
            },
            id=github.GithubClient.update_reference.__name__,
        ),
        pytest.param(
            github.GithubClient.delete_reference.__name__,
            {
                'user': GITHUB_USER,
                'repo': GITHUB_REPO,
                'ref': f'heads/{BRANCH_MOCK}',
            },
            id=github.GithubClient.delete_reference.__name__,
        ),
        pytest.param(
            github.GithubClient.merge_branch_.__name__,
            {
                'user': GITHUB_USER,
                'repo': GITHUB_REPO,
                'base': 'develop',
                'head': BRANCH_MOCK,
            },
            id=github.GithubClient.merge_branch_.__name__,
        ),
        pytest.param(
            github.GithubClient.get_blob.__name__,
            {'user': GITHUB_USER, 'repo': GITHUB_REPO, 'sha': SHA_MOCK},
            id=github.GithubClient.get_blob.__name__,
        ),
        pytest.param(
            github.GithubClient.create_blob_.__name__,
            {
                'user': GITHUB_USER,
                'repo': GITHUB_REPO,
                'content': 'test',
                'encoding': 'base64',
            },
            id=github.GithubClient.create_blob_.__name__,
        ),
        pytest.param(
            github.GithubClient.get_tree.__name__,
            {'user': GITHUB_USER, 'repo': GITHUB_REPO, 'tree_sha': SHA_MOCK},
            id=github.GithubClient.get_tree.__name__,
        ),
        pytest.param(
            github.GithubClient.create_tree.__name__,
            {'user': GITHUB_USER, 'repo': GITHUB_REPO, 'tree': []},
            id=github.GithubClient.create_tree.__name__,
        ),
        pytest.param(
            github.GithubClient.get_commit_object.__name__,
            {'user': GITHUB_USER, 'repo': GITHUB_REPO, 'commit_sha': SHA_MOCK},
            id=github.GithubClient.get_commit_object.__name__,
        ),
        pytest.param(
            github.GithubClient.create_commit_object.__name__,
            {
                'user': GITHUB_USER,
                'repo': GITHUB_REPO,
                'tree_sha': SHA_MOCK,
                'message': 'test',
                'parents': [],
            },
            id=github.GithubClient.create_commit_object.__name__,
        ),
        pytest.param(
            github.GithubClient.get_commit_.__name__,
            {'user': GITHUB_USER, 'repo': GITHUB_REPO, 'reference': SHA_MOCK},
            id=github.GithubClient.get_commit_.__name__,
        ),
        pytest.param(
            github.GithubClient.get_pull_request.__name__,
            {'user': GITHUB_USER, 'repo': GITHUB_REPO, 'number': 123},
            id=github.GithubClient.get_pull_request.__name__,
        ),
        pytest.param(
            github.GithubClient.get_pull_requests.__name__,
            {'user': GITHUB_USER, 'repo': GITHUB_REPO},
            id=github.GithubClient.get_pull_requests.__name__,
        ),
        pytest.param(
            github.GithubClient.create_pull_request_.__name__,
            {
                'user': GITHUB_USER,
                'repo': GITHUB_REPO,
                'base': 'develop',
                'head': BRANCH_MOCK,
                'title': 'test-pr',
            },
            id=github.GithubClient.create_pull_request_.__name__,
        ),
        pytest.param(
            github.GithubClient.get_pull_request_files.__name__,
            {'user': GITHUB_USER, 'repo': GITHUB_REPO, 'number': 123},
            id=github.GithubClient.get_pull_request_files.__name__,
        ),
        pytest.param(
            github.GithubClient.get_pull_reviews.__name__,
            {'user': GITHUB_USER, 'repo': GITHUB_REPO, 'number': 123},
            id=github.GithubClient.get_pull_reviews.__name__,
        ),
        pytest.param(
            github.GithubClient.merge_pull_request.__name__,
            {
                'user': GITHUB_USER,
                'repo': GITHUB_REPO,
                'number': 123,
                'commit_title': 'test',
                'commit_message': 'test message',
                'head_sha': SHA_MOCK,
            },
            id=github.GithubClient.merge_pull_request.__name__,
        ),
    ],
)
async def test_catch_base_api_errors(
        library_context,
        patch,
        load_json,
        patch_github_handler,
        get_mock_responses,
        method_name,
        kwargs,
        expected_error,
        server_error,
        responses_filename,
):
    if server_error:
        patch_github_handler(
            f'/api/v3/repos/{GITHUB_USER}/{GITHUB_REPO}',
            responses=get_mock_responses(load_json(responses_filename)),
            prefix=True,
        )
    else:

        @patch(
            f'generated.clients.github.GithubClient.{method_name.rstrip("_")}',
        )
        async def _client_mock(**kwargs):
            raise gh_api.ClientException()

    assert hasattr(library_context.client_github, method_name)
    func = getattr(library_context.client_github, method_name)
    with pytest.raises(expected_error):
        await func(**kwargs)
