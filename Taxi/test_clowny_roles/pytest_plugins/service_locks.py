from typing import List

import pytest

from clowny_roles.internal.models import service_lock as lock_models


@pytest.fixture
def service_lock_acquire(web_context):
    async def _wrapper(lock) -> bool:
        return await web_context.pg_manager.service_lock.acquire(
            web_context.pg.primary, lock,
        )

    return _wrapper


@pytest.fixture
def service_lock_release(web_context):
    async def _wrapper(lock: lock_models.ServiceLock) -> None:
        await web_context.pg_manager.service_lock.release(
            web_context.pg.primary, lock,
        )

    return _wrapper


@pytest.fixture
def service_lock_fetch_all(web_context):
    async def _wrapper() -> List[lock_models.ServiceLock]:
        return await web_context.pg_manager.service_lock.fetch_all(
            web_context.pg.primary,
        )

    return _wrapper
