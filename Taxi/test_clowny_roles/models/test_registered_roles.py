from clowny_roles.internal.models import common
from clowny_roles.internal.models import registered_role


async def test_batch_upsert(web_context, add_subsystem):
    subsystem_id = await add_subsystem('internal')
    new_roles = [
        registered_role.AddRole(
            slug='new_role_1',
            scopes=[common.ExternalRefType.namespace],
            fields=None,
            name=common.Translatable('new_role_1', 'new_role_1'),
            help=common.Translatable('new_role_1', 'new_role_1'),
            visible=True,
            subsystem_id=subsystem_id,
            includes=(),
        ),
        registered_role.AddRole(
            slug='new_role_2',
            scopes=[common.ExternalRefType.service],
            fields=None,
            name=common.Translatable('new_role_2', 'new_role_2'),
            help=common.Translatable('new_role_2', 'new_role_2'),
            visible=True,
            subsystem_id=subsystem_id,
            includes=('new_role_1',),
        ),
    ]
    await web_context.pg_manager.registered_role.upsert_batch(
        web_context.pg.primary, new_roles,
    )

    all_db_roles = await web_context.pg_manager.registered_role.fetch_all(
        web_context.pg.primary,
    )
    expected_db_roles = {
        x.slug: x
        for x in all_db_roles
        if x.slug in ('new_role_1', 'new_role_2')
    }
    assert expected_db_roles['new_role_2'].includes == (
        expected_db_roles['new_role_1'].db_meta.id,
    )
