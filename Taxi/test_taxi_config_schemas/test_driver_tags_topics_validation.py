from typing import Any
from typing import Dict

import pytest

from taxi_config_schemas import config_models
from test_taxi_config_schemas.configs import common

TAGS_SCHEMA = {
    'additionalProperties': {'$ref': '#/definitions/some_definition'},
    'properties': {'__default__': {'$ref': '#/definitions/some_definition'}},
    'required': ['__default__'],
    'type': 'object',
    'definitions': {
        'some_definition': {
            'type': 'object',
            'additionalProperties': False,
            'properties': {
                'test_one_of': {'$ref': '#/definitions/one_of_definition'},
                'tags_from_definition': {
                    'type': 'array',
                    'items': {'$ref': '#/definitions/subventions_topic_tags'},
                },
                'tags': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'x-taxi-driver-tags-from-topic': ['candidates'],
                },
            },
        },
        'subventions_topic_tags': {
            'type': 'array',
            'items': {'minLength': 1, 'type': 'string'},
            'x-taxi-driver-tags-from-topic': ['subventions'],
        },
        'one_of_definition': {
            'oneOf': [
                {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'x-taxi-driver-tags-from-topic': ['candidates'],
                },
                {'$ref': '#/definitions/AllOf'},
                {'$ref': '#/definitions/AnyOf'},
                {'$ref': '#/definitions/And'},
            ],
        },
        'And': {
            'type': 'object',
            'description': 'description',
            'additionalProperties': False,
            'properties': {
                'and': {
                    'type': 'array',
                    'items': {
                        'oneOf': [
                            {'$ref': '#/definitions/AllOf'},
                            {'$ref': '#/definitions/AnyOf'},
                        ],
                    },
                },
            },
        },
        'AllOf': {
            'type': 'object',
            'description': 'description',
            'additionalProperties': False,
            'properties': {
                'all_of_tags': {
                    '$ref': '#/definitions/subventions_topic_tags',
                },
            },
        },
        'AnyOf': {
            'type': 'object',
            'description': 'description',
            'additionalProperties': False,
            'properties': {
                'any_of_tags': {
                    '$ref': '#/definitions/subventions_topic_tags',
                },
            },
        },
    },
}

TAGS_DEFAULT_VALUE: Dict[str, Any] = {
    '__default__': {'tags': [], 'tags_from_definition': [[]]},
}

EMPTY_TAGS_RELATIONS: Dict[str, Any] = {}
CANDIDATES_TOPIC_RELATIONS = {'candidates': ['dispatch', 'cargo_van', 'vip']}
SUBVENTIONS_TOPIC_RELATIONS = {
    'subventions': ['discount_30', 'plus_user', 'vip'],
}
ALL_TOPICS_RELATIONS = dict(
    CANDIDATES_TOPIC_RELATIONS, **SUBVENTIONS_TOPIC_RELATIONS,
)


@pytest.mark.config(CONFIG_SCHEMAS_ENABLE_DRIVER_TAGS_TOPICS_VALIDATION=True)
@pytest.mark.parametrize(
    'new_value, has_tags_service_calls',
    [
        pytest.param(
            {'__default__': {'tags': 'not array'}}, False, id='bad field type',
        ),
        pytest.param(
            {'__default__': {'tags': [1234]}}, False, id='not string in array',
        ),
        pytest.param(
            {'__default__': {'tags': ['cargo_van']}},
            True,
            id='500 from tags call',
        ),
    ],
)
async def test_invalid_values(
        web_context, mockserver, new_value, has_tags_service_calls,
):
    @mockserver.json_handler('/tags/v1/topics_relations')
    def mock_tags_topics_relations(*args, **kwargs):
        return mockserver.make_response('', status=500)

    config_with_value = common.get_config_with_value(
        TAGS_DEFAULT_VALUE, TAGS_SCHEMA,
    )
    with pytest.raises(config_models.ValidationError):
        await config_with_value.validate(new_value, {}, web_context)
    assert mock_tags_topics_relations.has_calls == has_tags_service_calls


