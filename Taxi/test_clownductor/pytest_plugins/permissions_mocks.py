import pytest


@pytest.fixture
def add_grant(web_context):
    async def _wrapper(
            login: str,
            role: str,
            service_id=None,
            project_id=None,
            is_super=False,
    ):
        await web_context.pg.primary.execute(
            """
            INSERT INTO permissions.roles
                (login, role, service_id, project_id, is_super)
            VALUES ($1, $2, $3, $4, $5)
            """,
            login,
            role,
            service_id,
            project_id,
            is_super,
        )

    return _wrapper
