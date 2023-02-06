import pytest

import arcanum_api.components as arcanum_api


PULL_REQUEST_SHORT_MOCK = {
    'id': 123456,
    'url': 'https://a.yandex-team.ru/review/123456',
}
PULL_REQUEST_MOCK = {
    **PULL_REQUEST_SHORT_MOCK,
    'author': 'robot-taxi',
    'auto_merge': 'on_satisfied_requirements',
    'created_at': '2021-08-10T16:29:44.888582Z',
    'description': 'pull request description',
    'merge_allowed': False,
    'status': 'open',
    'summary': 'feat arcanum-api: test pr',
    'updated_at': '2021-08-10T16:29:51.673650Z',
    'vcs': {
        'from_branch': 'users/robot-taxi/test-branch',
        'to_branch': 'trunk',
        'type': 'arc',
    },
}


@pytest.mark.parametrize(
    'responses_filename, expected_error, expected_data',
    [
        pytest.param(
            'arcanum_get_pull_request_success_200.json',
            None,
            PULL_REQUEST_SHORT_MOCK,
            id='success',
        ),
        pytest.param(
            'arcanum_get_pull_request_success_200.json',
            None,
            PULL_REQUEST_MOCK,
            id='return_additional_fields',
        ),
    ],
)
async def test_get_pull_request(
        library_context,
        patch_arcanum_pr_handler,
        load_json,
        _get_mock_responses,
        _try_call,
        responses_filename,
        expected_error,
        expected_data,
):
    pr_number = 123456
    return_fields = list(expected_data.keys())

    responses = _get_mock_responses(load_json(responses_filename))
    pull_requests_mock_handler = patch_arcanum_pr_handler(
        number=pr_number,
        responses=responses,
        return_fields=(return_fields if not expected_error else None),
    )

    call = library_context.arcanum_api.get_pull_request(
        number=pr_number, return_additional_fields=return_fields,
    )
    pull_request = await _try_call(call, expected_error)

    assert pull_requests_mock_handler.times_called == len(responses)
    if not expected_error:
        assert pull_request.serialize() == expected_data


@pytest.mark.parametrize(
    'responses_filename, expected_error, expected_data',
    [
        pytest.param(
            'arcanum_create_pull_request_success_200.json',
            None,
            PULL_REQUEST_SHORT_MOCK,
            id='success',
        ),
        pytest.param(
            'arcanum_create_pull_request_success_200.json',
            None,
            PULL_REQUEST_MOCK,
            id='return_additional_fields',
        ),
        pytest.param(
            'arcanum_create_pull_request_already_exists_409.json',
            arcanum_api.AlreadyExistsError,
            PULL_REQUEST_SHORT_MOCK,
            id='already_exists',
        ),
        pytest.param(
            'arcanum_create_pull_request_branch_not_found_500.json',
            arcanum_api.ArcanumApiBaseError,
            PULL_REQUEST_SHORT_MOCK,
            id='branch_not_found',
        ),
    ],
)
async def test_create_pull_request(
        library_context,
        patch_arcanum_pr_handler,
        load_json,
        _get_mock_responses,
        _try_call,
        responses_filename,
        expected_error,
        expected_data,
):
    user = 'robot-taxi'
    base = 'trunk'
    head = 'test-branch'
    title = 'feat arcanum-api: test pr'
    description = 'pull request description'
    return_fields = list(expected_data.keys())

    responses = _get_mock_responses(load_json(responses_filename))
    pull_requests_mock_handler = patch_arcanum_pr_handler(
        number=None,
        responses=responses,
        return_fields=(return_fields if not expected_error else None),
    )

    call = library_context.arcanum_api.create_pull_request(
        user=user,
        base=base,
        head=head,
        title=title,
        description=description,
        return_additional_fields=list(return_fields),
    )
    pull_request = await _try_call(call, expected_error)

    assert pull_requests_mock_handler.times_called == len(responses)
    if not expected_error:
        assert pull_request.serialize() == expected_data
        assert pull_requests_mock_handler.next_call()['request'].json == {
            'summary': title,
            'description': description,
            'vcs': {'to_branch': base, 'from_branch': f'users/{user}/{head}'},
            'on_new_diffset': {'publish': True},
        }
