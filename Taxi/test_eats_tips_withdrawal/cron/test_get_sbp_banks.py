from aiohttp import web
import pytest

from eats_tips_withdrawal.generated.cron import run_cron


@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
@pytest.mark.now('1970-01-01 00:00:16')
async def test_get_sbp_banks(mock_best2pay, pgsql):
    @mock_best2pay('/webapi/b2puser/GetSBPBankList')
    async def _mock_get_bsp_list(request):
        assert (
            request.query['signature']
            == 'ZjA1ZjBjZjhlYTM3YWExNGQ1NDQzNTcyMWEwY2M3NzA='
        )
        return web.Response(
            body="""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                <GetSBPBankList>
                    <nonce>17</nonce>
                    <dataList>
                        <row>
                            <id>100000000001</id>
                            <title>Газпромбанк</title>
                            <latinTitle>Gazprombank</latinTitle>
                        </row>
                        <row>
                            <id>100000000002</id>
                            <title>РНКО Платежный центр</title>
                            <latinTitle>RNKO Payment Center</latinTitle>
                        </row>
                    </dataList>
                </GetSBPBankList>""",
            headers={'content-type': 'application/xml'},
            status=200,
        )

    await run_cron.main(
        ['eats_tips_withdrawal.crontasks.get_sbp_banks', '-t', '0'],
    )

    cursor = pgsql['eats_tips_withdrawal'].cursor()
    cursor.execute('select * from eats_tips_withdrawal.sbp_banks')
    rows = cursor.fetchall()
    assert [
        (
            '100000000001',
            'Газпромбанк',
            'Gazprombank',
            True,
            'http://bank.image.ru',
        ),
        (
            '100000000002',
            'РНКО Платежный центр',
            'RNKO Payment Center',
            False,
            None,
        ),
    ] == rows


@pytest.mark.pgsql('eats_tips_withdrawal', files=['pg.sql'])
async def test_get_sbp_banks_b2p_internal_error(mock_best2pay):
    @mock_best2pay('/webapi/b2puser/GetSBPBankList')
    async def _mock_get_bsp_list(request):
        return web.Response(
            body="""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
                    <error>
                        <description>Internal error</description>
                        <code>130</code>
                    </error>""",
            headers={'content-type': 'application/xml'},
            status=200,
        )

    with pytest.raises(
            RuntimeError, match=f'B2P error, code 130 error Internal error',
    ):
        await run_cron.main(
            ['eats_tips_withdrawal.crontasks.get_sbp_banks', '-t', '0'],
        )
