import pytest


from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files


NAME = 'experiment_for_restore'
FILE_CONTENT = (
    b'5ab66ff9cab04dfcb778147be85f1297\n' b'e2ed1c509f8f47eb82cb2d7fc42a6ee2\n'
)


@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
async def test_fail_restore_by_history_from_config(taxi_exp_client):
    # upload file
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', FILE_CONTENT, file_type='string',
    )
    assert response.status == 200
    file_id = (await response.json())['id']

    # create another experiment
    body = experiment.generate(
        consumers=[{'name': 'test_consumer'}],
        match_predicate=experiment.infile_predicate(file_id),
        default_value={},
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME + 'another'},
        json=body,
    )
    assert response.status == 200

    # create config
    body = experiment.generate(
        consumers=[{'name': 'test_consumer'}],
        match_predicate=experiment.DEFAULT_PREDICATE,
        default_value={},
        clauses=[
            experiment.make_clause(
                'first', predicate=experiment.infile_predicate(file_id),
            ),
        ],
    )
    body['match'].pop('applications', None)
    response = await taxi_exp_client.post(
        '/v1/configs/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == 200

    # create experiment
    body = experiment.generate(
        consumers=[{'name': 'test_consumer'}],
        match_predicate=experiment.infile_predicate(file_id),
        default_value={},
    )
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == 200

    # fail restore experiment because revision own is config
    response = await taxi_exp_client.post(
        '/v1/experiments/restore/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 3, 'revision': 2},
    )
    assert response.status == 409
    response_body = await response.json()
    assert response_body['code'] == 'RESTORE_ERROR'

    # fail restore experiment because revision own is another experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/restore/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 3, 'revision': 1},
    )
    assert response.status == 409
    response_body = await response.json()
    assert response_body['code'] == 'RESTORE_ERROR'
