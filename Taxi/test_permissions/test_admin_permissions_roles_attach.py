import pytest


SQL_FILES = ['add_systems.sql', 'add_roles.sql', 'add_permissions.sql']


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_attach_all_success(
        permissions_roles_attach_request,
        assert_response,
        assert_link_added,
        links_to_response,
):
    links = [
        ('system_main_role_2', 'system_main_role_1_permission_1'),
        ('system_main_role_3', 'system_main_role_1_permission_1'),
        ('system_main_role_3', 'system_main_empty_permission_1'),
    ]
    response = await permissions_roles_attach_request('system_main', links)
    assert_response(response, 200, {'links': links_to_response(links)})
    await assert_link_added(links)


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_attach_some_exist(
        permissions_roles_attach_request,
        assert_response,
        assert_link_added,
        links_to_response,
        links_to_errors,
):
    links = [
        ('system_main_role_1', 'system_main_role_1_permission_1'),
        ('system_main_role_3', 'system_main_role_1_permission_1'),
        ('system_main_role_3', 'system_main_role_3_permission_1'),
    ]
    response = await permissions_roles_attach_request('system_main', links)
    assert_response(
        response,
        200,
        {
            'errors': links_to_errors([links[0], links[2]]),
            'links': links_to_response([links[1]]),
        },
    )
    await assert_link_added([links[1]])


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_attach_from_wrong_system(
        permissions_roles_attach_request,
        assert_response,
        assert_link_added,
        links_to_errors,
):
    links = [('system_second_role_1', 'system_main_role_1_permission_1')]
    response = await permissions_roles_attach_request('system_main', links)
    assert_response(
        response, 200, {'links': [], 'errors': links_to_errors(links)},
    )
    await assert_link_added([])


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_attach_not_found_system(
        permissions_roles_attach_request,
        assert_response,
        assert_link_added,
        links_to_errors,
):
    links = [('system_main_role_1', 'system_main_role_1_permission_1')]
    response = await permissions_roles_attach_request('not_found', links)
    assert_response(
        response, 200, {'errors': links_to_errors(links), 'links': []},
    )
    await assert_link_added([])


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_attach_not_found_role_and_permission(
        permissions_roles_attach_request,
        assert_response,
        assert_link_added,
        links_to_response,
        links_to_errors,
):
    links = [
        ('not_found', 'system_main_role_1_permission_1'),
        ('system_main_role_1', 'not_found'),
        ('system_main_role_1', 'system_main_role_3_permission_1'),
    ]
    response = await permissions_roles_attach_request('system_main', links)
    assert_response(
        response,
        200,
        {
            'errors': links_to_errors([links[0], links[1]]),
            'links': links_to_response([links[2]]),
        },
    )
    await assert_link_added([links[2]])


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_attach_duplicate(
        permissions_roles_attach_request,
        assert_response,
        assert_link_added,
        links_to_response,
):
    links = [
        ('system_main_role_1', 'system_main_role_3_permission_1'),
        ('system_main_role_1', 'system_main_role_3_permission_1'),
        ('system_main_role_1', 'system_main_role_3_permission_1'),
    ]
    response = await permissions_roles_attach_request('system_main', links)
    assert_response(response, 200, {'links': links_to_response(links)})
    await assert_link_added([links[0]])
