import typing

import pytest

from taxi_exp.util import predicate_helpers


class Case(typing.NamedTuple):
    predicates: typing.List[typing.Dict]
    answer: predicate_helpers.FilesData


@pytest.mark.parametrize(
    'predicates,answer',
    [
        Case(
            predicates=[
                {
                    'type': 'in_file',
                    'init': {
                        'file': 'aaaaaa',
                        'set_elem_type': 'string',
                        'arg_name': 'phone_id',
                    },
                },
            ],
            answer=predicate_helpers.FilesData(
                file_ids=['aaaaaa'], file_types=['string'], file_tags=[],
            ),
        ),
        Case(
            predicates=[
                {
                    'type': 'any_of',
                    'init': {
                        'predicates': [
                            {
                                'type': 'in_file',
                                'init': {
                                    'file': 'aaaaaa',
                                    'set_elem_type': 'string',
                                    'arg_name': 'phone_id',
                                },
                            },
                            {
                                'type': 'all_of',
                                'init': {
                                    'predicates': [
                                        {
                                            'type': 'not',
                                            'init': {
                                                'predicate': {
                                                    'type': 'user_has',
                                                    'init': {'tag': 'ttttt'},
                                                },
                                            },
                                        },
                                        {
                                            'type': 'eq',
                                            'init': {
                                                'value': 123,
                                                'type': 'int',
                                                'arg_name': 'count',
                                            },
                                        },
                                        {
                                            'type': 'in_file',
                                            'init': {
                                                'file': 'bbb',
                                                'set_elem_type': 'int',
                                                'arg_name': 'geozone_id',
                                            },
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                },
                {'type': 'user_has', 'init': {'tag': 'yandex_phone_id'}},
            ],
            answer=predicate_helpers.FilesData(
                file_ids=['bbb', 'aaaaaa'],
                file_types=['integer', 'string'],
                file_tags=['yandex_phone_id', 'ttttt'],
            ),
        ),
        Case(
            predicates=[
                {
                    'type': 'any_of',
                    'init': {
                        'predicates': [
                            {
                                'type': 'in_file',
                                'init': {
                                    'file': 'aaaaaa',
                                    'set_elem_type': 'string',
                                    'arg_name': 'phone_id',
                                },
                            },
                            {
                                'type': 'all_of',
                                'init': {
                                    'predicates': [
                                        {
                                            'type': 'not',
                                            'init': {
                                                'predicate': {
                                                    'type': 'user_has',
                                                    'init': {'tag': 'ttttt'},
                                                },
                                            },
                                        },
                                        {
                                            'type': 'eq',
                                            'init': {
                                                'value': 123,
                                                'type': 'int',
                                                'arg_name': 'count',
                                            },
                                        },
                                        {
                                            'type': 'in_file',
                                            'init': {
                                                'file': 'bbb',
                                                'set_elem_type': 'int',
                                                'arg_name': 'geozone_id',
                                            },
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                },
                {'type': 'user_has', 'init': {'tag': 'yandex_phone_id'}},
                {'type': 'user_has', 'init': {'tag': 'yandex_phone_id'}},
                {'type': 'user_has', 'init': {'tag': 'eats_phone_id'}},
            ],
            answer=predicate_helpers.FilesData(
                file_ids=['bbb', 'aaaaaa'],
                file_types=['integer', 'string'],
                file_tags=['ttttt', 'yandex_phone_id', 'eats_phone_id'],
            ),
        ),
    ],
)
def test_extract_files_data(predicates, answer):
    response = predicate_helpers.extract_files_data(predicates)
    assert len(response.file_tags) == len(answer.file_tags)
    assert set(response.file_tags) == set(answer.file_tags)
    assert response.file_ids == answer.file_ids
    assert response.file_types == answer.file_types
