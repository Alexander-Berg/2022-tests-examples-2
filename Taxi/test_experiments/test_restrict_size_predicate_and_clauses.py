import pytest

from test_taxi_exp.helpers import experiment


@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
@pytest.mark.config(EXP_SIZE_PREDICATE_AND_CLAUSES_RESTRICTION=1)
async def test_restrict_size_predicate_and_clauses(taxi_exp_client):
    exp_body = experiment.generate('1')

    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': '1'},
        json=exp_body,
    )
    assert response.status == 400
    body = await response.json()
    assert body['code'] == 'SIZE_PREDICATE_OR_CLAUSES_TOO_BIG'
