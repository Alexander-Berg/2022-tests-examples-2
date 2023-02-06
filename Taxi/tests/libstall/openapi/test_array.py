import pytest

from libstall import oa


@pytest.mark.parametrize(
    'body,errors',
    [
        (
            {'f_arr': []},
            [],
        ),
        (
            {'f_arr': 300},
            [
                {
                    'message': "300 is not of type 'array'",
                    'path': 'body.f_arr',
                }
            ],
        ),
        (
            {'f_arr': None},
            [
                {
                    'message': "None is not of type 'array'",
                    'path': 'body.f_arr',
                }
            ],
        ),
        (
            {'f_arr_null': None},
            [],
        ),
        (
            {'f_arr_minmax': [1, 2, 3]},
            [],
        ),
        (
            {'f_arr_minmax': []},
            [
                {
                    'message': '[] is too short',
                    'path': 'body.f_arr_minmax',
                }
            ],
        ),
        (
            {'f_arr_minmax': [1, 2, 3, 4]},
            [
                {
                    'message': '[1, 2, 3, 4] is too long',
                    'path': 'body.f_arr_minmax',
                }
            ],
        ),
        (
            {'f_arr_minmax_null': None},
            [],
        ),
        (
            {
                'f_arr_unique': [{'a': 1}, {'a': 2}, {'a': 3}]
            },
            [],
        ),
        (
            {
                'f_arr_unique': [{'a': 1}, {'a': 1}, {'a': 2}]
            },
            [
                {
                    'message': "[{'a': 1}, {'a': 1}, {'a': 2}] "
                               "has non-unique elements",
                    'path': 'body.f_arr_unique',
                }
            ]
        ),
        (
            {
                'f_arr_hardcore': [
                    300,
                    'xyz',
                    {
                        'a': 1,
                        'b': 1,
                        'c': {
                            'ca': ['x', 'y'],
                        }
                    }
                ]
            },
            [],
        ),
        (
            {
                'f_arr_hardcore': [
                    299,
                    '',
                    {
                        'a': 1,
                        'b': 1,
                        'c': {
                            'ca': [1, 2, 3],
                        }
                    },
                    {
                        'a': 1,
                        'b': 1,
                        'c': {
                            'ca': ['x', 'y'],
                        }
                    },
                ]
            },
            [
                {
                    'message': '299 is not valid '
                               'under any of the given schemas',
                    'path': 'body.f_arr_hardcore.0'
                },
                {
                    'message': "'' is not valid under any of the given schemas",
                    'path': 'body.f_arr_hardcore.1',
                },
                {
                    'message': "{'a': 1, 'b': 1, 'c': {'ca': [1, 2, 3]}} "
                               "is not valid under any of the given schemas",
                    'path': 'body.f_arr_hardcore.2',
                },
            ],
        ),
    ]
)
def test_array(tap, spec, body, errors):
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
