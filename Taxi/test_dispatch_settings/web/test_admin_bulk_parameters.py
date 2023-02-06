async def test_bulk_properties(taxi_dispatch_settings_web):
    response = await taxi_dispatch_settings_web.get(
        '/v1/admin/bulk/parameters',
    )
    assert response.status == 200

    content = await response.json()

    # Response normalization
    content['parameters'].sort(key=lambda param: param['name'])

    assert content == {
        'parameters': [
            {'name': 'PARAM_A', 'available_actions': ['test_action_1']},
            {
                'name': 'PARAM_B',
                'available_actions': [
                    'test_action_2',
                    'test_action_1',
                    'test_action_3',
                ],
            },
            {
                'name': 'PARAM_C',
                'available_actions': [
                    'test_action_5',
                    'test_action_3',
                    'test_action_2',
                    'test_action_4',
                ],
            },
            {
                'name': 'PARAM_D',
                'available_actions': [
                    'test_action_add_items',
                    'test_action_remove',
                    'test_action_set',
                ],
            },
        ],
    }
