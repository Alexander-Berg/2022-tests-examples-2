import pytest

from crm_admin.generated.cron import run_monrun


CRM_ADMIN_MONRUN = {
    'Limits': {
        'campaign_sending_processing_limit_in_seconds': 600,
        'campaign_segment_calculating_limit_in_seconds': 600,
    },
    'DuplicatesCommunications': {
        'enabled': True,
        'path': '//home/logfeller/logs/taxi-crm-hub-experiments/stream/5min',
    },
}


@pytest.mark.now('2022-04-07 12:00:00')
@pytest.mark.config(CRM_ADMIN_MONRUN=CRM_ADMIN_MONRUN)
@pytest.mark.parametrize(
    'file', ['without_duplicates.json', 'with_duplicates.json'],
)
async def test_check_duplicates_communications(patch, load_json, file):
    params = load_json(file)

    @patch('client_chyt.components.AsyncChytClient.execute')
    async def execute(query):
        assert query == params['query_text']
        return params['query_result']

    msg = await run_monrun.run(
        [
            'crm_admin.monrun_checks.check_duplicates_communications',
            'duplicates_communications',
        ],
    )

    assert execute.calls

    assert msg == params['message']
