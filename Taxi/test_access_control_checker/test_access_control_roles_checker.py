import pytest

from access_control_roles_checker import component


@pytest.mark.parametrize(
    'permission, uid, expected_res',
    [
        ('permission1', 'uid1', True),
        ('non_existing_permission', 'uid1', False),
        ('non_existing_permission', 'uid3', False),
        ('permission4', 'uid3', True),
    ],
)
async def test_check_user(
        access_control_roles_checker,
        access_control_mock,
        permission,
        uid,
        expected_res,
):
    if expected_res:
        await access_control_roles_checker.check_role(permission, uid)
    else:
        with pytest.raises(component.AccessControlError):
            await access_control_roles_checker.check_role(permission, uid)

    assert access_control_mock.check_users.times_called == 1


@pytest.mark.parametrize(
    'permission, uid, expected_res',
    [
        ('permission1', 'uid1', True),
        ('non_existing_permission', 'uid1', False),
    ],
)
async def test_roles_found_at_cache(
        access_control_roles_checker,
        access_control_mock,
        permission,
        uid,
        expected_res,
):
    if expected_res:
        await access_control_roles_checker.check_role(permission, uid)
    else:
        with pytest.raises(component.AccessControlError):
            await access_control_roles_checker.check_role(permission, uid)

    assert access_control_mock.check_users.times_called == 1

    if expected_res:
        await access_control_roles_checker.check_role(permission, uid)
    else:
        with pytest.raises(component.AccessControlError):
            await access_control_roles_checker.check_role(permission, uid)

    assert access_control_mock.check_users.times_called == 1 + bool(
        not expected_res,
    )


@pytest.mark.parametrize(
    'permission, expected_users',
    [
        ('permission1', {'uid1'}),
        ('permission2', {'uid1', 'uid2'}),
        ('non_existing_permission', set()),
    ],
)
async def test_approvers_found(
        access_control_roles_checker,
        access_control_mock,
        permission,
        expected_users,
):
    result = await access_control_roles_checker.take_approvers(permission)
    assert result == expected_users
    assert access_control_mock.check_users.times_called == 1


@pytest.mark.parametrize(
    'permission, expected_users',
    [
        ('permission1', {'uid1'}),
        ('permission2', {'uid1', 'uid2'}),
        ('non_existing_permission', set()),
    ],
)
async def test_approvers_found_at_cache(
        access_control_roles_checker,
        access_control_mock,
        permission,
        expected_users,
):
    result = await access_control_roles_checker.take_approvers(permission)
    assert result == expected_users
    assert access_control_mock.check_users.times_called == 1

    result = await access_control_roles_checker.take_approvers(permission)

    assert result == expected_users
    assert access_control_mock.check_users.times_called == 1
