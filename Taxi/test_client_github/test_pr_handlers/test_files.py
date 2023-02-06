import pytest

from client_github import types


def _case(file_name, id_=None):
    return pytest.param(file_name, id=id_)


@pytest.mark.parametrize('responses_filename', [_case('get_pr_files.json')])
async def test_get_pull_files(
        load_json,
        library_context,
        patch_get_pull_requests_info,
        get_mock_responses,
        responses_filename,
):
    patch_get_pull_requests_info(
        user='taxi',
        repo='backend-py3',
        number=1,
        pr_info_type=types.PRInfoVariant.files,
        responses=get_mock_responses(load_json(responses_filename)),
    )
    response = await library_context.client_github.get_pull_request_files(
        user='taxi', repo='backend-py3', number=1,
    )
    assert len(response) == 2
    assert [x.filename for x in response] == [
        'checks/pg_taxi-infra_clowny_balancer_stable',
        'checks/pg_taxi-infra_clowny_perforator_stable',
    ]
