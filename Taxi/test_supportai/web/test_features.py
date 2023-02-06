import pytest

from supportai.common import core_features

CORE_FEATURE_COUNT = len(core_features.CORE_FEATURES.keys())


def check_feature_content(feature, ref_feature):
    assert feature['slug'] == ref_feature['slug']
    assert feature['description'] == ref_feature['description']
    assert feature['type'] == ref_feature['type']
    assert feature['is_array'] == ref_feature['is_array']
    assert feature['domain'] == ref_feature['domain']
    assert feature['clarification_type'] == ref_feature['clarification_type']

    def _check_optional(field):
        if field in ref_feature:
            assert feature[field] == ref_feature[field]

    _check_optional('force_question')
    _check_optional('clarifying_question')
    _check_optional('default_value')
    _check_optional('entity_id')
    _check_optional('entity_extract_order')


@pytest.mark.pgsql('supportai', files=['default.sql', 'sample_features.sql'])
async def test_get_features(web_app_client):
    all_features_response = await web_app_client.get(
        '/v1/features?user_id=1&project_slug=ya_lavka',
    )
    assert all_features_response.status == 200
    assert (
        len((await all_features_response.json())['features'])
        == 4 + CORE_FEATURE_COUNT
    )


@pytest.mark.parametrize(
    'type_,is_array,is_calculated,domain,predicate,valid',
    [
        ('int', False, False, ['1', '2'], None, True),
        ('float', False, False, ['0.1', '5'], None, True),
        ('bool', False, False, ['True', 'False'], None, True),
        ('str', False, False, ['foo', 'bar', '42'], None, True),
        ('int', False, False, [], None, True),
        ('int', False, False, ['1a', '2'], None, False),
        ('float', False, False, ['0,1', '2cv'], None, False),
        ('bool', False, False, ['Not_True', 'Not_False'], None, False),
        ('int', True, False, ['[1]', '[1,2]'], None, True),
        ('int', True, False, ['["abc"]', '[1,2]'], None, False),
        ('str', True, False, ['[abc', '["a", "b"]'], None, False),
        ('str', False, True, [], None, False),
        ('bool', False, True, [], '=== 100', False),
        ('bool', False, True, [], 'iteration_number = 1', True),
    ],
)
@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_create_feature(
        web_app_client,
        type_,
        domain,
        valid,
        is_array,
        is_calculated,
        predicate,
):
    ref_feature = {
        'id': '',
        'slug': 'new_feature',
        'description': 'New feature',
        'type': type_,
        'is_array': is_array,
        'is_calculated': is_calculated,
        'domain': domain,
        'clarification_type': 'external',
    }

    if predicate is not None:
        ref_feature['predicate'] = predicate

    feature_response = await web_app_client.post(
        '/v1/features?user_id=1&project_slug=ya_market', json=ref_feature,
    )

    assert feature_response.status == (200 if valid else 400)

    if valid:
        new_feature = await feature_response.json()

        check_feature_content(new_feature, ref_feature)

        all_features_response = await web_app_client.get(
            '/v1/features?user_id=1&project_slug=ya_market',
        )

        all_features_response_json = await all_features_response.json()

        assert (
            len(all_features_response_json['features'])
            == 1 + CORE_FEATURE_COUNT
        )

        assert new_feature['id'] in [
            entity['id'] for entity in all_features_response_json['features']
        ]


@pytest.mark.parametrize(
    'force_question, clarifying_question, entity_id, valid',  # noqa
    [
        (False, None, '1', True),
        (True, '', None, False),
        (True, 'Clarify question', '1', True),
        (False, 'Clarify question', '1', True),
        (False, None, '1', True),
        (False, None, '2', False),
        (False, None, '3', False),
    ],
)
@pytest.mark.pgsql('supportai', files=['default.sql', 'sample_features.sql'])
async def test_create_complex_feature(
        web_app_client, force_question, clarifying_question, entity_id, valid,
):
    ref_feature = {
        'id': '',
        'slug': 'new_feature',
        'description': 'New feature',
        'type': 'str',
        'is_array': False,
        'domain': [],
        'clarification_type': 'from_text',
        'force_question': force_question,
    }

    if clarifying_question:
        ref_feature['clarifying_question'] = clarifying_question

    if entity_id:
        ref_feature['entity_id'] = entity_id
        ref_feature['entity_extract_order'] = 0

    feature_response = await web_app_client.post(
        '/v1/features?user_id=1&project_slug=ya_lavka', json=ref_feature,
    )

    assert feature_response.status == (200 if valid else 400)

    if valid:
        new_feature = await feature_response.json()
        check_feature_content(new_feature, ref_feature)


