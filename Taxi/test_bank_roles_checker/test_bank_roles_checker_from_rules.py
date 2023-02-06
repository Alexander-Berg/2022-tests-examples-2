import pytest

from bank_roles_checker import component
from bank_roles_checker import models


async def test_roles_found(bank_roles_checker, bank_idm_mock):
    system_slug = 'configs'
    login = models.UserLogin('first')

    await bank_roles_checker.check_rule_role(system_slug, 'BANK_TEST', login)
    assert bank_idm_mock.get_user_roles.times_called == 1


@pytest.mark.parametrize(
    'login,rule,error,times_called',
    [
        ('first', 'CORE_TEST', 'Role not found', 1),
        ('first', 'unknown', 'Role not found', 2),
        (
            'unknown',
            'CORE_TEST',
            'Getting roles error: bank-idm response, status: 404, '
            'body: Error(code=\'404\', message=\'No user\')',
            1,
        ),
    ],
)
async def test_roles_not_found(
        bank_roles_checker, bank_idm_mock, login, rule, error, times_called,
):
    system_slug = 'configs'
    login = models.UserLogin(login)
    with pytest.raises(component.BankRoleError) as exc:
        await bank_roles_checker.check_rule_role(system_slug, rule, login)
    assert exc.value.args[0] == error
    assert bank_idm_mock.get_user_roles.times_called == times_called


async def test_roles_found_from_extra(bank_roles_checker, bank_idm_mock):
    system_slug = 'configs'
    login = models.UserLogin('third')

    await bank_roles_checker.check_rule_role(system_slug, 'unknown', login)
    assert bank_idm_mock.get_user_roles.times_called > 0


@pytest.mark.parametrize(
    'rule,slug_path,is_found',
    [
        ('BANK_TEST', 'cpp_programmer', True),
        ('CORE_TEST', 'java_programmer', False),
    ],
)
async def test_roles_found_at_cache(
        bank_roles_checker, bank_idm_mock, rule, slug_path, is_found,
):
    login = models.UserLogin('first')

    await bank_roles_checker.check_rule_role('configs', 'BANK_TEST', login)

    assert bank_idm_mock.get_user_roles.times_called == 1

    try:
        await bank_roles_checker.check_role(
            models.BankRole('configs', slug_path), login,
        )
    except component.BankRoleError:
        assert not is_found
    else:
        assert is_found
    count = 1 if is_found is True else 2
    assert bank_idm_mock.get_user_roles.times_called == count


@pytest.mark.parametrize(
    'rule,logins',
    [('BANK_CONFIG', {'second', 'first'}), ('CORE_CONFIG', set())],
)
async def test_approvers_found(
        bank_roles_checker, bank_idm_mock, rule, logins,
):
    result = await bank_roles_checker.get_approvers_by_rule('configs', rule)
    assert result == logins
    assert bank_idm_mock.get_logins.times_called == 1


async def test_approvers_not_found(bank_roles_checker, bank_idm_mock):
    await bank_roles_checker.get_approvers_by_rule('configs', 'unknown')
    assert bank_idm_mock.get_logins.times_called == 2


@pytest.mark.parametrize(
    'rule,logins', [('BANK_TEST', {'second', 'first'}), ('CORE_TEST', set())],
)
async def test_approvers_found_at_cache(
        bank_roles_checker, bank_idm_mock, rule, logins,
):
    await bank_roles_checker.get_approvers_by_rule('configs', 'BANK_TEST')
    assert bank_idm_mock.get_logins.times_called == 1

    result = await bank_roles_checker.get_approvers_by_rule('configs', rule)

    assert result == logins
    count = 1 if len(logins) == 2 else 2
    assert bank_idm_mock.get_logins.times_called == count


@pytest.mark.parametrize('login,is_found', [('first', False), ('third', True)])
async def test_role_in_exception_group(
        bank_roles_checker, bank_idm_mock, login, is_found,
):
    login = models.UserLogin(login)

    try:
        await bank_roles_checker.check_rule_role(
            'configs', 'BANK_ROLES_CHECKER_APPROVE_RULES', login,
        )
    except component.BankRoleError:
        assert not is_found
    else:
        assert is_found


async def test_exception_groups(bank_roles_checker, bank_idm_mock):
    result = await bank_roles_checker.get_approvers_by_rule(
        'configs', 'BANK_ROLES_CHECKER_APPROVE_RULES',
    )
    assert result == {'third'}
