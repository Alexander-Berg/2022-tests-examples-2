import asyncpg
import pytest


async def test_abc_role_for_non_existing_scope(add_subsystem, add_role):
    subsystem_id = await add_subsystem('subsystem')
    with pytest.raises(
            asyncpg.RaiseError,
            match=(
                r'abc scope\(missing_abc_slug\) '
                r'not exists for standalone type'
            ),
    ):
        await add_role(
            'test_slug', 'missing_abc_slug', 'standalone', subsystem_id,
        )


@pytest.mark.parametrize('soft_delete', [True, False])
async def test_remove_abc_scope_with_roles(
        add_abc_scope, add_subsystem, add_role, delete_abc_scope, soft_delete,
):
    scope = await add_abc_scope('some_slug')
    subsystem_id = await add_subsystem('subsystem')
    await add_role('test_slug', scope, 'standalone', subsystem_id)
    with pytest.raises(
            asyncpg.RaiseError,
            match=(
                r'cant remove abc scope\(some_slug\), '
                r'cause there are some related roles'
            ),
    ):
        await delete_abc_scope(scope, soft_delete)
