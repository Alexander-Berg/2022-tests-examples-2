import pytest


async def test_get_preset_cities(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.post(
        '/api/preset_cities', json={'user': 'preset_user'},
    )
    assert response.status == 200

    content = sorted(await response.json(), key=lambda x: x['_id'])
    assert len(content) == 4

    assert content[0]['public']
    assert content[1] == {
        '_id': '5acc85488d8d14f9b3f9473f',
        'cities': ['Москва', 'Казань'],
        'en': 'RTT Experiment 2',
        'name': 'RTT Experiment 2',
        'public': True,
        'user': 'preset_user',
    }


@pytest.mark.parametrize(
    'username, expected_status, expected_presets',
    [
        ('omnipotent_user', 200, {'All Cities', 'RTT Experiment 2'}),
        ('preset_user', 200, {'RTT Experiment 2', 'RTT Experiment 3'}),
        ('super_user', 200, {'All Cities', 'RTT Experiment 2'}),
        ('restricted_user', 200, {'All Cities', 'RTT Experiment 2'}),
        ('main_user', 200, {'All Cities', 'RTT Experiment 2'}),
        ('nonexisted_user', 200, set()),
    ],
)
async def test_get_preset_cities_permissions(
        username,
        expected_status,
        web_app_client,
        atlas_blackbox_mock,
        expected_presets,
):
    response = await web_app_client.post(
        '/api/preset_cities', json={'user': username},
    )

    assert response.status == expected_status

    response_presets = {x['name'] for x in await response.json()}
    assert response_presets == expected_presets
