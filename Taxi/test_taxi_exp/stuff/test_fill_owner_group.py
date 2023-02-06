import pytest

from taxi_exp import settings
from taxi_exp.generated.cron import run_cron as cron_run
from test_taxi_exp import helpers
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXP_NAME = 'test'


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_send_alert(
        taxi_exp_client, patch_aiohttp_session, response_mock,
):
    @patch_aiohttp_session(f'{settings.STAFF_API_URL}/v3/persons')
    def _email_from_staff(*args, **kwargs):
        assert 'params' in kwargs
        assert 'login' in kwargs['params']
        logins = kwargs['params']['login'].split(',')
        return response_mock(
            json={
                'page': 1,
                'pages': 1,
                'result': [
                    {
                        'department_group': {'id': 1},
                        'login': login,
                        'id': index,
                    }
                    for index, login in enumerate(logins)
                ],
            },
        )

    # running cron
    test_exp = experiment.generate(name=EXP_NAME, owners=['person'])
    await helpers.init_exp(taxi_exp_client, body=test_exp)
    await cron_run.main(['taxi_exp.stuff.fill_owner_group', '-t', '0'])
    response = await db.get_owner_group(
        taxi_exp_client.app,
        owner='person',
        exp_name=EXP_NAME,
        namespace=helpers.DEFAULT_NAMESPACE,
    )
    assert response[0]['owner_group'] == 1
