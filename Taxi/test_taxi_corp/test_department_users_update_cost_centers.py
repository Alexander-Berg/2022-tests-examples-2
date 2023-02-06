import pytest


@pytest.mark.parametrize(
    [
        'passport_mock',
        'client_id',
        'request_json',
        'response_status',
        'changed_users',
    ],
    [
        # success: change for department (other users untouched)
        pytest.param(
            'client_1',
            'client_1',
            {'department_id': 'd1', 'cost_centers_id': 'cc_option_1'},
            200,
            {'user_1', 'user_2'},
            id='success-department-d1-client_1',
        ),
        # success: change for subdepartment (other users untouched)
        pytest.param(
            'client_1',
            'client_1',
            {'department_id': 'd1_1', 'cost_centers_id': 'cc_option_1'},
            200,
            {'user_2'},
            id='success-department-d1_1',
        ),
        # error: client does not have such department
        pytest.param(
            'client_1',
            'client_1',
            {'department_id': 'd1_2', 'cost_centers_id': 'cc_option_1'},
            404,
            {},
            id='error-department-d1_2-client_1',
        ),
        # error: department belongs to other client
        pytest.param(
            'client_2',
            'client_2',
            {'department_id': 'd1', 'cost_centers_id': 'cc_option_1'},
            403,
            {},
            id='error-department-d1-client_2',
        ),
        # error: client does not have such cost center option
        pytest.param(
            'client_1',
            'client_1',
            {'department_id': 'd1', 'cost_centers_id': 'cc_option_2'},
            400,
            {},
            id='error-absent-option-in-db',
        ),
        # error: no option in request
        pytest.param(
            'client_1',
            'client_1',
            {'department_id': 'd1'},
            400,
            {},
            id='error-absent-option-in-request',
        ),
        # error: no department in request
        pytest.param(
            'client_1',
            'client_1',
            {'cost_centers_id': 'cc_option_2'},
            400,
            {},
            id='error-absent-department-in-request',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_department_users_cost_centers(
        db,
        taxi_corp_real_auth_client,
        passport_mock,
        client_id,
        request_json,
        response_status,
        changed_users,
):
    response = await taxi_corp_real_auth_client.post(
        f'/1.0/client/{client_id}/department_users/update_cost_centers',
        json=request_json,
    )
    response_json = await response.json()
    assert response.status == response_status, response_json

    users = await db.corp_users.find().to_list(None)
    for user in users:
        if user['_id'] in changed_users:
            assert user['cost_centers_id'] == request_json['cost_centers_id']
        else:
            assert 'cost_centers_id' not in user
