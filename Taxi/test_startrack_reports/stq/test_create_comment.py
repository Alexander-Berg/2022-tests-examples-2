import datetime

from aiohttp import web
import pytest

from startrack_reports.db import queries
from startrack_reports.stq import create_comment as create_comment_stq


@pytest.mark.parametrize(
    'comment_pk,expected',
    [
        (
            1,
            '\n'
            '<{Changelist\n'
            '#|\n'
            '|| data key | current value | new value ||\n'
            '|| Включена | yes | no ||\n'
            '|#}>',
        ),
        (
            2,
            '\n'
            '<{Changelist\n'
            '#|\n'
            '|| data key |  | new value ||\n'
            '|| series |  | testalx0 ||\n'
            '|| status |  |  ||\n'
            '||  | ok | 200 ||\n'
            '|#}>',
        ),
        pytest.param(3, '', id='data key is not in database'),
    ],
)
@pytest.mark.translations(
    startrack_reports={
        'drafts.commissions_create.enabled': {
            'ru': 'Включена',
            'en': 'Enabled',
        },
    },
)
@pytest.mark.pgsql(
    'startrack_reports',
    files=[
        'startrack_reports_comments.sql',
        'startrack_reports_commissions.sql',
    ],
)
async def test_task(stq3_context, patch, mock_audit, comment_pk, expected):
    # pylint: disable=unused-variable
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(*args, **kwargs):
        assert kwargs['text'] == expected
        return {}

    @mock_audit('/v1/robot/logs/retrieve/')
    async def handler(request):
        return web.json_response(
            [
                {
                    'action': 'addcuponseries',
                    'arguments': {'series': 'testalx0', 'status': {'ok': 200}},
                    'login': 'alexsandr',
                    'timestamp': datetime.datetime(
                        2015, 6, 29, 12, 4, 38, 794000,
                    ).strftime('%c'),
                },
            ],
        )

    comment_record = await queries.get_comment_by_pk(stq3_context, comment_pk)
    assert comment_record['created'] is False

    await create_comment_stq.task(stq3_context, comment_pk)

    comment_record = await queries.get_comment_by_pk(stq3_context, comment_pk)
    assert comment_record['created'] is True
