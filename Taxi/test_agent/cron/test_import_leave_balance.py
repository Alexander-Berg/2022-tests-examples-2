from aiohttp import web
import pytest

from agent.generated.cron import run_cron


OK_RESPONSE = """<ROWSET><ROW>
<PERSON_GUID>abeb11542dbaee44bf7753d5ddf41100</PERSON_GUID>
<LEAVE_BALANCE>-2.01</LEAVE_BALANCE>
<TIME_OFF>0</TIME_OFF>
<TIME_OFF_WORK_IN_HOLIDAY>0</TIME_OFF_WORK_IN_HOLIDAY>
<TIME_OFF_OVERTIME/>
<LEAVE_BALANCES>
<LEAVE_BALANCE_DEFAULT>-2.01</LEAVE_BALANCE_DEFAULT>
<LEAVE_BALANCE_COMPANY>0</LEAVE_BALANCE_COMPANY>
</LEAVE_BALANCES>
</ROW>
<ROW>
<PERSON_GUID>86b4253c71f04848a614b7ea57000116</PERSON_GUID>
<LEAVE_BALANCE>9.32</LEAVE_BALANCE>
<TIME_OFF>0</TIME_OFF>
<TIME_OFF_WORK_IN_HOLIDAY>0</TIME_OFF_WORK_IN_HOLIDAY>
<TIME_OFF_OVERTIME/>
<LEAVE_BALANCES>
<LEAVE_BALANCE_DEFAULT>9.32</LEAVE_BALANCE_DEFAULT>
<LEAVE_BALANCE_COMPANY>0</LEAVE_BALANCE_COMPANY>
</LEAVE_BALANCES>
</ROW>
</ROWSET>"""


FAIL_RESPONSE = ''


@pytest.mark.parametrize(
    'response,expected_db',
    [
        (
            OK_RESPONSE,
            [
                {
                    'guid': 'abeb11542dbaee44bf7753d5ddf41100',
                    'leave_balance': -2,
                },
                {
                    'guid': '86b4253c71f04848a614b7ea57000116',
                    'leave_balance': 9,
                },
            ],
        ),
        (
            FAIL_RESPONSE,
            [
                {
                    'guid': 'abeb11542dbaee44bf7753d5ddf41100',
                    'leave_balance': None,
                },
                {
                    'guid': '86b4253c71f04848a614b7ea57000116',
                    'leave_balance': None,
                },
            ],
        ),
    ],
)
async def test_import_leave_balance(
        cron_context, mock_oebs, response, expected_db,
):
    @mock_oebs('/rest/leaveBalance', prefix=True)
    def handler(request):  # pylint: disable=unused-variable
        return web.Response(content_type='application/xml', text=response)

    await run_cron.main(['agent.crontasks.import_leave_balance', '-t', '0'])

    query = 'SELECT guid,leave_balance FROM agent.users'
    async with cron_context.pg.slave_pool.acquire() as conn:
        result = [dict(row) for row in await conn.fetch(query)]

        assert expected_db == result
