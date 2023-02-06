from typing import Optional

import pytest

from scripts.lib.models import async_check_queue as acq_models
from scripts.lib.repositories import async_check_queue as acq_repo


@pytest.fixture
def insert_many_acq_tasks(db):
    async def _wrapper(*items: acq_models.QueueItem):
        await acq_repo.insert_many(db.scripts_async_checks_queue, list(items))

    return _wrapper


@pytest.fixture
def get_acq_task(db):
    async def _wrapper(script_id: str) -> Optional[acq_models.QueueItem]:
        return await acq_repo.find_one(
            db.scripts_async_checks_queue, script_id,
        )

    return _wrapper
