# pylint: disable=redefined-outer-name
import datetime

import pytest
import pytz

from document_templator.generated.api import web_context
from document_templator.generated.cron import run_cron


@pytest.mark.config(
    DOCUMENT_TEMPLATOR_CRON_MARK_DOCUMENTS_OUTDATED={'enabled': True},
)
@pytest.mark.parametrize(
    'persistent_id, expected_count',
    (
        pytest.param(
            '000009999988888777771111',
            1,
            id='update_schedule_is_daily_and_time_is_01:01',
            marks=pytest.mark.now('2021-01-01T01:01:00+03:00'),
        ),
        pytest.param(
            '000009999988888777771111',
            0,
            id='update_schedule_is_daily_and_time_is_02:01',
            marks=pytest.mark.now('2021-01-01T02:01:00+03:00'),
        ),
        pytest.param(
            '000009999988888777771111',
            0,
            id='update_schedule_is_daily_and_time_is_01:01_and_not_friday',
            marks=pytest.mark.now('2021-01-02T01:01:00+03:00'),
        ),
        pytest.param(
            '000009999988888777772222', 0, id='update_schedule_is_never',
        ),
    ),
)
async def test_mark_documents_as_outdated(persistent_id, expected_count):
    now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    context = web_context.Context()
    await context.on_startup()
    query = """
        SELECT count(*)
        FROM document_templator.dynamic_documents
        WHERE
            persistent_id = $1
            AND NOT removed
            AND outdated_at = $2;
    """

    count = await context.pg.master.fetchval(query, persistent_id, now)
    assert count == 0
    await run_cron.main(
        ['document_templator.crontasks.mark_documents_outdated', '-t', '0'],
    )
    count = await context.pg.master.fetchval(query, persistent_id, now)
    assert count == expected_count


@pytest.mark.config(
    DOCUMENT_TEMPLATOR_CRON_MARK_DOCUMENTS_OUTDATED={'enabled': False},
)
async def test_mark_documents_as_outdated_with_not_enabled():
    query = """
        SELECT count(*)
        FROM document_templator.dynamic_documents
        WHERE
            persistent_id = $1
            AND NOT removed
            AND outdated_at IS NOT NULL;
    """
    context = web_context.Context()
    await context.on_startup()
    count = await context.pg.master.fetchval(query, '000009999988888777773333')
    assert count == 0
    await run_cron.main(
        ['document_templator.crontasks.mark_documents_outdated', '-t', '0'],
    )

    count = await context.pg.master.fetchval(query, '000009999988888777773333')
    assert count == 0
