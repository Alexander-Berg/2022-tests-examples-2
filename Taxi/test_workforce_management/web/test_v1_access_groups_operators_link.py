import pytest


URI = '/v1/access-groups/operators/link'
UNLINK_URI = '/v1/access-groups/operators/unlink'
REVISION_ID = '2020-08-25T21:00:00.000000 +0000'
WRONG_REVISION_ID = '2020-07-25T21:00:00.000000 +0000'


@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, non_existing_users, non_existing_groups, '
    'invalid_users, expected_status',
    [
        (
            {
                'operators': [
                    {'yandex_uid': 'uid1', 'revision_id': REVISION_ID},
                ],
                'group': 'group1',
            },
            [],
            [],
            [],
            200,
        ),
        (
            {
                'operators': [
                    {'yandex_uid': 'uid1', 'revision_id': REVISION_ID},
                ],
                'group': 'group1',
            },
            [],
            ['group1'],
            [],
            400,
        ),
        (
            {
                'operators': [
                    {'yandex_uid': 'uid1', 'revision_id': WRONG_REVISION_ID},
                ],
                'group': 'group1',
            },
            [],
            [],
            [],
            409,
        ),
        (
            {
                'operators': [
                    {'yandex_uid': 'uid1', 'revision_id': REVISION_ID},
                ],
                'group': 'group1',
            },
            [{'provider': 'yandex', 'provider_user_id': 'uid1'}],
            [],
            [],
            400,
        ),
        (
            {
                'operators': [
                    {'yandex_uid': 'uid1', 'revision_id': REVISION_ID},
                ],
                'group': 'group1',
            },
            [],
            [],
            [{'provider': 'yandex', 'provider_user_id': 'uid1'}],
            400,
        ),
    ],
)
async def test_base(
        taxi_workforce_management_web,
        mockserver,
        tst_request,
        non_existing_users,
        non_existing_groups,
        invalid_users,
        expected_status,
):
    @mockserver.json_handler('/access-control/v1/admin/users/bulk-create/')
    def bulk_create(request, *args, **kwargs):
        assert len(request.json['users']) == len(tst_request['operators'])
        return {
            'created_users': [
                {'provider': 'yandex', 'provider_user_id': 'uid1'},
            ],
            'existing_users': [],
            'invalid_users': invalid_users,
        }

    @mockserver.json_handler(
        '/access-control/v1/admin/users/bulk-add-to-system/',
    )
    def bulk_add(request, *args, **kwargs):
        assert len(request.json['users']) == len(tst_request['operators'])
        assert request.json['groups'] == [tst_request['group']]
        assert request.query['system'] == 'wfm_effrat'
        return {
            'non_existing_groups': non_existing_groups,
            'non_existing_users': non_existing_users,
            'invalid_users': [],
        }

    res = await taxi_workforce_management_web.post(URI, json=tst_request)
    assert res.status == expected_status
    assert bulk_add.times_called or invalid_users or res.status == 409
    assert bulk_create.times_called or res.status == 409


@pytest.mark.pgsql('workforce_management', files=['simple_operators.sql'])
@pytest.mark.parametrize(
    'tst_request, errors, expected_status',
    [
        (
            {
                'operators': [
                    {'yandex_uid': 'uid1', 'revision_id': REVISION_ID},
                ],
                'group': 'group1',
            },
            [],
            200,
        ),
        (
            {
                'operators': [
                    {'yandex_uid': 'uid1', 'revision_id': WRONG_REVISION_ID},
                ],
                'group': 'group1',
            },
            [],
            409,
        ),
        (
            {
                'operators': [
                    {'yandex_uid': 'uid1', 'revision_id': REVISION_ID},
                ],
                'group': 'group1',
            },
            [{'code': 'fatal error'}],
            500,
        ),
    ],
)
async def test_unlink(
        taxi_workforce_management_web,
        mockserver,
        tst_request,
        errors,
        expected_status,
):
    @mockserver.json_handler(
        '/access-control/v1/admin/groups' '/users/bulk-detach/',
    )
    def bulk_delete(request, *args, **kwargs):
        assert len(request.json['users']) == len(tst_request['operators'])
        return {'detached_users': request.json['users'], 'errors': errors}

    res = await taxi_workforce_management_web.post(
        UNLINK_URI, json=tst_request,
    )
    assert res.status == expected_status
    assert bulk_delete.times_called or res.status == 409
