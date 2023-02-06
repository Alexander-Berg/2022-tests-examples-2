# pylint: disable=line-too-long
# flake8: noqa: E501

import typing

import pytest

from taxi_exp.lib import predicates
from taxi_exp.util import predicate_helpers


TAGS_TRANSFORM_RULES = {
    '__default__': '__same_name__',
    'yandex_phone_id': 'phone_id',
    'taxi_phone_id': 'phone_id',
}

TAGS = {
    'yandex_phone_id': predicates.FileTag(
        'yandex_phone_id', 'a63410a685d442e485768702c9ad32fe', 'string', 1,
    ),
    'taxi_phone_id': predicates.FileTag(
        'taxi_phone_id', 'ad052d476b8045519207b1098b1c555c', 'string', 2,
    ),
}

PARTIAL_TAGS = {
    'yandex_phone_id': predicates.FileTag(
        'yandex_phone_id', 'a63410a685d442e485768702c9ad32fe', 'string', 1,
    ),
}


class Case(typing.NamedTuple):
    predicate: dict
    tags: typing.Optional[dict]
    expected_predicate: dict
    exception: typing.Optional[typing.Any]


@pytest.mark.parametrize(
    'predicate,tags,expected_predicate,exception',
    [
        pytest.param(
            *Case(
                predicate={
                    'type': 'user_has',
                    'init': {'tag': 'yandex_phone_id'},
                },
                tags=TAGS,
                expected_predicate={
                    'type': 'in_file',
                    'init': {
                        'file': 'a63410a685d442e485768702c9ad32fe',
                        'arg_name': 'phone_id',
                        'set_elem_type': 'string',
                    },
                },
                exception=None,
            ),
            id='simple_one_transform',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'all_of',  # 1
                    'init': {
                        'predicates': [
                            {
                                'type': 'all_of',  # 2
                                'init': {
                                    'predicates': [
                                        {
                                            'type': 'all_of',  # 3
                                            'init': {
                                                'predicates': [
                                                    {
                                                        'type': 'all_of',  # 4
                                                        'init': {
                                                            'predicates': [
                                                                {
                                                                    'type': 'user_has',
                                                                    'init': {
                                                                        'tag': 'taxi_phone_id',
                                                                    },
                                                                },
                                                                {
                                                                    'type': (
                                                                        'true'
                                                                    ),
                                                                },
                                                            ],
                                                        },
                                                    },
                                                    {'type': 'false'},
                                                ],
                                            },
                                        },
                                        {'type': 'false'},
                                    ],
                                },
                            },
                            {'type': 'false'},
                        ],
                    },
                },
                tags=TAGS,
                expected_predicate={
                    'type': 'all_of',  # 1
                    'init': {
                        'predicates': [
                            {
                                'type': 'all_of',  # 2
                                'init': {
                                    'predicates': [
                                        {
                                            'type': 'all_of',  # 3
                                            'init': {
                                                'predicates': [
                                                    {
                                                        'type': 'all_of',  # 4
                                                        'init': {
                                                            'predicates': [
                                                                {
                                                                    'type': 'in_file',
                                                                    'init': {
                                                                        'file': 'ad052d476b8045519207b1098b1c555c',
                                                                        'arg_name': 'phone_id',
                                                                        'set_elem_type': 'string',
                                                                    },
                                                                },
                                                                {
                                                                    'type': (
                                                                        'true'
                                                                    ),
                                                                },
                                                            ],
                                                        },
                                                    },
                                                    {'type': 'false'},
                                                ],
                                            },
                                        },
                                        {'type': 'false'},
                                    ],
                                },
                            },
                            {'type': 'false'},
                        ],
                    },
                },
                exception=None,
            ),
            id='deep_one_transfrom',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'all_of',  # 1
                    'init': {
                        'predicates': [
                            {
                                'type': 'all_of',  # 2
                                'init': {
                                    'predicates': [
                                        {
                                            'type': 'all_of',  # 3
                                            'init': {
                                                'predicates': [
                                                    {
                                                        'type': 'any_of',  # 4
                                                        'init': {
                                                            'predicates': [
                                                                {
                                                                    'type': 'user_has',
                                                                    'init': {
                                                                        'tag': 'taxi_phone_id',
                                                                    },
                                                                },
                                                                {
                                                                    'type': (
                                                                        'true'
                                                                    ),
                                                                },
                                                            ],
                                                        },
                                                    },
                                                    {
                                                        'type': 'user_has',
                                                        'init': {
                                                            'tag': 'other_tag',
                                                        },
                                                    },
                                                ],
                                            },
                                        },
                                        {'type': 'false'},
                                    ],
                                },
                            },
                            {
                                'type': 'user_has',
                                'init': {'tag': 'yandex_phone_id'},
                            },
                        ],
                    },
                },
                tags={
                    'yandex_phone_id': predicates.FileTag(
                        'yandex_phone_id',
                        'a63410a685d442e485768702c9ad32fe',
                        'string',
                        1,
                    ),
                    'taxi_phone_id': predicates.FileTag(
                        'taxi_phone_id',
                        'ad052d476b8045519207b1098b1c555c',
                        'string',
                        2,
                    ),
                    'other_tag': predicates.FileTag(
                        'other_tag',
                        '5d2d0a60189c4d89949d357786214ccc',
                        'string',
                        2,
                    ),
                },
                expected_predicate={
                    'type': 'all_of',  # 1
                    'init': {
                        'predicates': [
                            {
                                'type': 'all_of',  # 2
                                'init': {
                                    'predicates': [
                                        {
                                            'type': 'all_of',  # 3
                                            'init': {
                                                'predicates': [
                                                    {
                                                        'type': 'any_of',  # 4
                                                        'init': {
                                                            'predicates': [
                                                                {
                                                                    'type': 'in_file',
                                                                    'init': {
                                                                        'file': 'ad052d476b8045519207b1098b1c555c',
                                                                        'arg_name': 'phone_id',
                                                                        'set_elem_type': 'string',
                                                                    },
                                                                },
                                                                {
                                                                    'type': (
                                                                        'true'
                                                                    ),
                                                                },
                                                            ],
                                                        },
                                                    },
                                                    {
                                                        'type': 'in_file',
                                                        'init': {
                                                            'file': '5d2d0a60189c4d89949d357786214ccc',
                                                            'arg_name': (
                                                                'other_tag'
                                                            ),  #
                                                            'set_elem_type': (
                                                                'string'
                                                            ),
                                                        },
                                                    },
                                                ],
                                            },
                                        },
                                        {'type': 'false'},
                                    ],
                                },
                            },
                            {
                                'type': 'in_file',
                                'init': {
                                    'file': 'a63410a685d442e485768702c9ad32fe',
                                    'arg_name': 'phone_id',
                                    'set_elem_type': 'string',
                                },
                            },
                        ],
                    },
                },
                exception=None,
            ),
            id='multi_transform',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'user_has',
                    'init': {'tag': 'yandex_phone_id'},
                },
                tags=None,
                expected_predicate={},
                exception=predicates.TagError,
            ),
            id='without_tags',
        ),
        pytest.param(
            *Case(
                predicate={
                    'type': 'user_has',
                    'init': {'tag': 'taxi_phone_id'},
                },
                tags=PARTIAL_TAGS,
                expected_predicate={},
                exception=predicates.TagError,
            ),
            id='partial_without_tags',
        ),
    ],
)
def test_transform_predicates(predicate, tags, expected_predicate, exception):
    if exception is None:
        transformed_predicate = predicate_helpers.replace_tags(
            predicate, tags, TAGS_TRANSFORM_RULES, {},
        )
        assert transformed_predicate == expected_predicate
    else:
        with pytest.raises(exception):
            predicate_helpers.replace_tags(
                predicate, tags, TAGS_TRANSFORM_RULES, {},
            )
