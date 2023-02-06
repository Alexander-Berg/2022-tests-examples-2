import pytest


@pytest.mark.parametrize(
    'data_type, count',
    [
        ('features', 3),
        ('entities', 1),
        ('topics', 4),
        ('features', 3),
        ('scenarios', 2),
        ('tags', 2),
        ('lines', 2),
    ],
)
@pytest.mark.pgsql('supportai', files=['default.sql', 'data.sql'])
async def test_get_bulk_data(web_app_client, data_type, count):
    all_features_response = await web_app_client.get(
        f'/supportai/v1/{data_type}?project_slug=ya_lavka&limit=10&offset=0',
    )
    assert all_features_response.status == 200
    assert len((await all_features_response.json())[data_type]) == count


@pytest.mark.parametrize('data_type', ['tags', 'lines'])
@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_post_simple_entities_bulk(web_app_client, data_type):

    new_entities_resp = await web_app_client.post(
        f'/supportai/v1/{data_type}?project_slug=ya_lavka',
        json={
            data_type: [
                {'id': '', 'slug': 'new_ent_1'},
                {'id': '', 'slug': 'new_ent_2'},
            ],
        },
    )

    assert new_entities_resp.status == 200
    new_entities = await new_entities_resp.json()

    assert new_entities[data_type][0]['slug'] == 'new_ent_1'
    assert new_entities[data_type][1]['slug'] == 'new_ent_2'

    all_entities_resp = await web_app_client.get(
        f'/supportai/v1/{data_type}?project_slug=ya_lavka&limit=10&offset=0',
    )

    all_entities = await all_entities_resp.json()

    slugs = [entity['slug'] for entity in all_entities[f'{data_type}']]

    assert 'new_ent_1' in slugs
    assert 'new_ent_2' in slugs


@pytest.mark.pgsql('supportai', files=['default.sql', 'data.sql'])
async def test_post_scenarios_bulk(web_app_client):
    scenarios = []

    for idx in range(1, 3):
        scenarios.append(
            {
                'id': '',
                'topic_id': str(idx),
                'title': f'Some new title {idx}',
                'tags': [
                    {'id': str(idx), 'project_slug': '1', 'slug': f'tag{idx}'},
                ],
                'rule': {'parts': ['True']},
                'clarify_order': [
                    {
                        'id': '2',
                        'project_slug': '1',
                        'slug': 'feature2',
                        'description': 'Feature 2',
                        'type': 'str',
                        'domain': ['abc', 'cba'],
                    },
                    {
                        'id': '1',
                        'project_slug': '1',
                        'slug': 'feature1',
                        'description': 'Feature 2',
                        'type': 'int',
                        'domain': ['1', '2'],
                    },
                ],
                'available': True,
                'actions': [
                    {
                        'type': 'response',
                        'texts': ['1234', '4321'],
                        'delay_value_sec': 60,
                        'forward_line': 'line1',
                        'close': True,
                    },
                    {
                        'type': 'change_state',
                        'features': [
                            {'key': 'feature1', 'value': 'Feature value'},
                        ],
                    },
                    {
                        'type': 'custom',
                        'action_type': 'some_custom_actions',
                        'parameters': {'param1': 'Param 1'},
                    },
                ],
            },
        )

    new_scenarios_resp = await web_app_client.post(
        '/supportai/v1/scenarios?project_slug=ya_lavka',
        json={'scenarios': scenarios},
    )

    assert new_scenarios_resp.status == 200
    new_scenarios = (await new_scenarios_resp.json())['scenarios']

    for idx, scenario in enumerate(new_scenarios):
        assert scenario['id']

    search_resp = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka',
        json={'search_text': 'Some new title'},
    )

    search_resp_data = await search_resp.json()
    search_scenarios = search_resp_data['scenarios']

    assert len(search_scenarios) == 2
    assert search_resp_data['total'] == 2

    for idx, search_scenario in enumerate(search_scenarios):
        new_scenario = new_scenarios[idx]

        assert new_scenario['id'] == search_scenario['id']

        tag_slugs = [tag['slug'] for tag in search_scenario['tags']]
        assert tag_slugs == [f'tag{idx + 1}']

        feature_slugs = [
            feature['slug'] for feature in search_scenario['clarify_order']
        ]
        assert feature_slugs == ['feature2', 'feature1']
