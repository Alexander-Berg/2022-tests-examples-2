import pytest

from client_github import components as github
from client_github import types


@pytest.mark.parametrize(
    'responses_filename, success',
    [
        pytest.param('success_merge.json', True),
        pytest.param('no_access_merge.json', False),
    ],
)
async def test_merge_pr(
        load_json,
        library_context,
        patch_get_pull_requests_info,
        get_mock_responses,
        responses_filename,
        success,
):
    mock_data = load_json(responses_filename)
    patch_get_pull_requests_info(
        user='taxi',
        repo='infra-cfg-juggler',
        number=1,
        pr_info_type=types.PRInfoVariant.merge,
        responses=get_mock_responses(mock_data['responses']),
        expected_requests=mock_data['requests'],
    )

    _call = library_context.client_github.merge_pull_request(
        user='taxi',
        repo='infra-cfg-juggler',
        number=1,
        commit_title='test merge',
        commit_message='test merge body',
        head_sha='123',
    )

    if success:
        response = await _call
        assert response.merged is True
    else:
        with pytest.raises(github.NotFoundError) as exc:
            await _call
            assert exc.content == {
                'message': 'Not Found',
                'documentation_url': (
                    'https://developer.github.com/enterprise/2.21/v3/pulls/'
                    '#merge-a-pull-request-merge-button'
                ),
            }
