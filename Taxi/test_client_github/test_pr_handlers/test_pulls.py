import pytest

from client_github import components as github


GITHUB_USER = 'taxi'
GITHUB_REPO = 'backend-py3'
BRANCH_MOCK = 'test-branch'


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [pytest.param(None, 'get_pull_request_response_200.json', id='success')],
)
async def test_get_pull_request(
        library_context,
        patch_get_pull_request,
        get_mock_responses,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
):
    pull_request_number = 1
    get_pull_request_handler = patch_get_pull_request(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        number=pull_request_number,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.get_pull_request(
        user=GITHUB_USER, repo=GITHUB_REPO, number=pull_request_number,
    )
    pull_request = await _try_call(call, expected_error)
    if not expected_error:
        assert pull_request.number == pull_request_number

    assert get_pull_request_handler.times_called == 1


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [pytest.param(None, 'get_pull_requests_response_200.json', id='success')],
)
async def test_get_pull_requests(
        library_context,
        patch_get_pull_request,
        get_mock_responses,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
):
    head_branch_filter = 'spolischouck:test-branch'
    get_pull_requests_handler = patch_get_pull_request(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        number=None,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.get_pull_requests(
        user=GITHUB_USER, repo=GITHUB_REPO, head=head_branch_filter,
    )
    pull_requests = await _try_call(call, expected_error)
    if not expected_error:
        assert len(pull_requests) == 1
        assert pull_requests.pop().head.label == head_branch_filter

    assert get_pull_requests_handler.times_called == 1


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [
        pytest.param(
            None, 'create_pull_request_response_201.json', id='success',
        ),
        pytest.param(
            github.AlreadyExistsError,
            'create_pull_request__already_exists_response_422.json',
            id='already_exists',
        ),
        pytest.param(
            github.NoDiffError,
            'create_pull_request__no_diff_response_422.json',
            id='already_exists',
        ),
    ],
)
async def test_create_pull_request(
        library_context,
        patch_create_pull_request,
        get_mock_responses,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
):
    head = BRANCH_MOCK
    base = 'develop'
    title = 'feat test-service: add feature'
    body = 'TAXIPLATFORM-1234'
    create_pull_request_handler = patch_create_pull_request(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.create_pull_request_(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        base=base,
        head=head,
        title=title,
        body=body,
    )
    pull_request = await _try_call(call, expected_error)
    if not expected_error:
        assert pull_request.head.ref == head
        assert pull_request.title == title
        assert pull_request.body == body

    assert create_pull_request_handler.times_called == 1
    assert create_pull_request_handler.next_call()['request'].json == {
        'base': base,
        'head': head,
        'title': title,
        'body': body,
    }
