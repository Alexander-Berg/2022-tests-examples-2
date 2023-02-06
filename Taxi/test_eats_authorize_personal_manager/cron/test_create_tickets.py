import pytest

from eats_authorize_personal_manager.generated.cron import run_cron


CRON_SETTINGS = [
    'eats_authorize_personal_manager.crontasks.create_issues_with_startrek',
    '-t',
    '0',
]


@pytest.mark.pgsql(
    'eats_authorize_personal_manager', files=['add_admin_line_info.sql'],
)
@pytest.mark.config(
    EATS_AUTHORIZE_PERSONAL_MANAGER_SETTINGS={
        'logins_limit': 3,
        'startrek_settings': {'queue': 'queue', 'ticket_type': 'task'},
    },
)
@pytest.mark.config(
    EATS_AUTHORIZE_PERSONAL_MANAGER_CRON_CREATE_ISSUE_ENABLE=True,
)
async def test_create_tickets(patch, pgsql):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def create_ticket(**kwargs):  # pylint: disable=unused-variable
        return {'key': 'EDAMANAGER-1'}

    await _check_data(pgsql, False)
    await run_cron.main(CRON_SETTINGS)
    await _check_data(pgsql, True)


async def _check_data(pgsql, expected_status):
    with pgsql['eats_authorize_personal_manager'].dict_cursor() as cursor:
        cursor.execute('SELECT * FROM line_bind_place')
        actual_data = [row for row in cursor]
    for i in actual_data:
        assert i['has_ticket'] is expected_status


@pytest.mark.pgsql(
    'eats_authorize_personal_manager',
    files=['add_admin_line_info_all_true.sql'],
)
@pytest.mark.config(
    EATS_AUTHORIZE_PERSONAL_MANAGER_CRON_CREATE_ISSUE_ENABLE=True,
)
async def test_not_create_tickets(patch, pgsql):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_ticket')
    async def create_ticket(**kwargs):  # pylint: disable=unused-variable
        return {'key': 'EDAMANAGER-1'}

    await _check_data(pgsql, True)
    await run_cron.main(CRON_SETTINGS)
    assert not create_ticket.call
