import pytest

from client_github import components as github


GITHUB_USER = 'taxi'
GITHUB_REPO = 'backend-py3'
BRANCH_MOCK = 'test-branch'


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [
        pytest.param(None, 'merge_branch_response_201.json', id='success'),
        pytest.param(
            github.AlreadyExistsError,
            'merge_branch_response_204.json',
            id='already_merged',
        ),
    ],
)
async def test_merge_branch(
        library_context,
        patch_merge_branch_handler,
        get_mock_responses,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
):
    base = 'develop'
    head = BRANCH_MOCK
    merge_branch_handler = patch_merge_branch_handler(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.merge_branch_(
        user=GITHUB_USER, repo=GITHUB_REPO, base=base, head=head,
    )
    github_commit = await _try_call(call, expected_error)
    if not expected_error:
        assert github_commit.commit.message == f'Merge {head} into {base}'
        assert len(github_commit.parents) == 2

    assert merge_branch_handler.times_called == 1
    assert merge_branch_handler.next_call()['request'].json == {
        'base': base,
        'head': head,
    }
