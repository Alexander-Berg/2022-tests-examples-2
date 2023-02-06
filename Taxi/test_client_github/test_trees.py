import pytest

from generated.models import github as gh_models

from client_github import components as github


GITHUB_USER = 'taxi'
GITHUB_REPO = 'backend-py3'
TREE_SHA_MOCK = 'e7eaa233ce71818b7cf5f40fcfcb73ca99426530'


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [pytest.param(None, 'get_tree_response_200.json', id='success')],
)
async def test_get_tree(
        library_context,
        patch_get_tree,
        get_mock_responses,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
):
    get_tree_handler = patch_get_tree(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        tree_sha=TREE_SHA_MOCK,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.get_tree(
        user=GITHUB_USER, repo=GITHUB_REPO, tree_sha=TREE_SHA_MOCK,
    )
    git_tree = await _try_call(call, expected_error)
    if not expected_error:
        assert git_tree.sha == TREE_SHA_MOCK

    assert get_tree_handler.times_called == 1


@pytest.mark.parametrize(
    'expected_error, responses_filename',
    [pytest.param(None, 'create_tree_response_201.json', id='success')],
)
async def test_create_tree(
        library_context,
        patch_create_tree,
        get_mock_responses,
        load_json,
        _try_call,
        responses_filename,
        expected_error,
):
    tree_object_sha = 'f0d39ceec053c6115aea2e4abc1e426a5904c948'
    create_tree_handler = patch_create_tree(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        responses=get_mock_responses(load_json(responses_filename)),
    )

    call = library_context.client_github.create_tree(
        user=GITHUB_USER,
        repo=GITHUB_REPO,
        tree=[
            gh_models.GithubCreateTreeObject(
                path='service.yaml',
                mode=github.FileMode.FILE.value,
                type=github.GitTreeObjectType.BLOB.value,
                sha=tree_object_sha,
            ),
        ],
    )

    git_tree = await _try_call(call, expected_error)
    if not expected_error:
        assert any(tree.sha == tree_object_sha for tree in git_tree.tree)

    assert create_tree_handler.times_called == 1
    assert create_tree_handler.next_call()['request'].json == {
        'tree': [
            {
                'mode': '100644',
                'path': 'service.yaml',
                'sha': tree_object_sha,
                'type': 'blob',
            },
        ],
    }
