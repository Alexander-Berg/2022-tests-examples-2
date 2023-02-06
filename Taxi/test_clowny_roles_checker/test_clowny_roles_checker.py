import pytest

from clowny_roles_checker import component
from clowny_roles_checker import models


@pytest.mark.parametrize(
    ['login', 'expected_roles'],
    [
        pytest.param(
            'superuser',
            {
                'clowny_role_1': models.AggregatedRole(
                    role=models.UserRole('clowny_role_1'),
                    namespaces=set(),
                    projects={models.ProjectName('taxi-support')},
                    abc_slugs={models.AbcSlug('lavkaakeneo')},
                ),
                'clowny_role_2': models.AggregatedRole(
                    role=models.UserRole('clowny_role_2'),
                    namespaces=set(),
                    projects={models.ProjectName('taxi-infra')},
                    abc_slugs=set(),
                ),
                'clowny_role_3': models.AggregatedRole(
                    role=models.UserRole('clowny_role_3'),
                    namespaces={models.TplatformNamespace('taxi')},
                    projects=set(),
                    abc_slugs=set(),
                ),
                'clowny_role_4': models.AggregatedRole(
                    role=models.UserRole('clowny_role_4'),
                    namespaces=set(),
                    projects=set(),
                    abc_slugs={models.AbcSlug('abc-random-slug')},
                ),
                'common_clown_role': models.AggregatedRole(
                    role=models.UserRole('common_clown_role'),
                    namespaces=set(),
                    projects=set(),
                    abc_slugs={models.AbcSlug('some')},
                ),
            },
            id='superuser',
        ),
        pytest.param(
            'some_man',
            {
                'clowny_role_1': models.AggregatedRole(
                    role=models.UserRole('clowny_role_1'),
                    namespaces=set(),
                    projects=set(),
                    abc_slugs={models.AbcSlug('lavkaakeneo')},
                ),
                'clowny_role_2': models.AggregatedRole(
                    role=models.UserRole('clowny_role_2'),
                    namespaces=set(),
                    projects=set(),
                    abc_slugs={models.AbcSlug('lavkaakeneo')},
                ),
                'clowny_role_3': models.AggregatedRole(
                    role=models.UserRole('clowny_role_3'),
                    namespaces=set(),
                    projects=set(),
                    abc_slugs={models.AbcSlug('lavkaakeneo')},
                ),
            },
            id='some_man',
        ),
        pytest.param('noone', {}, id='noone'),
    ],
)
async def test_retrieve_roles(
        clowny_roles_checker, grands_retrieve_mock, login, expected_roles,
):
    mock = grands_retrieve_mock()
    login = models.UserLogin(login)
    roles = await clowny_roles_checker.retriever.retrieve_roles(login)
    assert roles == expected_roles
    assert mock.times_called == 1
    request = mock.next_call()['args'][0]
    assert request.json == {'filters': {'login': login}, 'limit': 1000}
    assert request.query == {}


@pytest.mark.parametrize(
    ['field'],
    [
        pytest.param(
            models.RoleField(
                role=models.UserRole('clowny_role_1'),
                field_type=models.FieldType.ABC_SLUG,
                field_value='lavkaakeneo',
            ),
            id='simple_role',
        ),
        pytest.param(
            models.RoleField(
                role=models.UserRole('clowny_role_1'),
                field_type=models.FieldType.PROJECT_NAME,
                field_value='taxi-support',
            ),
            id='simple_role_from_project',
        ),
        pytest.param(
            models.RoleField(
                role=models.UserRole('clowny_role_1'),
                field_type=models.FieldType.SERVICE_ID,
                field_value=354601,
            ),
            id='abc_in_project',
        ),
        pytest.param(
            models.RoleField(
                role=models.UserRole('clowny_role_3'),
                field_type=models.FieldType.TPLATFORM_NAMESPACE,
                field_value='taxi',
            ),
            id='simple_role_from_namespace',
        ),
        pytest.param(
            models.RoleField(
                role=models.UserRole('clowny_role_3'),
                field_type=models.FieldType.PROJECT_NAME,
                field_value='taxi-support',
            ),
            id='project_in_namespace',
        ),
        pytest.param(
            models.RoleField(
                role=models.UserRole('clowny_role_3'),
                field_type=models.FieldType.ABC_SLUG,
                field_value='taxicompendium',
            ),
            id='abc_project_in_namespace',
        ),
    ],
)
async def test_good_check_role(
        clowny_roles_checker, grands_retrieve_mock, field,
):
    grands_retrieve_mock()
    await clowny_roles_checker.check_role(field, models.UserLogin('superuser'))


