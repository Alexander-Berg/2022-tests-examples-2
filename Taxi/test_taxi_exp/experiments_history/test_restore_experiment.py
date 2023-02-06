import contextlib

import pytest

from test_taxi_exp.helpers import experiment
from test_taxi_exp.helpers import files
from test_taxi_exp.helpers import filters

NAME = 'experiment_for_restore'
FILE_CONTENT = (
    b'5ab66ff9cab04dfcb778147be85f1297\n' b'e2ed1c509f8f47eb82cb2d7fc42a6ee2\n'
)


async def _restore_old_consumer(taxi_exp_client):
    return await filters.add_consumer(taxi_exp_client, 'test_consumer')


async def _remove_old_consumer(taxi_exp_client):
    return await filters.remove_consumer(taxi_exp_client, 'test_consumer')


async def _restore_application(taxi_exp_client):
    return await filters.add_application(taxi_exp_client, 'ios')


async def _remove_application(taxi_exp_client):
    return await filters.remove_application(taxi_exp_client, 'ios')


@contextlib.asynccontextmanager
async def _temporary(client, before, after):
    await before(client)
    yield
    await after(client)


@pytest.mark.pgsql('taxi_exp', files=('default.sql',))
@pytest.mark.now('2020-11-01T23:59:59+03:00')
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'settings': {
            'common': {
                'departments': {'commando': {'map_to_namespace': 'market'}},
            },
        },
    },
)
async def test_restore_by_history(taxi_exp_client):
    # upload file
    response = await files.post_file(
        taxi_exp_client, 'file_1.txt', FILE_CONTENT, file_type='string',
    )
    assert response.status == 200
    file_id = (await response.json())['id']

    # generate experiment body
    body = experiment.generate(
        consumers=[{'name': 'test_consumer'}],
        match_predicate=experiment.infile_predicate(file_id),
        default_value={},
        applications=[
            {
                'name': 'ios',
                'version_range': {'from': '0.0.0', 'to': '99.99.99'},
            },
        ],
        action_time={
            'from': '2020-01-01T12:35:00+03:00',
            'to': '2020-12-31T23:59:59+03:00',
        },
        department='commando',
    )

    # create experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
        json=body,
    )
    assert response.status == 200, await response.text()

    # create new consumer
    response = await taxi_exp_client.post(
        '/v1/experiments/filters/consumers/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': 'other_test_consumer'},
    )
    assert response.status == 200

    # update experiment with new consumer
    body = experiment.generate(
        consumers=[{'name': 'other_test_consumer'}],
        match_predicate=experiment.DEFAULT,
        department='commando',
    )
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 1},
        json=body,
    )
    assert response.status == 200

    # success restore experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/restore/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 2, 'revision': 1},
    )
    assert response.status == 200
    response_body = await response.json()
    assert response_body['tplatform_namespace'] == 'market'
    response = await taxi_exp_client.get(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME},
    )
    assert response.status == 200
    response_body = await response.json()
    assert response_body['match']['consumers'] == [{'name': 'test_consumer'}]
    assert (
        response_body['match']['action_time']['from']
        == '2020-01-01T12:35:00+03:00'
    )
    assert (
        response_body['match']['action_time']['to']
        == '2020-12-31T23:59:59+03:00'
    )

    # retry update experiment with new consumer
    response = await taxi_exp_client.put(
        '/v1/experiments/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 3},
        json=body,
    )
    assert response.status == 200

    async with _temporary(
            taxi_exp_client, _remove_old_consumer, _restore_old_consumer,
    ):
        # fail restore experiment because consumer not found
        response = await taxi_exp_client.post(
            '/v1/experiments/restore/',
            headers={'X-Ya-Service-Ticket': '123'},
            params={'name': NAME, 'last_modified_at': 4, 'revision': 1},
        )
        assert response.status == 409
        response_body = await response.json()
        assert response_body['code'] == 'DATABASE_ERROR'
        assert 'consumer' in response_body['message']

    async with _temporary(
            taxi_exp_client, _remove_application, _restore_application,
    ):
        # fail restore experiment because application not found
        response = await taxi_exp_client.post(
            '/v1/experiments/restore/',
            headers={'X-Ya-Service-Ticket': '123'},
            params={'name': NAME, 'last_modified_at': 4, 'revision': 1},
        )
        assert response.status == 409
        response_body = await response.json()
        assert response_body['code'] == 'DATABASE_ERROR'
        assert 'application' in response_body['message']

    # remove old file
    response = await taxi_exp_client.delete(
        '/v1/files/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'id': file_id},
    )
    assert response.status == 200

    # fail restore experiment because file not found
    response = await taxi_exp_client.post(
        '/v1/experiments/restore/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 4, 'revision': 1},
    )
    assert response.status == 409
    response_body = await response.json()
    assert response_body['code'] == 'DATABASE_ERROR'
    assert 'file' in response_body['message']

    # fail restore experiment because restore revision > current
    response = await taxi_exp_client.post(
        '/v1/experiments/restore/',
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 1, 'revision': 3},
    )
    assert response.status == 400
