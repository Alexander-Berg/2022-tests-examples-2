import random

import pytest

from libstall import oa


@pytest.mark.parametrize(
    'body,errors',
    [
        (
            {'f_num': 300},
            [],
        ),
        (
            {'f_num': 300.300},
            [],
        ),
        (
            {'f_num': '300'},
            [
                {
                    'message': "'300' is not of type 'number'",
                    'path': 'body.f_num',
                }
            ],
        ),
        (
            {'f_num': None},
            [
                {
                    'message': "None is not of type 'number'",
                    'path': 'body.f_num',
                }
            ],
        ),
        (
            {'f_num_null': None},
            [],
        ),
        (
            {'f_num_minmax': 2},
            [],
        ),
        (
            {'f_num_minmax': 0},
            [
                {
                    'message': '0 is less than the minimum of 1',
                    'path': 'body.f_num_minmax',
                }
            ],
        ),
        (
            {'f_num_minmax': 4},
            [
                {
                    'message': '4 is greater than the maximum of 3',
                    'path': 'body.f_num_minmax',
                }
            ],
        ),
        (
            {'f_num_enum': random.choice([1, 2])},
            [],
        ),
        (
            {'f_num_enum': 300},
            [
                {
                    'message': '300 is not one of [1, 2]',
                    'path': 'body.f_num_enum',
                }
            ],
        ),
    ]
)
def test_number(tap, spec, body, errors):
    with tap.plan(1):
        try:
            spec.validate_request(
                '/pets',
                'post',
                content_type='application/json',
                params={
                    'header': {
                        'Authorization': 'Token 300',
                        'X-Yandex-ID': '300',
                    },
                },
                body=body,
            )
        except oa.ErValidation as exc:
            tap.eq(exc.errors, errors, f'есть ошибки: {body}')
        else:
            tap.eq(errors, [], f'нет ошибок: {body}')