@pytest.mark.pgsql('supportai', files=['default.sql'])
async def test_post_features_bulk(web_app_client):

    ref_features = [
        {
            'id': '',
            'slug': 'new_feature1',
            'description': 'New feature1',
            'type': 'str',
            'is_array': False,
            'domain': ['srt1', 'srt2'],
            'clarification_type': 'external',
        },
        {
            'id': '',
            'slug': 'new_feature2',
            'description': 'New feature2',
            'type': 'int',
            'is_array': False,
            'domain': ['1', '2'],
            'clarification_type': 'external',
        },
        {
            'id': '',
            'slug': 'new_feature3',
            'description': 'New feature3',
            'type': 'bool',
            'is_array': False,
            'is_calculated': True,
            'domain': [],
            'predicate': 'iteration_number = 1',
        },
    ]

    feature_response = await web_app_client.post(
        '/supportai/v1/features?user_id=1&project_slug=ya_lavka',
        json={'features': ref_features},
    )

    assert feature_response.status == 200

    new_features = (await feature_response.json())['features']

    assert len(new_features) == 3

    for idx, ref_feature in enumerate(ref_features[:2]):
        check_feature_content(new_features[idx], ref_feature)

    assert 'predicate' in ref_features[-1]


@pytest.mark.parametrize(
    'type_,domain,default_value,valid',
    [
        ('bool', ['1', '2'], None, False),
        ('float', ['0.1', '5'], None, True),
        ('float', [], '0.5', True),
        ('float', [], 'abc', False),
    ],
)
@pytest.mark.pgsql('supportai', files=['default.sql', 'sample_features.sql'])
async def test_update_feature(
        web_app_client, type_, domain, default_value, valid,
):
    ref_feature = {
        'id': '3',
        'slug': 'feature3',
        'description': 'New feature',
        'type': type_,
        'is_array': False,
        'domain': domain,
        'clarification_type': 'external',
    }

    if default_value is not None:
        ref_feature['default_value'] = default_value

    update_feature_response = await web_app_client.put(
        '/v1/features/3?user_id=1&project_slug=ya_lavka', json=ref_feature,
    )

    assert update_feature_response.status == (200 if valid else 400)

    if valid:
        updated_feature = await update_feature_response.json()

        check_feature_content(updated_feature, ref_feature)

        all_features_response = await web_app_client.get(
            '/v1/features?user_id=1&project_slug=ya_lavka',
        )

        all_features_response_json = await all_features_response.json()

        for feature in all_features_response_json['features']:
            if feature['id'] == ref_feature['id']:
                check_feature_content(feature, ref_feature)
                break


@pytest.mark.pgsql('supportai', files=['default.sql', 'sample_features.sql'])
async def test_update_features_bulk(web_app_client):
    ref_features = [
        {
            'id': '1',
            'slug': 'feature1',
            'description': 'Feature 1',
            'type': 'int',
            'is_array': False,
            'domain': ['1', '2'],
            'clarification_type': 'external',
            'default_value': '10',
        },
        {
            'id': '2',
            'slug': 'feature2',
            'description': 'Feature 2',
            'type': 'float',
            'is_array': False,
            'domain': ['0.1', '0.2'],
            'clarification_type': 'external',
            'default_value': '0.7',
        },
    ]

    update_features_response = await web_app_client.put(
        '/v1/features/bulk?user_id=1&project_slug=ya_lavka',
        json={'features': ref_features},
    )

    assert update_features_response.status == 200

    updated_features = await update_features_response.json()

    assert len(ref_features) == len(updated_features['features'])

    for idx, feature in enumerate(ref_features):
        check_feature_content(updated_features['features'][idx], feature)

    all_features_response = await web_app_client.get(
        '/v1/features?user_id=1&project_slug=ya_lavka',
    )

    all_features_response_json = await all_features_response.json()

    for feature in all_features_response_json['features']:
        for ref_feature in ref_features:
            if feature['id'] == ref_feature['id']:
                check_feature_content(feature, ref_feature)
                break

    update_features_response = await web_app_client.put(
        '/v1/features/bulk?user_id=1&project_slug=ya_lavka',
        json={'features': []},
    )

    assert update_features_response.status == 200


@pytest.mark.pgsql('supportai', files=['default.sql', 'sample_features.sql'])
async def test_update_feature_without_access(web_app_client):
    ref_feature = {
        'id': '5',
        'slug': 'feature3',
        'description': 'New feature',
        'type': 'str',
        'domain': [],
        'clarification_type': 'external',
    }

    update_feature_response = await web_app_client.put(
        '/v1/features/5?user_id=1&project_slug=ya_lavka', json=ref_feature,
    )

    assert update_feature_response.status == 403


@pytest.mark.pgsql('supportai', files=['default.sql', 'sample_features.sql'])
async def test_delete_feature_with_scenario_link(web_app_client):

    remove_feature_response = await web_app_client.delete(
        '/v1/features/1?user_id=1&project_slug=ya_lavka',
    )

    assert remove_feature_response.status == 200

    all_scenarios = await web_app_client.post(
        '/v1/scenarios/search?user_id=1&project_slug=ya_lavka', json={},
    )

    first_scenario = (await all_scenarios.json())['scenarios'][0]
    assert len(first_scenario['clarify_order']) == 1

    assert first_scenario['clarify_order'][0]['id'] == '2'


@pytest.mark.pgsql('supportai', files=['default.sql', 'sample_features.sql'])
async def test_delete_feature_without_access(web_app_client):

    remove_feature_response = await web_app_client.delete(
        '/v1/features/5?user_id=1&project_slug=ya_lavka',
    )

    assert remove_feature_response.status == 403
