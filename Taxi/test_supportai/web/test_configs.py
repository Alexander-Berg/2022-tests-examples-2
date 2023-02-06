import pytest


@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_custom_configs(web_app_client):
    response = await web_app_client.get(
        f'/v1/configs/custom?project_slug=ya_lavka&user_id=1',
    )

    assert response.status == 204

    response = await web_app_client.post(
        f'/v1/configs/custom?project_slug=ya_lavka&user_id=1',
        json={
            'id': '',
            'value': {'nlu': {}, 'nlg': {'some_param': 'param_value'}},
        },
    )
    assert response.status == 200

    config = await response.json()

    response = await web_app_client.get(
        f'/v1/configs/custom?project_slug=ya_lavka&user_id=1',
    )

    assert response.status == 200
    get_config = await response.json()

    assert get_config == config


@pytest.mark.pgsql('supportai', files=['default.sql', 'data.sql'])
async def test_full_config(web_app_client):
    response = await web_app_client.get(
        f'/v1/configs/full?project_slug=ya_lavka&user_id=1',
    )

    assert response.status == 200
    response_json = await response.json()

    assert 'nlg' in response_json
    assert len(response_json['nlg']['enrich']) == 1
    assert (
        response_json['nlg']['localisations']['greeting']['ru']
        == 'Здравствуйте!'
    )

    assert len(response_json['nlu']['topics']) == 4
    assert 'policy_graph' in response_json
    assert 'main' in response_json['policy_graph']


@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_custom_configs_not_valid_filter(web_app_client):
    response = await web_app_client.post(
        f'/v1/configs/custom?project_slug=ya_lavka&user_id=1',
        json={
            'id': '',
            'value': {
                'nlu': {
                    'preprocessor': {
                        'text_filter': {'regexp_extractors': [r'[.*']},
                    },
                },
                'nlg': {'some_param': 'param_value'},
            },
        },
    )

    assert response.status == 400


@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_custom_configs_not_valid_replacer(web_app_client):
    response = await web_app_client.post(
        f'/v1/configs/custom?project_slug=ya_lavka&user_id=1',
        json={
            'id': '',
            'value': {
                'nlu': {
                    'preprocessor': {
                        'text_filter': {'regexp_extractors': [r'abcdef']},
                        'text_replacer': {
                            'replacements': [[r'b', 'a'], [r'[^]', 'c']],
                        },
                    },
                },
                'nlg': {'some_param': 'param_value'},
            },
        },
    )

    assert response.status == 400


@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_custom_configs_bool_values(web_app_client):
    response = await web_app_client.post(
        f'/v1/configs/custom?project_slug=ya_lavka&user_id=1',
        json={
            'id': '',
            'value': {
                'nlu': {
                    'preprocessor': {'text_filter': {'filter_html': 'true'}},
                },
                'nlg': {'some_param': 'param_value'},
            },
        },
    )

    assert response.status == 200


@pytest.mark.pgsql('supportai', files=['multiple_actions.sql'])
async def test_custom_config_multiple_actions(web_app_client):
    expected_graph_output = {
        'graph': {
            '1': {
                'links': {'': {'next': 'XXXX'}, 'XXXX': {'next': 'XXXX2'}},
                'title': 'my_lovely_graph',
            },
        },
        'nodes': {
            'XXXX': {
                'slug': '',
                'type': 'action',
                'action': {
                    'type': 'action_1',
                    'parameters': {
                        'parameter_1': 'value_1',
                        'parameter_2': 'value_2',
                    },
                },
                'actions': [
                    {
                        'type': 'action_2',
                        'parameters': {'parameter_3': 'value_3'},
                    },
                    {
                        'type': 'action_3',
                        'parameters': {
                            'parameter_4': 'value_4',
                            'parameter_5': 'value_5',
                        },
                    },
                ],
                'tags': [],
                'counter': None,
            },
            'XXXX2': {
                'slug': '',
                'type': 'close',
                'action': {'type': 'close', 'parameters': {}},
                'actions': None,
                'tags': [],
                'counter': None,
            },
        },
        'topics_slugs': [],
    }

    response = await web_app_client.get(
        f'/v1/configs/full?project_slug=ya_lavka&user_id=1',
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['policy_graph']['main'] == expected_graph_output
