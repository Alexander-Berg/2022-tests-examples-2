async def test_priority_types(client, headers):
    response = await client.get('/v1/admin/priority/types', headers=headers)
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'prioritized_entity_type': 'bin_set', 'has_entity': True},
            {'prioritized_entity_type': 'class', 'has_entity': False},
            {'prioritized_entity_type': 'experiment', 'has_entity': False},
        ],
    }
