async def test_operation_list(taxi_virtual_tariffs):
    response = await taxi_virtual_tariffs.get('/v1/operation/list')
    assert response.status_code == 200
    assert 'operations' in response.json()
    assert set(response.json()['operations']) == set(
        [
            'Greater',
            'ContainsAll',
            'LessOrEqual',
            'NotContainsAll',
            'ContainsOneOf',
            'ContainsNoOne',
        ],
    )


async def test_contexts_list(taxi_virtual_tariffs):
    response = await taxi_virtual_tariffs.get('/v1/context/list')
    assert response.status_code == 200
    assert 'contexts' in response.json()
    assert set(response.json()['contexts']) == set(
        ['Tags', 'Exams', 'TaximeterFeatures'],
    )
