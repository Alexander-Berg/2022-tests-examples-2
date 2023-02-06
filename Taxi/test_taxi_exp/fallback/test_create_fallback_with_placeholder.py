import pytest

from taxi_exp.util import pg_helpers
from taxi_exp.util import predicate_helpers
from test_taxi_exp.helpers import experiment

EXPERIMENT_NAME = 'experiment_with_fallback'


def _clean_and_get_rev(experiment_body):
    predicate_helpers.remove_ql(experiment_body)
    experiment_body.pop('closed', None)
    experiment_body.pop('name', None)
    experiment_body.pop('removed', None)
    experiment_body.pop('owners', None)
    rev = experiment_body.pop('last_modified_at')
    return experiment_body, rev


async def _count_fallbacks(app):
    query = 'SELECT COUNT(*) as count FROM clients_schema.fallbacks;'
    result = await pg_helpers.fetchrow(app['pool'], query)
    return result['count']


@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_create_fallback_with_placeholder(taxi_exp_client):
    experiment_body = experiment.generate_default(
        fallback=experiment.make_fallback(
            short_description='Short description',
            what_happens_when_turn_off='Blackout',
            need_turn_off=True,
            placeholder='https://wiki.yandex-team.ru/smth',
        ),
    )
    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME + '1'},
        json=experiment_body,
    )
    assert response.status == 200

    experiment_body = experiment.generate_default(
        fallback=experiment.make_fallback(
            short_description='Short description',
            what_happens_when_turn_off='Blackout',
            need_turn_off=True,
            placeholder='https://wiki.team.ru/smth-other',
        ),
    )
    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': EXPERIMENT_NAME + '2'},
        json=experiment_body,
    )
    assert response.status == 400
