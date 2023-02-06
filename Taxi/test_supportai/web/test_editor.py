import copy

import pytest


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai', files=['default.sql', 'lavka.sql']),
]


@pytest.mark.parametrize('entity,num', [('tag', 5), ('line', 2)])
async def test_get_simple_entity(web_app_client, entity, num):
    response = await web_app_client.get(
        f'/v1/{entity}s?user_id=1&project_slug=ya_lavka',
    )
    assert response.status == 200
    assert len((await response.json())[f'{entity}s']) == num


async def test_post_scenarios_search(web_app_client):
    all_scenarios = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka', json={},
    )
    assert all_scenarios.status == 200
    all_scenarios_json = await all_scenarios.json()
    assert len(all_scenarios_json['scenarios']) == 4
    assert all_scenarios_json['total'] == 4

    by_topic = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka',
        json={'topic_id': '3'},
    )
    assert by_topic.status == 200
    by_topic_json = await by_topic.json()
    assert len(by_topic_json['scenarios']) == 2
    assert by_topic_json['total'] == 2

    first_page = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka',
        json={'topic_id': '3', 'limit': 1},
    )
    first_page_data = await first_page.json()
    assert first_page_data['total'] == 2
    assert len(first_page_data['scenarios']) == 1
    first_page_scenario = first_page_data['scenarios'][0]
    first_page_scenario_id = first_page_scenario['id']
    assert first_page_scenario_id == '2'
    assert first_page_scenario['actions'][0]['forward_line'] == 'line2'
    assert not first_page_scenario['tags']
    assert not first_page_scenario['clarify_order']

    second_page = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka',
        json={
            'topic_id': '3',
            'limit': 1,
            'newer_than': first_page_scenario_id,
        },
    )
    second_page_data = await second_page.json()
    assert len(second_page_data['scenarios']) == 1
    assert second_page_data['total'] == 2
    second_page_scenario = second_page_data['scenarios'][0]
    second_page_scenario_id = second_page_scenario['id']
    assert second_page_scenario_id != first_page_scenario_id
    assert 'forward_line' not in second_page_scenario['actions'][0]
    tag_slugs = [tag['slug'] for tag in second_page_scenario['tags']]
    assert sorted(tag_slugs) == sorted(['tag1', 'tag3', 'complex_tag_slug'])
    feature_slugs = [
        feature['slug'] for feature in second_page_scenario['clarify_order']
    ]
    assert feature_slugs == ['feature2', 'feature1']

    by_russian_text = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka',
        json={'topic_id': '3', 'search_text': 'СцЕнАрИй 2 3й'},
    )
    by_russian_text_data = await by_russian_text.json()
    assert len(by_russian_text_data['scenarios']) == 1
    assert by_russian_text_data['total'] == 1

    by_english_text = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka',
        json={'topic_id': '2', 'search_text': 'NaMe'},
    )
    by_english_text_data = await by_english_text.json()
    assert len(by_english_text_data['scenarios']) == 1
    assert by_english_text_data['total'] == 1

    by_tag = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka',
        json={'topic_id': '3', 'search_text': 'complex_Tag'},
    )
    by_tag_data = await by_tag.json()
    assert len(by_tag_data['scenarios']) == 1
    assert by_tag_data['total'] == 1


@pytest.mark.parametrize('entity', ['tag', 'line'])
async def test_post_simple_entity(web_app_client, entity):
    slug = f'new_{entity}'
    new_entity_resp = await web_app_client.post(
        f'/v1/{entity}s?user_id=1&project_slug=ya_lavka',
        json={'id': '', 'slug': slug},
    )

    assert new_entity_resp.status == 200
    new_entity = await new_entity_resp.json()
    assert new_entity['slug'] == slug
    all_entities_resp = await web_app_client.get(
        f'/v1/{entity}s?user_id=1&project_slug=ya_lavka',
    )
    all_entities = await all_entities_resp.json()
    assert slug in [entity['slug'] for entity in all_entities[f'{entity}s']]


@pytest.mark.parametrize('entity', ['tag', 'line', 'feature', 'topic'])
async def test_delete_absent_simple_entity(web_app_client, entity):
    incorrect_resp = await web_app_client.delete(
        f'/v1/{entity}s/20000?user_id=1&project_slug=ya_lavka',
    )
    # for the sake of simplification
    assert incorrect_resp.status == 400


async def test_delete_tag(web_app_client):
    resp = await web_app_client.delete(
        f'/v1/tags/1?user_id=1&project_slug=ya_lavka',
    )
    assert resp.status == 200
    all_tags_resp = await web_app_client.get(
        f'/v1/tags?user_id=1&project_slug=ya_lavka',
    )
    all_tags = await all_tags_resp.json()
    assert 1 not in [int(tag['id']) for tag in all_tags[f'tags']]


