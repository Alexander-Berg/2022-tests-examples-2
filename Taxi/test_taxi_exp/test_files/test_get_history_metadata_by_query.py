import pytest


@pytest.mark.parametrize(
    'link, expected',
    [
        pytest.param(
            'by_experiment',
            {'action': 'create', 'id': '11111', 'name': 'user_ids.txt'},
            marks=pytest.mark.pgsql(
                'taxi_exp', files=('history_by_experiment.sql',),
            ),
        ),
        pytest.param(
            'by_config',
            {
                'action': 'create',
                'id': 'c11111',
                'name': 'config_user_ids.txt',
            },
            marks=pytest.mark.pgsql(
                'taxi_exp', files=('history_by_experiment.sql',),
            ),
        ),
    ],
)
async def test_get_history_files_by_experiment(
        taxi_exp_client, link, expected,
):
    response = await taxi_exp_client.get(
        f'/v1/files/history/{link}/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'n1'},
    )

    data = await response.json()
    assert len(data['history']) == 3

    item = data['history'][0]
    item.pop('updated')
    item.pop('namespace')
    assert item == expected
