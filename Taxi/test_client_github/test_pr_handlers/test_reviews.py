import pytest

from client_github import types


def _case(file_name, id_=None):
    return pytest.param(file_name, id=id_)


@pytest.mark.parametrize('responses_filename', [_case('get_pr_reviews.json')])
async def test_get_pull_files(
        load_json,
        library_context,
        patch_get_pull_requests_info,
        get_mock_responses,
        responses_filename,
):
    patch_get_pull_requests_info(
        user='taxi',
        repo='infra-cfg-juggler',
        number=1,
        pr_info_type=types.PRInfoVariant.reviews,
        responses=get_mock_responses(load_json(responses_filename)),
    )
    response = await library_context.client_github.get_pull_reviews(
        user='taxi', repo='infra-cfg-juggler', number=1,
    )
    assert len(response) == 2
    assert {x.user.login for x in response} == {'d1mbas'}
    assert [x.state for x in response] == ['APPROVED', 'COMMENTED']