async def test_delete_free_line(web_app_client):
    resp = await web_app_client.delete(
        f'/v1/lines/1?user_id=1&project_slug=ya_lavka',
    )
    assert resp.status == 200
    all_lines_resp = await web_app_client.get(
        f'/v1/lines?user_id=1&project_slug=ya_lavka',
    )
    all_lines = await all_lines_resp.json()
    assert 1 not in [int(line['id']) for line in all_lines[f'lines']]


@pytest.mark.parametrize(
    'method,url',
    [
        ('post', '/v1/scenarios?user_id=1&project_slug=ya_lavka'),
        ('put', '/v1/scenarios/1?user_id=1&project_slug=ya_lavka'),
    ],
)
@pytest.mark.parametrize(
    'rule,rule_is_correct',
    [
        ({'parts': ['True']}, True),
        ({'parts': 'a abracadabra b'}, False),
        ({'parts': []}, False),
        ({'parts': ['strange_feature', 'feature1']}, False),
        ({'parts': ['False', 'True']}, True),
    ],
)
async def test_post_put_scenarios(
        web_app_client, method, url, rule, rule_is_correct,
):

    new_scenario_resp = await getattr(web_app_client, method)(
        url,
        json={
            'id': '',
            'topic_id': '3',
            'title': 'Some new title',
            'tags': [{'id': '1', 'project_slug': '1', 'slug': 'tag1'}],
            'rule': rule,
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
            'available': True,
            'extra': {'test': '123'},
        },
    )

    new_scenario = await new_scenario_resp.json()
    if not rule_is_correct:
        assert (
            new_scenario_resp.status == 500 or new_scenario_resp.status == 400
        )
        return

    assert new_scenario_resp.status == 200

    assert new_scenario['id']

    tag_slugs = [tag['slug'] for tag in new_scenario['tags']]
    assert tag_slugs == ['tag1']

    feature_slugs = [
        feature['slug'] for feature in new_scenario['clarify_order']
    ]
    assert feature_slugs == ['feature2', 'feature1']

    search_resp = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka',
        json={'search_text': 'Some new title'},
    )
    search_resp_data = await search_resp.json()
    assert len(search_resp_data['scenarios']) == 1
    scenario = search_resp_data['scenarios'][0]

    assert scenario['id'] == new_scenario['id']

    assert scenario['short_description'] == scenario['id']
    assert len(scenario['actions']) == 3
    assert scenario['actions'][1] == new_scenario['actions'][1]


async def test_delete_scenario(web_app_client):
    resp = await web_app_client.delete(
        f'/v1/scenarios/1?user_id=1&project_slug=ya_lavka',
    )
    assert resp.status == 200

    all_scenarios_resp = await web_app_client.post(
        f'/v1/scenarios/search?user_id=1&project_slug=ya_lavka', json={},
    )
    all_scenarios = await all_scenarios_resp.json()
    assert 1 not in [
        int(scenario['id']) for scenario in all_scenarios[f'scenarios']
    ]


async def test_validate_scenarios(web_app_client):
    search_resp = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka',
        json={'search_text': 'Сценарий 1 1й тематики'},
    )
    search_resp_data = await search_resp.json()
    scenario = search_resp_data['scenarios'][0]

    correct_resp = await web_app_client.post(
        '/v1/scenarios/validate?user_id=1&project_slug=ya_lavka',
        json=scenario,
    )
    assert correct_resp.status == 200
    correct_resp_data = await correct_resp.json()
    assert correct_resp_data['is_valid']

    def absent_tag(data):
        data['tags'][0]['id'] = '34'

    def project_mismatch_tag(data):
        data['tags'][0]['id'] = '5'

    def absent_line(data):
        data['actions'][0]['forward_line'] = 'not_exists'

    def incorrect_change_state_feature(data):
        data['actions'][1]['features'][0]['key'] = 'not_exists'

    def wrong_rule_value(data):
        data['rule']['parts'] = ['a abracadabra b']

    def incorrect_feature_in_rule(data):
        data['rule']['parts'] = ['strange_feature and feature1']

    def non_eval_predicate(data):
        data['rule']['parts'] = ['feature1 contains {}']

    def complex_predicate(data):
        data['rule']['parts'] = [
            'feature1 is 1 and '
            '(feature2 is undefined or not_exists_feature is null)',
        ]

    for corruption_actions in (
            absent_tag,
            project_mismatch_tag,
            absent_line,
            incorrect_change_state_feature,
            wrong_rule_value,
            incorrect_feature_in_rule,
            non_eval_predicate,
            complex_predicate,
    ):
        new_data = copy.deepcopy(scenario)
        corruption_actions(new_data)

        resp = await web_app_client.post(
            '/v1/scenarios/validate?user_id=1&project_slug=ya_lavka',
            json=new_data,
        )

        assert resp.status == 200
        resp_data = await resp.json()
        assert not resp_data['is_valid']
