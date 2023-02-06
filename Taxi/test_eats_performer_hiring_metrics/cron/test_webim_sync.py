# pylint: disable=redefined-outer-name
import datetime
import typing

import dateutil.parser
import pytest

from eats_performer_hiring_metrics.common import db
from eats_performer_hiring_metrics.crontasks import webim_sync
from eats_performer_hiring_metrics.generated.cron import (
    cron_context as context_module,
)
from eats_performer_hiring_metrics.generated.cron import run_cron


@pytest.fixture
def mock_webim_chats(mock_eats_performer_hiring_webim):
    def specific_webim_chats_mock(
            webim_responses: typing.Dict[typing.Union[int, str], dict],
    ) -> None:
        @mock_eats_performer_hiring_webim('/api/v2/chats')
        def _chats(request) -> dict:
            assert (
                request.headers['Authorization']
                == 'Basic dGVzdGxvZ2luOnRlc3RwYXNz'
            )
            return webim_responses[request.query['since']]

    return specific_webim_chats_mock


@pytest.fixture
async def create_init_cursor(cron_context: context_module.Context) -> None:
    await db.insert_webim_sync_cursor(cron_context.pg, 'init')


@pytest.mark.parametrize(
    ('data_path',),
    [
        ('chats_ok_noop.json',),
        ('chats_ok_create_string__chat_id__last_ts.json',),
        ('chats_ok_create_integer__chat_id__last_ts.json',),
        ('chats_ok_update.json',),
        ('chats_ok_4_pages.json',),
        ('chats_ok_no_operator_response.json',),
        ('chats_ok_no_state_history.json',),
        ('chats_ok_state_no_department_id.json',),
    ],
)
@pytest.mark.config(
    EATS_PERFORMER_HIRING_METRICS_WEBIM_DEPARTMENT_IDS=[42],
    EATS_PERFORMER_HIRING_METRICS_WEBIM_SYNC_PAGES_PER_RUN=3,
)
@pytest.mark.now('2022-02-01T12:00:00Z')
async def test_webim_sync(
        data_path,
        cron_context: context_module.Context,
        load_json,
        create_init_cursor,
        mock_webim_chats,
):
    data = load_json(data_path)
    mock_webim_chats(data['responses'])

    await run_cron.main(
        ['eats_performer_hiring_metrics.crontasks.webim_sync', '-t', '0'],
    )

    async with cron_context.pg.master_pool.acquire() as conn:
        chats_result = sorted(
            (
                dict(**raw_chat)
                for raw_chat in (
                    await conn.fetch(
                        """
                            SELECT
                                id,
                                created_at,
                                updated_at,
                                operator_response_time
                            FROM
                                webim_chats
                        """,
                    )
                )
            ),
            key=lambda chat: str(chat['id']),
        )
        chats_expected = sorted(
            data['expected']['chats'], key=lambda chat: str(chat['id']),
        )
        assert len(chats_expected) == len(chats_result)
        for expected, result in zip(chats_expected, chats_result):
            assert str(expected['id']) == result['id']
            assert (
                expected['operator_response_time']
                == result['operator_response_time']
            )
            assert dateutil.parser.isoparse(expected['created_at']).astimezone(
                datetime.timezone.utc,
            ) == result['created_at'].astimezone(datetime.timezone.utc)
            assert dateutil.parser.isoparse(expected['updated_at']).astimezone(
                datetime.timezone.utc,
            ) == result['updated_at'].astimezone(datetime.timezone.utc)

    assert str(data['expected']['cursor']) == await db.get_webim_sync_cursor(
        cron_context.pg,
    )


async def test_webim_sync_error(
        cron_context: context_module.Context,
        create_init_cursor,
        mock_webim_chats,
):
    mock_webim_chats(dict(init=dict(error='unknown')))
    with pytest.raises(webim_sync.WebimSyncError):
        await run_cron.main(
            ['eats_performer_hiring_metrics.crontasks.webim_sync', '-t', '0'],
        )


@pytest.mark.config(
    EATS_PERFORMER_HIRING_METRICS_WEBIM_DEFAULT_CURSOR_DELTA=60,
)
async def test_webim_sync_default_cursor(
        cron_context: context_module.Context, patch, mock_webim_chats,
):
    @patch('time.time_ns')
    def _() -> int:
        return 300 * 10 ** 9

    expected_cursor_value = str((300 - 60) * 10 ** 6)
    mock_webim_chats(
        {
            expected_cursor_value: {
                'chats': [],
                'last_ts': 'end',
                'more_chats_available': False,
            },
        },
    )

    await run_cron.main(
        ['eats_performer_hiring_metrics.crontasks.webim_sync', '-t', '0'],
    )
