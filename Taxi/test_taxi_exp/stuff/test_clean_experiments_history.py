import pytest

from taxi_exp.generated.cron import run_cron as cron_run
from test_taxi_exp.helpers import db
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'default_experiment'
UPDATE_COUNT = 10
REPLICATION_RULE_NAME = 'taxi_exp_history'


@pytest.mark.usefixtures('simple_secdist')
@pytest.mark.config(
    EXP_EXPERIMENTS_HISTORY_CLEAN={'disabled': False, 'table_size': 1},
)
@pytest.mark.config(TVM_RULES=[{'dst': 'replication', 'src': 'taxi_exp'}])
@pytest.mark.pgsql('taxi_exp', files=['default.sql'])
async def test_clean_experiments_history(taxi_exp_client, mockserver):
    @mockserver.json_handler(
        f'/replication/v2/state/get/{REPLICATION_RULE_NAME}',
    )
    def _last_replicated_rev(request):
        assert REPLICATION_RULE_NAME in request.url
        return {
            'replication_settings': {'field': 'rev', 'type': 'int'},
            'queue_states': {'state': {'last_replicated': str(UPDATE_COUNT)}},
            'target_state': {'last_replicated': str(UPDATE_COUNT)},
        }

    # fill experiment history
    exp_body = experiment.generate_default()
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME},
        json=exp_body,
    )
    assert response.status == 200
    rev = 1
    for _ in range(UPDATE_COUNT - 1):
        response = await taxi_exp_client.put(
            '/v1/experiments/',
            headers={'YaTaxi-Api-Key': 'secret'},
            params={'name': EXPERIMENT_NAME, 'last_modified_at': rev},
            json=exp_body,
        )
        rev += 1
        assert response.status == 200

    count_before = len(await db.get_experiments_history(taxi_exp_client.app))
    # running cron for clean experiments history
    await cron_run.main(
        ['taxi_exp.stuff.clean_experiments_history', '-t', '0'],
    )
    count_after = len(await db.get_experiments_history(taxi_exp_client.app))

    assert count_before == UPDATE_COUNT and count_after == 1
