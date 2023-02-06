import pytest

from bank_roles_checker import component
from bank_roles_checker import models


async def test_roles_found(bank_roles_checker, bank_idm_mock):
    login = 'first'
    login = models.UserLogin(login)

    await bank_roles_checker.check_role(
        models.BankRole('configs', 'cpp_programmer'), login,
    )
    assert bank_idm_mock.get_user_roles.times_called == 1


@pytest.mark.parametrize(
    'login,error',
    (
        (
            'not_found',
            'Getting roles error: bank-idm response, status: 404, '
            'body: Error(code=\'404\', message=\'No user\')',
        ),
        ('first', 'Role not found'),
    ),
)
async def test_roles_not_found(
        bank_roles_checker, bank_idm_mock, login, error,
):
    login = models.UserLogin(login)

    with pytest.raises(component.BankRoleError) as exc:
        await bank_roles_checker.check_role(
            models.BankRole('exps', 'path/exps'), login,
        )
    assert exc.value.args[0] == error
    assert bank_idm_mock.get_user_roles.times_called == 1


@pytest.mark.parametrize(
    'system_slug,slug_path,found',
    [('configs', 'cpp_programmer', True), ('exps', 'path/exps', False)],
)
async def test_roles_found_at_cache(
        bank_roles_checker, bank_idm_mock, system_slug, slug_path, found,
):
    login = 'first'
    login = models.UserLogin(login)

    await bank_roles_checker.check_role(
        models.BankRole('configs', 'cpp_programmer'), login,
    )
    assert bank_idm_mock.get_user_roles.times_called == 1

    try:
        await bank_roles_checker.check_role(
            models.BankRole(system_slug, slug_path), login,
        )
    except component.BankRoleError:
        assert not found
    else:
        assert found
    count = 1 if found is True else 2
    assert bank_idm_mock.get_user_roles.times_called == count


@pytest.mark.parametrize(
    'role',
    [
        ('cpp_programmer', 'configs', {'second', 'first'}),
        ('path/exps', 'exps', set()),
    ],
)
async def test_approvers_found(bank_roles_checker, bank_idm_mock, role):
    result = await bank_roles_checker.take_approvers(
        models.BankRole(role[1], role[0]),
    )
    assert result == role[2]
    assert bank_idm_mock.get_logins.times_called == 1


async def test_approvers_not_found(bank_roles_checker, bank_idm_mock):
    with pytest.raises(component.BankRoleError):
        await bank_roles_checker.take_approvers(
            models.BankRole('unknown', 'unknown'),
        )
    assert bank_idm_mock.get_logins.times_called == 1


@pytest.mark.parametrize(
    'role',
    [
        ('cpp_programmer', 'configs', {'second', 'first'}),
        ('path/exps', 'exps', set()),
    ],
)
async def test_approvers_found_at_cache(
        bank_roles_checker, bank_idm_mock, role,
):
    await bank_roles_checker.take_approvers(
        models.BankRole('configs', 'cpp_programmer'),
    )
    assert bank_idm_mock.get_logins.times_called == 1

    result = await bank_roles_checker.take_approvers(
        models.BankRole(role[1], role[0]),
    )

    assert result == role[2]
    count = 1 if len(role[2]) == 2 else 2
    assert bank_idm_mock.get_logins.times_called == count
