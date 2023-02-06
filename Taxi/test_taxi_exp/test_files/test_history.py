# pylint: disable=invalid-name
import pytest

from test_taxi_exp.helpers import files


@pytest.mark.parametrize(
    'params,count',
    [
        ({'id': '11111'}, 2),
        ({'name': 'user_ids.txt'}, 3),
        ({'action': 'create'}, 2),
    ],
)
@pytest.mark.pgsql('taxi_exp', files=('history_search.sql',))
async def test_history_search(params, count, taxi_exp_client):
    response = await files.history_search(
        taxi_exp_client, namespace=None, **params,
    )

    data = await response.json()
    assert len(data['history']) == count


@pytest.mark.pgsql('taxi_exp', files=('history_by_experiment.sql',))
async def test_get_history_files_by_experiment(taxi_exp_client):
    response = await files.get_history_by_experiment(taxi_exp_client, 'n1')

    data = await response.json()
    assert len(data['history']) == 3

    item = data['history'][0]
    item.pop('updated')
    assert item == {
        'action': 'create',
        'id': '11111',
        'name': 'user_ids.txt',
        'namespace': None,
    }