@pytest.mark.config(CONFIG_SCHEMAS_ENABLE_DRIVER_TAGS_TOPICS_VALIDATION=True)
@pytest.mark.parametrize(
    'new_value, topic_relations, topics_set, is_ok, times_called',
    [
        pytest.param(
            {'__default__': {'tags': []}},
            EMPTY_TAGS_RELATIONS,
            {'candidates'},
            True,
            0,
            id='empty tags array and relations',
        ),
        pytest.param(
            {'__default__': {'tags': []}},
            ALL_TOPICS_RELATIONS,
            {'candidates'},
            True,
            0,
            id='empty tags array',
        ),
        pytest.param(
            {'__default__': {'tags': ['']}},
            ALL_TOPICS_RELATIONS,
            {'candidates'},
            False,
            1,
            id='empty tag in array has no relation',
        ),
        pytest.param(
            {
                '__default__': {
                    'tags': ['cargo_van', 'plus_user', 'non_related_tag'],
                },
            },
            EMPTY_TAGS_RELATIONS,
            {'candidates'},
            False,
            1,
            id='empty relations',
        ),
        pytest.param(
            {
                '__default__': {
                    'tags': ['cargo_van', 'plus_user', 'non_related'],
                    'test_one_of': ['cargo_van'],
                },
            },
            ALL_TOPICS_RELATIONS,
            {'candidates'},
            False,
            1,
            id='no relation for not_related tag',
        ),
        pytest.param(
            {'__default__': {'tags': ['cargo_van', 'plus_user', 'vip']}},
            ALL_TOPICS_RELATIONS,
            {'candidates'},
            False,
            1,
            id='some tags not related with candidates topic',
        ),
        pytest.param(
            {
                '__default__': {
                    'tags_from_definition': [
                        ['cargo_van'],
                        ['plus_user'],
                        ['vip'],
                    ],
                },
            },
            ALL_TOPICS_RELATIONS,
            {'subventions'},
            False,
            1,
            id='some tags not related with subventions topic',
        ),
        pytest.param(
            {
                '__default__': {
                    'tags': ['plus_user'],
                    'test_one_of': {'bad_key': [{'any_of_tags': ['vip']}]},
                },
            },
            ALL_TOPICS_RELATIONS,
            {'plus_user'},
            False,
            0,
            id='first level one_of type mismatch, no tags requests',
        ),
        pytest.param(
            {
                '__default__': {
                    'tags': ['plus_user'],
                    'test_one_of': {'and': [['vip']]},
                },
            },
            ALL_TOPICS_RELATIONS,
            {'subventions'},
            False,
            0,
            id='second level one_of type mismatch, no tags requests',
        ),
        pytest.param(
            {
                '__default__': {
                    'tags': ['cargo_van', 'vip'],
                    'tags_from_definition': [['plus_user', 'vip']],
                    'test_one_of': {'any_of_tags': ['discount_30']},
                },
            },
            ALL_TOPICS_RELATIONS,
            {'candidates', 'subventions'},
            True,
            1,
            id='all tags has relations with necessary topics',
        ),
        pytest.param(
            {
                '__default__': {
                    'tags': ['cargo_van', 'vip'],
                    'test_one_of': {
                        'and': [
                            {'all_of_tags': ['discount_30']},
                            {'any_of_tags': ['plus_user']},
                        ],
                    },
                },
            },
            ALL_TOPICS_RELATIONS,
            {'candidates', 'subventions'},
            True,
            1,
            id='all one_of tags has relations with necessary topics',
        ),
        pytest.param(
            {
                '__default__': {
                    'tags': ['cargo_van', 'vip'],
                    'test_one_of': ['dispatch'],
                },
            },
            CANDIDATES_TOPIC_RELATIONS,
            {'candidates'},
            True,
            1,
            id='only candidates topic tags',
        ),
        pytest.param(
            {'__default__': {'tags': ['discount']}},
            CANDIDATES_TOPIC_RELATIONS,
            {'candidates'},
            False,
            1,
            id='tag has relation, but for another topic',
        ),
        pytest.param(
            {
                '__default__': {
                    'tags': ['vip'],
                    'tags_from_definition': [['discount'], ['vip']],
                },
                'some_zone': {'tags_from_definition': [['cargo_van']]},
            },
            CANDIDATES_TOPIC_RELATIONS,
            {'candidates', 'subventions'},
            False,
            1,
            id='has non-related tag only in one tags array',
        ),
    ],
)
async def test_tags_topics_validation(
        web_context,
        mockserver,
        new_value,
        topic_relations,
        topics_set,
        is_ok,
        times_called,
):
    @mockserver.json_handler('/tags/v1/topics_relations')
    def mock_tags_topics_relations(request):
        assert set(request.json['topics']) == topics_set
        return mockserver.make_response(json=topic_relations, status=200)

    config_with_value = common.get_config_with_value(
        TAGS_DEFAULT_VALUE, TAGS_SCHEMA,
    )
    if is_ok:
        await config_with_value.validate(new_value, {}, web_context)
    else:
        with pytest.raises(config_models.ValidationError):
            await config_with_value.validate(new_value, {}, web_context)
    assert mock_tags_topics_relations.times_called == times_called
