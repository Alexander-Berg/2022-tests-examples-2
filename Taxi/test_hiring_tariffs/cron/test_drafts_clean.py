# pylint: disable=redefined-outer-name
import pytest

from hiring_tariffs.generated.cron import run_cron


@pytest.mark.config(
    HIRING_TARIFFS_DRAFT_TIMEOUT=0, HIRING_TARIFFS_DRAFT_TIMEOUT_LIMIT=2,
)
async def test_drafts_clean(load_json, create_draft):
    await create_draft(load_json('draft.json'))
    await create_draft(load_json('draft.json'))
    await create_draft(load_json('draft.json'))

    await run_cron.main(['hiring_tariffs.crontasks.drafts_clean', '-t', '0'])
