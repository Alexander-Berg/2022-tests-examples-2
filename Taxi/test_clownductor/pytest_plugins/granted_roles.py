import pytest

from clownductor.internal.utils import postgres


@pytest.fixture
def add_granted_roles(web_context):
    async def _wrapper(
            service_id: int, idm_id: int, process_name: str = 'duty_roots',
    ):
        await web_context.service_manager.permissions.add_granted_roles(
            service_id=service_id,
            process_name=process_name,
            idm_ids=[idm_id],
            conn=None,
        )

    return _wrapper


@pytest.fixture
def get_last_granted_roles_idm_id(web_context):
    async def _wrapper() -> int:
        async with postgres.get_connection(web_context) as conn:
            row = await conn.fetchrow(
                'SELECT max(idm_id) as max_id FROM permissions.granted_roles;',
            )
        return row['max_id'] if row else 0

    return _wrapper
