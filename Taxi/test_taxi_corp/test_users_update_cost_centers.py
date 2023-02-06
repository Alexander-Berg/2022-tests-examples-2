import pytest

LONG_DEFAULT_CC = 'cc' * 256 + '_'  # 513 symbols


@pytest.mark.parametrize(
    ['client_id', 'post_content', 'expected'],
    [
        pytest.param(
            'client1',
            {
                'role': {'role_id': 'role1'},
                'cost_center': 'some_default',
                'cost_centers': {
                    'required': True,
                    'format': 'mixed',
                    'values': ['1,2,3,4,5'],
                },
            },
            {
                'custom_user0': {'cost_center': 'MoeCostCenter'},
                'role1_user1': {
                    'cost_center': 'some_default',
                    'cost_centers': {
                        'required': True,
                        'format': 'mixed',
                        'values': ['1,2,3,4,5'],
                    },
                },
                'role1_user2': {
                    'cost_center': 'some_default',
                    'cost_centers': {
                        'required': True,
                        'format': 'mixed',
                        'values': ['1,2,3,4,5'],
                    },
                },
                'deleted_role1_user3': {
                    'cost_center': 'some_default',
                    'cost_centers': {
                        'required': True,
                        'format': 'mixed',
                        'values': ['1,2,3,4,5'],
                    },
                },
                'role2_user0': {'cost_center': 'hoeCostCenter'},
                'client2_role3_user1': {'cost_center': 'client2_default'},
            },
            id='old-cost-centers-client1',
            marks=pytest.mark.filldb(corp_cost_center_options='empty'),
        ),
        pytest.param(
            'client2',
            {
                'role': {'role_id': 'role3'},
                'cost_centers': {
                    'required': True,
                    'format': 'mixed',
                    'values': ['1,2,3,4,5'],
                },
            },
            {
                'custom_user0': {'cost_center': 'MoeCostCenter'},
                'role1_user1': {
                    'cost_center': 'ZoeCostCenter',
                    'cost_centers': {
                        'required': False,
                        'format': 'mixed',
                        'values': ['123', '12321', '12323423'],
                    },
                },
                'role1_user2': {},
                'deleted_role1_user3': {'cost_center': 'hoeCostCenter'},
                'role2_user0': {'cost_center': 'hoeCostCenter'},
                'client2_role3_user1': {
                    'cost_center': '',
                    'cost_centers': {
                        'required': True,
                        'format': 'mixed',
                        'values': ['1,2,3,4,5'],
                    },
                },
            },
            id='old-cost-centers-client2',
        ),
        pytest.param(
            'client1',
            {
                'role': {'role_id': 'role1'},
                'cost_centers_id': 'other_cc_options_id',
            },
            {
                'custom_user0': {'cost_center': 'MoeCostCenter'},
                'role1_user1': {
                    'cost_center': 'ZoeCostCenter',
                    'cost_centers': {
                        'required': False,
                        'format': 'mixed',
                        'values': ['123', '12321', '12323423'],
                    },
                    'cost_centers_id': 'other_cc_options_id',
                },
                'role1_user2': {'cost_centers_id': 'other_cc_options_id'},
                'deleted_role1_user3': {
                    'cost_center': 'hoeCostCenter',
                    'cost_centers_id': 'other_cc_options_id',
                },
                'role2_user0': {'cost_center': 'hoeCostCenter'},
                'client2_role3_user1': {'cost_center': 'client2_default'},
            },
            id='new-cost-centers',
        ),
    ],
)
async def test_cost_centers_bulk_update(
        taxi_corp_auth_client, db, client_id, post_content, expected,
):
    response = await taxi_corp_auth_client.post(
        '/1.0/client/{}/users/update_cost_centers'.format(client_id),
        json=post_content,
    )
    response_json = await response.json()
    assert response.status == 200, response_json

    users = await db.corp_users.find().to_list(None)
    role_users = {
        u['_id']: {
            k: u.get(k)
            for k in ('cost_center', 'cost_centers', 'cost_centers_id')
            if k in u
        }
        for u in users
    }
    assert role_users == expected


@pytest.mark.parametrize(
    ['client_id', 'post_content', 'expected_error'],
    [
        pytest.param(
            'client1',
            {
                'role': {'role_id': 'role1'},
                'cost_center': 'some_default',
                'cost_centers': {
                    'format': 'select',
                    'required': True,
                    'values': [],
                },
            },
            {'code': 'REQUEST_VALIDATION_ERROR'},
            id='empty-values',
            marks=pytest.mark.filldb(corp_cost_center_options='empty'),
        ),
        pytest.param(
            'client1',
            {
                'role': {'role_id': 'role1'},
                'cost_center': LONG_DEFAULT_CC,
                'cost_centers': {
                    'format': 'text',
                    'required': False,
                    'values': [],
                },
            },
            {'code': 'REQUEST_VALIDATION_ERROR'},
            id='long-default-cc',
            marks=pytest.mark.filldb(corp_cost_center_options='empty'),
        ),
        pytest.param(
            'client1',
            {'role': {'role_id': 'role1'}, 'cost_center': 'some_default'},
            {'code': 'REQUEST_VALIDATION_ERROR'},
            id='no-cost_centers-field-no-new-cc',
            marks=pytest.mark.filldb(corp_cost_center_options='empty'),
        ),
        pytest.param(
            'client1',
            {'role': {'role_id': 'role1'}, 'cost_center': 'some_default'},
            {'code': 'CLIENT_OLD_FORMAT_COST_CENTERS_NO_MORE_SUPPORTED'},
            id='no-cost_centers_id-field-with-new-cc',
        ),
        pytest.param(
            'client1',
            {
                'role': {'role_id': 'role1'},
                'cost_centers_id': 'unknown_cost_centers_id',
            },
            {'code': 'CLIENT_COST_CENTERS_NOT_FOUND'},
            id='cost-centers-not-found',
        ),
    ],
)
async def test_cost_centers_update_fail(
        taxi_corp_auth_client, db, client_id, post_content, expected_error,
):
    response = await taxi_corp_auth_client.post(
        '/1.0/client/{}/users/update_cost_centers'.format(client_id),
        json=post_content,
    )
    response_json = await response.json()
    assert response.status == 400
    assert response_json['code'] == expected_error['code']
