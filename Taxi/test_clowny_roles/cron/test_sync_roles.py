import operator

import pytest

from clowny_roles.internal.models import common as common_models
from clowny_roles.internal.models import role as role_models

EXISTED = [
    {'slug': 'test_user', 'external_slug': 'taxi', 'ref_type': 'namespace'},
    {'slug': 'test_user', 'external_slug': 'prj-1', 'ref_type': 'project'},
    {'slug': 'test_user', 'external_slug': 'prj-2', 'ref_type': 'project'},
    {
        'slug': 'test_user',
        'external_slug': 'srv-1-slug',
        'ref_type': 'service',
    },
    {
        'slug': 'test_task_manager',
        'external_slug': 'market',
        'ref_type': 'namespace',
    },
    {
        'slug': 'test_service_responsible',
        'external_slug': 'market',
        'ref_type': 'namespace',
    },
]


EXPECTED = [
    {
        'external_slug': 'market',
        'ref_type': 'namespace',
        'slug': 'approvals_user',
    },
    {
        'external_slug': 'taxi',
        'ref_type': 'namespace',
        'slug': 'approvals_user',
    },
    {
        'external_slug': 'market',
        'ref_type': 'namespace',
        'slug': 'approvals_view',
    },
    {
        'external_slug': 'taxi',
        'ref_type': 'namespace',
        'slug': 'approvals_view',
    },
    {
        'external_slug': 'srv-1-slug',
        'ref_type': 'service',
        'slug': 'test_admin',
    },
    {
        'external_slug': 'srv-3-slug',
        'ref_type': 'service',
        'slug': 'test_admin',
    },
    {
        'external_slug': 'srv-4-slug',
        'ref_type': 'service',
        'slug': 'test_admin',
    },
    {
        'external_slug': 'srv-5-slug',
        'ref_type': 'service',
        'slug': 'test_admin',
    },
    {
        'external_slug': 'srv-6-slug',
        'ref_type': 'service',
        'slug': 'test_admin',
    },
    {
        'external_slug': 'srv-4-slug',
        'ref_type': 'service',
        'slug': 'test_user',
    },
    {
        'external_slug': 'srv-5-slug',
        'ref_type': 'service',
        'slug': 'test_user',
    },
    {
        'external_slug': 'srv-6-slug',
        'ref_type': 'service',
        'slug': 'test_user',
    },
    {
        'external_slug': 'srv-3-slug',
        'ref_type': 'service',
        'slug': 'test_user',
    },
    {
        'external_slug': 'taxi',
        'ref_type': 'namespace',
        'slug': 'test_service_responsible',
    },
    {
        'external_slug': 'prj-1',
        'ref_type': 'project',
        'slug': 'test_task_manager',
    },
    {
        'external_slug': 'prj-2',
        'ref_type': 'project',
        'slug': 'test_task_manager',
    },
    {
        'external_slug': 'prj-3',
        'ref_type': 'project',
        'slug': 'test_task_manager',
    },
    {
        'external_slug': 'prj-4',
        'ref_type': 'project',
        'slug': 'test_task_manager',
    },
    {'external_slug': 'prj-3', 'ref_type': 'project', 'slug': 'test_user'},
    {'external_slug': 'prj-4', 'ref_type': 'project', 'slug': 'test_user'},
    {
        'external_slug': 'taxi',
        'ref_type': 'namespace',
        'slug': 'test_task_manager',
    },
    {'external_slug': 'market', 'ref_type': 'namespace', 'slug': 'test_user'},
]


@pytest.fixture(name='add_role')
def _add_role(cron_context):
    async def _request(
            role_slug: str,
            external_slug: str,
            ref_type: common_models.ExternalRefType,
            subsystem_id: int,
    ):
        async with cron_context.pg_manager.primary_connect() as conn:
            add_role = role_models.AddRole(
                slug=role_slug,
                fields=None,
                name=common_models.Translatable('ru', 'en'),
                help=common_models.Translatable('ru', 'en'),
                external_ref_slug=external_slug,
                ref_type=ref_type,
                visible=True,
                subsystem_id=subsystem_id,
            )
            role = await cron_context.pg_manager.roles.add_role(conn, add_role)
            return role

    return _request


async def test_sync_roles(cron_context, cron_runner, add_subsystem, add_role):
    subsystem_id = await add_subsystem('internal')
    for exist in EXISTED:
        await add_role(
            exist['slug'],
            exist['external_slug'],
            common_models.ExternalRefType(exist['ref_type']),
            subsystem_id=subsystem_id,
        )

    await cron_runner.sync_roles()
    async with cron_context.pg_manager.primary_connect() as conn:
        roles = await cron_context.pg_manager.roles.fetch_all(conn)
    roles_to_compare = [
        {
            'slug': role.slug,
            'external_slug': role.external_ref_slug,
            'ref_type': role.ref_type.value,
        }
        for role in roles
    ]
    sort_key = operator.itemgetter('slug', 'external_slug', 'ref_type')
    assert sorted(roles_to_compare, key=sort_key) == sorted(
        EXPECTED + EXISTED, key=sort_key,
    )
