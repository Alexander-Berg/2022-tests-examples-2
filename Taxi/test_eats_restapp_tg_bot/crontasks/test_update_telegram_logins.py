import pytest

from eats_restapp_tg_bot.generated.cron import run_cron


@pytest.mark.parametrize('testcase', ['ids', 'logins'])
@pytest.mark.pgsql('eats_restapp_tg_bot', files=['logins.sql'])
async def test_should_update_personal_logins(
        pgsql, mock_personal, load_json, testcase,
):
    @mock_personal('/v2/telegram_logins/bulk_store')
    async def _login_mock(request):
        return load_json('personal.json')[testcase]['logins']

    @mock_personal('/v2/telegram_ids/bulk_store')
    async def _id_mock(request):
        return load_json('personal.json')[testcase]['ids']

    await run_cron.main(
        ['eats_restapp_tg_bot.crontasks.update_telegram_logins', '-t', '0'],
    )

    assert get_logins(pgsql) == load_json('expected.json')[testcase]


def get_logins(pgsql):
    with pgsql['eats_restapp_tg_bot'].dict_cursor() as cursor:
        cursor.execute(
            'SELECT login,personal_login,personal_user_id,user_id FROM logins',
        )
        return [row.copy() for row in cursor]
