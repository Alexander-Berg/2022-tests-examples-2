from typing import Optional

import pytest

from clowny_alert_manager.internal.models import config_queue


@pytest.fixture
def add_config_in_queue(web_context):
    async def _wrapper(
            branch_id: int, data: dict, status: str, job_id: Optional[int],
    ):
        config_queue.BareConfig.parse_raw(data)
        _status = config_queue.ConfigStatus(status)
        cfg = config_queue.BareConfig(branch_id, data, _status, job_id)
        db_cfg = await config_queue.Repository.upsert(
            web_context, web_context.pg.primary, model=cfg,
        )
        await config_queue.Repository.update_one(
            web_context,
            web_context.pg.primary,
            config_id=db_cfg.id,
            status=_status.value,
            job_id=job_id,
        )
        return await config_queue.Repository.fetch_one(
            web_context, web_context.pg.primary, id=db_cfg.id,
        )

    return _wrapper
