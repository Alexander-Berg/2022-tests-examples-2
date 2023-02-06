import pytest

from crm_admin.generated.cron import run_cron
from crm_admin.storage import dict_ticket_status

CRM_ADMIN_SETTINGS = {
    'StartrekSettings': {
        'campaign_queue': 'CRMTEST',
        'target_statuses': ['target_status'],
        'unapproved_statuses': ['target_status'],
        'creative_queue': ['CRMTEST'],
        'idea_approved_statuses': ['target_status'],
    },
}


@pytest.mark.config(CRM_ADMIN_SETTINGS=CRM_ADMIN_SETTINGS)
async def test_success(cron_context, patch, load_json):
    @patch('taxi.clients.startrack.StartrackAPIClient._request')
    async def _(**kwargs):
        if kwargs['params']['language'] == 'en':
            ret = load_json('startrek_ru.json')
        else:
            ret = load_json('startrek_en.json')
        return ret

    await run_cron.main(['crm_admin.crontasks.ticket_states', '-t', '0'])

    dts = dict_ticket_status.DbDictTicketStatus(cron_context)
    expected_keys = ('open', 'inProgress', 'agreed', 'closed')

    rows = await dts.fetch_by_lang('ru')
    expected = ('Открыт', 'В работе', 'Одобрено', 'Закрыт')
    i = 0
    for row in rows:
        assert row['st_key'] == expected_keys[i]
        assert row['st_value'] == expected[i]
        assert row['pos'] == i + 1
        i += 1

    rows = await dts.fetch_by_lang('en')
    expected = ('Open', 'In Progress', 'Agreed', 'Closed')
    i = 0
    for row in rows:
        assert row['st_key'] == expected_keys[i]
        assert row['st_value'] == expected[i]
        assert row['pos'] == i + 1
        i += 1
