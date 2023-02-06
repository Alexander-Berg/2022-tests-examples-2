import pytest


@pytest.mark.pgsql('taxi_exp', files=['financial_and_not_experiments.sql'])
@pytest.mark.parametrize('type_name', ['experiment', 'config'])
async def test_hide_financial_filter(taxi_exp_client, type_name):

    response = await taxi_exp_client.get(
        f'/v1/{type_name}s/list/', headers={'YaTaxi-Api-Key': 'secret'},
    )
    assert response.status == 200
    result = await response.json()
    names = {experiment['name'] for experiment in result[f'{type_name}s']}
    assert names == {f'financial_{type_name}', f'not_financial_{type_name}'}

    response = await taxi_exp_client.get(
        f'/v1/{type_name}s/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'get_financial': 'False'},
    )
    assert response.status == 200
    result = await response.json()
    print(result)
    names = {experiment['name'] for experiment in result[f'{type_name}s']}
    assert names == {f'not_financial_{type_name}'}

    response = await taxi_exp_client.get(
        f'/v1/{type_name}s/list/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'get_financial': 'True'},
    )
    assert response.status == 200
    result = await response.json()
    names = {experiment['name'] for experiment in result[f'{type_name}s']}
    assert names == {f'financial_{type_name}'}