@pytest.mark.parametrize(
    ['field'],
    [
        pytest.param(
            models.RoleField(
                role=models.UserRole('clowny_role_1'),
                field_type=models.FieldType.ABC_SLUG,
                field_value='bad_slug',
            ),
            id='bad_slug',
        ),
        pytest.param(
            models.RoleField(
                role=models.UserRole('no_role'),
                field_type=models.FieldType.SERVICE_ID,
                field_value=354601,
            ),
            id='no_role',
        ),
        pytest.param(
            models.RoleField(
                role=models.UserRole('clowny_role_3'),
                field_type=models.FieldType.PROJECT_NAME,
                field_value='eda',
            ),
            id='no_project_in_namespace',
        ),
        pytest.param(
            models.RoleField(
                role=models.UserRole('clowny_role_3'),
                field_type=models.FieldType.ABC_SLUG,
                field_value='lavkaakeneo',
            ),
            id='no_abc_project_in_namespace',
        ),
    ],
)
async def test_bad_check_role(
        clowny_roles_checker, grands_retrieve_mock, field,
):
    grands_retrieve_mock()
    with pytest.raises(component.CheckRoleError):
        await clowny_roles_checker.check_role(
            field, models.UserLogin('superuser'),
        )


@pytest.mark.parametrize(
    ['field', 'expected'],
    [
        pytest.param(
            models.RoleField(
                models.UserRole('clowny_role_3'),
                models.FieldType.ABC_SLUG,
                'lavkaakeneo',
            ),
            {'some_man'},
            id='service_in_lavka',
        ),
        pytest.param(
            models.RoleField(
                models.UserRole('clowny_role_3'),
                models.FieldType.ABC_SLUG,
                'no_service',
            ),
            set(),
            id='no_service',
        ),
        pytest.param(
            models.RoleField(
                models.UserRole('clowny_role_3'),
                models.FieldType.PROJECT_NAME,
                'taxi-ml',
            ),
            {'superuser'},
            id='project_in_taxi',
        ),
        pytest.param(
            models.RoleField(
                models.UserRole('clowny_role_1'),
                models.FieldType.ABC_SLUG,
                'lavkaakeneo',
            ),
            {'superuser', 'some_man'},
            id='role_for_service',
        ),
    ],
)
async def test_retrieve_approvers(
        clowny_roles_checker, grands_retrieve_mock, field, expected,
):
    mock = grands_retrieve_mock()
    logins = await clowny_roles_checker.retriever.retrieve_approvers(field)
    assert logins == expected
    assert mock.times_called == 1


async def test_take_approvers_cache(
        clowny_roles_checker, grands_retrieve_mock,
):
    mock = grands_retrieve_mock()
    field = models.RoleField(
        models.UserRole('clowny_role_1'),
        models.FieldType.ABC_SLUG,
        'lavkaakeneo',
    )
    expected = {'superuser', 'some_man'}
    logins = await clowny_roles_checker.take_approvers(field)
    assert logins == expected
    logins = await clowny_roles_checker.take_approvers(field)
    assert logins == expected
    assert mock.times_called == 1


async def test_none_retrieve_approvers(
        clowny_roles_checker, grands_retrieve_mock,
):
    logins = await clowny_roles_checker.retriever.retrieve_approvers(
        models.RoleField(
            models.UserRole('clowny_role_1'), models.FieldType.ABC_SLUG, None,
        ),
    )
    assert logins == set()


async def test_bad_retrieve_approvers(
        clowny_roles_checker, grands_retrieve_mock,
):
    logins = await clowny_roles_checker.retriever.retrieve_approvers(
        models.RoleField(
            models.UserRole('clowny_role_1'),
            models.FieldType.BRANCH_ID,
            'bad',
        ),
    )
    assert logins == set()


@pytest.mark.parametrize(
    'field, login, expected_logins',
    [
        (
            models.RoleField(
                models.UserRole('clowny_role_1'),
                models.FieldType.ABC_SLUG,
                'lavkaakeneo',
            ),
            None,
            ['superuser', 'some_man'],
        ),
        (None, 'some_man', ['some_man']),
        (None, 'some bad man', []),
    ],
)
async def test_take_grants_for(
        clowny_roles_checker,
        grands_retrieve_mock,
        field,
        login,
        expected_logins,
):
    mock = grands_retrieve_mock()

    async def _do_it():
        grants = await clowny_roles_checker.take_grants_for(field, login)
        assert [x.grand.login for x in grants] == expected_logins

    await _do_it()
    await _do_it()
    assert mock.times_called == 1
