import json
from typing import List
from typing import Optional
from typing import Tuple

import pytest

from clowny_roles.internal.models import common
from clowny_roles.internal.models import role as role_models
from clowny_roles.internal.models import subsystem as subsystem_models
from clowny_roles.internal.repositories import role as role_repo
from clowny_roles.internal.repositories import subsystem


ADD_ROLE_QUERY = """
    INSERT INTO
        roles.roles (
            slug,
            name,
            help,
            external_ref_slug,
            ref_type,
            visible,
            subsystem_id,
            fields
        )
    VALUES
        ($1, ($2, $3), ($4, $5), $6, $7, $8, $9, $10)
    RETURNING
        id
    ;
"""


@pytest.fixture(name='add_subsystem')
def _add_subsystem(web_context):
    async def _do_it(slug: str) -> int:
        en_name = ru_name = slug
        item = await subsystem.Repository(web_context).upsert_one(
            web_context.pg.primary,
            slug,
            common.Translatable(en=en_name, ru=ru_name),
        )
        return item.db_meta.id

    return _do_it


@pytest.fixture(name='get_subsystem')
def _get_subsystem(web_context):
    async def _do_it(slug: str) -> subsystem_models.Subsystem:
        result = await web_context.pg_manager.subsystems.find_one(
            conn=web_context.pg.secondary, slug=slug,
        )
        assert result
        return result

    return _do_it


@pytest.fixture(name='add_role')
def _add_role(web_context):
    async def _do_it(
            slug: str,
            external_ref_slug: str,
            scope_node_type: str,
            subsystem_id: int,
            name: Optional[Tuple[str, str]] = None,
            help_: Optional[Tuple[str, str]] = None,
            fields: Optional[List[dict]] = None,
            visible: bool = True,
    ):
        _double_slug = (slug, slug)
        en_name, ru_name = name if name else _double_slug
        en_help, ru_help = help_ if help_ else _double_slug
        record = await web_context.pg.primary.fetchrow(
            ADD_ROLE_QUERY,
            slug,
            en_name,
            ru_name,
            en_help,
            ru_help,
            external_ref_slug,
            scope_node_type,
            visible,
            subsystem_id,
            json.dumps(fields) if fields is not None else None,
        )
        return record['id']

    return _do_it


@pytest.fixture(name='add_abc_scope')
def _add_abc_scope(web_context):
    async def _do_it(
            slug: str,
            name: Optional[Tuple[str, str]] = None,
            help_: Optional[Tuple[str, str]] = None,
    ) -> str:
        _double_slug = (slug, slug)
        en_name, ru_name = name if name else _double_slug
        en_help, ru_help = help_ if help_ else _double_slug
        record = await web_context.pg.primary.fetchrow(
            """
            INSERT INTO roles.abc_scopes(slug, name, help)
            VALUES ($1, ($2, $3), ($4, $5))
            RETURNING slug
            """,
            slug,
            en_name,
            ru_name,
            en_help,
            ru_help,
        )
        return record['slug']

    return _do_it


@pytest.fixture(name='delete_abc_scope')
def _delete_abc_scope(web_context):
    async def _do_it(slug: str, soft=True):
        query_part = (
            'UPDATE roles.abc_scopes SET is_deleted = TRUE'
            if soft
            else 'DELETE FROM roles.abc_scopes'
        )
        await web_context.pg.primary.execute(
            f'{query_part} WHERE slug = $1', slug,
        )

    return _do_it


@pytest.fixture(name='get_roles')
def _get_roles(web_context):
    async def _do_it(
            external_ref_slug: Optional[str] = None,
            ref_type: Optional[str] = None,
    ) -> List[role_models.Role]:
        filters = None
        if external_ref_slug and ref_type:
            filters = role_repo.FetchManyFilter(
                external_ref_slug=external_ref_slug,
                ref_type=common.ExternalRefType(ref_type),
            )
        return await web_context.pg_manager.roles.fetch_all(
            conn=web_context.pg.secondary, fetch_many_filter=filters,
        )

    return _do_it


@pytest.fixture(name='get_role')
def _get_role(web_context):
    async def _do_it(slug: str, scope: str, ref_slug: str) -> role_models.Role:
        role = await web_context.pg_manager.roles.find_one(
            conn=web_context.pg.secondary,
            slug=slug,
            scope=common.ExternalRefType(scope),
            ref_slug=ref_slug,
            subsystem=None,
        )
        assert role
        return role

    return _do_it
