import datetime

import pytest

from taxi_approvals.generated.cron import run_cron


REMINDED_QUERY = """
    select
        id,
        reminded
    from
        approvals_schema.drafts
    where
        id = 5;
"""


@pytest.mark.pgsql('approvals', files=['default.sql'])
@pytest.mark.now('2017-11-01T03:00:00')
async def test_check_reminders(approvals_cron_app, mockserver):

    was_called = False
    # pylint: disable=unused-variable
    @mockserver.json_handler('/startrack_reports/v2/create_comments/')
    async def patch_reports_comments(request):
        nonlocal was_called
        was_called = True
        data = request.json
        assert request.headers.get('Accept-Language') == 'ru'

        summonees = None
        hours = None
        created = None
        draft_id = data['template_kwargs']['draft_id']
        if draft_id == 5:
            summonees = ['test_login1', 'test_login2']
            hours = 3
            created = '2016-11-01T04:10:00+0300'

        assert data == {
            'action': 'drafts:reminder',
            'data': {},
            'audit_action_id': '',
            'tickets': [{'key': 'TAXIRATE-35', 'summonees': summonees}],
            'template_kwargs': {
                'created': created,
                'login': 'test_user',
                'draft_id': draft_id,
                'url': (
                    'https://tariff-editor.taxi.yandex-team.ru'
                    f'/test_service/test_api/{draft_id}'
                ),
                'hours': hours,
                'time': '2017-11-01T03:00:00Z',
            },
        }

    await run_cron.main(['taxi_approvals.stuff.check_reminders', '-t', '0'])
    assert was_called
    pool = approvals_cron_app['pool']
    async with pool.acquire() as connection:
        result = await connection.fetch(REMINDED_QUERY)
        assert len(result) == 1
        for row in result:
            assert row['reminded'] == datetime.datetime.now()
