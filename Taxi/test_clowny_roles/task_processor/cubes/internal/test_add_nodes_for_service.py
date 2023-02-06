import pytest

CUBE_NAME = 'InternalAddNodesForService'


@pytest.mark.roles_features_on('internal_add_nodes_for_service')
async def test_cube(load_yaml, get_roles, call_cube):
    old_roles = await get_roles(
        external_ref_slug='srv-1-slug', ref_type='service',
    )
    assert not old_roles
    response = await call_cube(CUBE_NAME, {'clown_service_id': 1})
    assert response == {'status': 'success'}
    new_roles = await get_roles(
        external_ref_slug='srv-1-slug', ref_type='service',
    )
    assert [x.as_dict() for x in new_roles] == load_yaml(
        'expected_new_roles.yaml',
    )
