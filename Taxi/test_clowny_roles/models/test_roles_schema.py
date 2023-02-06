import pytest

from clowny_roles.components.roles_schema import component
from clowny_roles.generated.web import web_context as web_module


INTERNAL_ID = 1
APPROVALS_ID = 2


@pytest.fixture(autouse=True)
def _add_subsystems(local_add_subsystem):
    local_add_subsystem('internal')
    local_add_subsystem('approvals')


@pytest.fixture(name='add_test_role')
def _add_test_role(add_registered_role):
    def _wrapper(slug, subsystem_id):
        return add_registered_role(
            slug,
            ['namespace', 'project', 'service'],
            subsystem_id,
            ('test', 'test'),
            ('test', 'test'),
        )

    return _wrapper


@pytest.fixture(name='add_internal_role')
def _add_internal_role(add_test_role):
    def _wrapper(slug):
        return add_test_role(slug, INTERNAL_ID)

    return _wrapper


@pytest.fixture(name='add_approvals_role')
def _add_approvals_role(add_test_role):
    def _wrapper(slug):
        return add_test_role(slug, APPROVALS_ID)

    return _wrapper


@pytest.fixture(name='component_manager')
def _component_manager(web_context) -> component.RolesSchemaManager:
    return web_context.roles_schema


@pytest.fixture(autouse=True)
def _default_registered_roles():
    return


@pytest.fixture(name='init_simple_roles')
def _init_simple_roles(add_internal_role):
    add_internal_role('slug1')
    add_internal_role('slug2')


@pytest.mark.usefixtures('init_simple_roles')
async def test_simple_roles(component_manager):
    roles_schema = component_manager.roles
    assert len(roles_schema) == 2
    assert roles_schema['slug1']
    assert roles_schema['slug2']
    assert not roles_schema.dependencies_slugs('slug1')
    assert not roles_schema.dependencies_slugs('slug2')


@pytest.fixture(name='init_simple_roles_includes')
def _init_simple_roles_includes(
        add_internal_role, add_approvals_role, add_roles_includes,
):
    slug1_id = add_internal_role('slug1')
    slug2_id = add_approvals_role('slug2')
    slug3_id = add_internal_role('slug3')
    add_roles_includes(slug1_id, [slug2_id])
    add_roles_includes(slug3_id, [slug1_id, slug2_id])


@pytest.mark.usefixtures('init_simple_roles_includes')
async def test_simple_roles_includes(component_manager):
    roles_schema = component_manager.roles
    assert len(roles_schema) == 3
    assert roles_schema['slug1'].subsystem.slug == 'internal'
    assert roles_schema['slug2'].subsystem.slug == 'approvals'
    assert roles_schema['slug3'].subsystem.slug == 'internal'
    assert roles_schema.dependencies_slugs('slug1') == ['slug2']
    assert roles_schema.dependencies_slugs('slug2') == []
    assert roles_schema.dependencies_slugs('slug3') == ['slug1', 'slug2']


@pytest.fixture(name='init_not_simple_roles_includes')
def _init_not_simple_roles_includes(
        add_internal_role, add_approvals_role, add_roles_includes,
):
    slug_internal_1 = add_internal_role('slug_internal_1')
    slug_approvals_1 = add_approvals_role('slug_approvals_1')
    slug_approvals_2 = add_approvals_role('slug_approvals_2')
    slug_internal_2 = add_internal_role('slug_internal_2')
    slug_internal_3 = add_internal_role('slug_internal_3')
    add_internal_role('slug_internal_4')
    slug_internal_5 = add_internal_role('slug_internal_5')

    add_roles_includes(slug_approvals_2, [slug_approvals_1])
    add_roles_includes(slug_internal_3, [slug_internal_2, slug_internal_1])
    add_roles_includes(slug_internal_1, [slug_approvals_2])
    add_roles_includes(slug_internal_5, [slug_internal_1, slug_internal_3])


@pytest.mark.usefixtures('init_not_simple_roles_includes')
async def test_not_simple_roles_includes(component_manager):
    roles_schema = component_manager.roles
    exprected_slugs = {
        'slug_internal_1': ['slug_approvals_1', 'slug_approvals_2'],
        'slug_internal_2': [],
        'slug_internal_3': [
            'slug_approvals_1',
            'slug_approvals_2',
            'slug_internal_1',
            'slug_internal_2',
        ],
        'slug_internal_4': [],
        'slug_internal_5': [
            'slug_approvals_1',
            'slug_approvals_2',
            'slug_internal_1',
            'slug_internal_2',
            'slug_internal_3',
        ],
        'slug_approvals_1': [],
        'slug_approvals_2': ['slug_approvals_1'],
    }
    assert len(roles_schema) == len(exprected_slugs)
    for existed_slug, includes in exprected_slugs.items():
        assert roles_schema[existed_slug]
        assert roles_schema.dependencies_slugs(existed_slug) == includes


@pytest.fixture(name='init_cycle_includes')
def _init_cycle_includes(add_internal_role, add_roles_includes):
    slug_internal_1 = add_internal_role('slug_internal_1')
    slug_internal_2 = add_internal_role('slug_internal_2')
    slug_internal_3 = add_internal_role('slug_internal_3')
    slug_internal_4 = add_internal_role('slug_internal_4')

    add_roles_includes(slug_internal_1, [slug_internal_4])
    add_roles_includes(slug_internal_2, [slug_internal_1])
    add_roles_includes(slug_internal_3, [slug_internal_1, slug_internal_2])
    add_roles_includes(slug_internal_4, [slug_internal_3])


@pytest.mark.usefixtures('init_cycle_includes')
async def test_cycle_includes():
    ctx = web_module.create_context()
    expected_msg = (
        'Cycle includes slug_'
        'internal_4 -> slug_internal_3 -> slug_internal_1 -> slug_internal_4'
    )
    with pytest.raises(component.CycleInclude, match=f'^{expected_msg}$'):
        await ctx.on_startup()
    await ctx.on_shutdown()
