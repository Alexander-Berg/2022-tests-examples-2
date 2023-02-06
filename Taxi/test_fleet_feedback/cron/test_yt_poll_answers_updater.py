import pytest

from fleet_feedback.generated.cron import cron_context as context_module
from fleet_feedback.generated.cron import run_cron


@pytest.mark.config(
    FLEET_FEEDBACK_CRON_YT_POLL_ANSWER_UPDATER={'is_enabled': True},
)
@pytest.mark.pgsql(
    'fleet_feedback', files=['simple_poll.sql', 'simple_poll_answer.sql'],
)
async def test_success(cron_context: context_module.Context, patch):
    @patch('taxi.yt_wrapper.YtClient.create')
    def _create(*args, **kwargs):
        return '1234-4321-2345-5432'

    @patch('taxi.yt_wrapper.YtClient.exists')
    def _exists(*args, **kwargs):
        return False

    @patch('taxi.yt_wrapper.YtClient.write_table')
    def _write_table(*args, **kwargs):
        return

    assert await get_uploaded_count(cron_context) == 0

    await run_cron.main(
        ['fleet_feedback.crontasks.yt_poll_answers_updater', '-t', '0'],
    )

    assert await get_uploaded_count(cron_context) == 1


async def get_uploaded_count(cron_context: context_module.Context) -> int:
    return await cron_context.pg.main_master.fetchval(
        'SELECT COUNT(id) FROM fleet_feedback.poll_answers where yt_status = 1;',  # noqa
    )
