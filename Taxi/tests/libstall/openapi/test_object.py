import pytest

from libstall import oa


@pytest.mark.parametrize(
    'body,errors',
    [
        (
            {'f_obj': {}},
            [],
        ),
        (
            {'f_obj': []},
            [
                {
                    'message': "[] is not of type 'object'",
                    'path': 'body.f_obj',
                }
            ],
        ),
        (
            {'f_obj': None},
            [
                {
                    'message': "None is not of type 'object'",
                    'path': 'body.f_obj',
                }
            ],
        ),
        (
            {'f_obj_null': None},
            [],
        ),
        (
            {'f_obj_minmax': {'a': 1}},
            [],
        ),
        (
            {'f_obj_minmax': {}},
            [
                {
                    'message': '{} does not have enough properties',
                    'path': 'body.f_obj_minmax',
                }
            ],
        ),
        (
            {'f_obj_minmax': {'a': 1, 'b': 2, 'c': 3, 'd': 4}},
            [
                {
                    'message': "{'a': 1, 'b': 2, 'c': 3, 'd': 4} "
                               "has too many properties",
                    'path': 'body.f_obj_minmax',
                }
            ],
        ),
        (
            {'f_obj_required': {'a': 1, 'b': 2}},
            [],
        ),
        (
            {'f_obj_required': {'b': 2}},
            [
                {
                    'message': "'a' is a required property",
                    'path': 'body.f_obj_required',
                }
            ],
        ),
        (
            {'f_obj_required_null': None},
            [],
        ),
        (
            {'f_obj_required_null': {'b': 2}},
            [
                {
                    'message': "'a' is a required property",
                    'path': 'body.f_obj_required_null',
                }
            ],
        ),
        (
            {'f_obj_disable_extra_props': {'a': 1, 'b': 2, 'c': 3}},
            [
                {
                    'message': "Additional properties are not allowed "
                               "('c' was unexpected)",
                    'path': 'body.f_obj_disable_extra_props',
                }
            ],
        ),
        (
            {
                'f_obj_hardcore': {
                    'a': 300,
                    'b': 'xyzx',
                    'c': {
                        'ca': 300,
                        'cb': '1970-01-01T23:59:59Z',
                        'cc': [
                            {
                                'cca': 'OK',
                            }
                        ],
                    }
                }
            },
            [],
        ),
        (
            {
                'f_obj_hardcore': {
                    'a': 299,
                    'b': 'xyz',
                    'c': {
                        'ca': 301,
                        'cb': '1970-01-01',
                        'cc': [
                            {
                                'cca': 'OK',
                            },
                            {
                                'cca': 300,
                            },
                        ],
                    }
                }
            },
            [
                {
                    'message': '299 is less than the minimum of 300',
                    'path': 'body.f_obj_hardcore.a',
                },
                {
                    'message': "'xyz' does not match '\\\\S{4}'",
                    'path': 'body.f_obj_hardcore.b',
                },
                {
                    'message': '301 is greater than the maximum of 300',
                    'path': 'body.f_obj_hardcore.c.ca',
                },
                {
                    'message': "'1970-01-01' is not a 'date-time'",
                    'path': 'body.f_obj_hardcore.c.cb',
                },
                {
                    'message': "300 is not of type 'string'",
                    'path': 'body.f_obj_hardcore.c.cc.1.cca',
                },
                {
                    'message': "300 is not one of ['OK']",
                    'path': 'body.f_obj_hardcore.c.cc.1.cca',
                },
            ]
        ),
    ]
)
def test_object(tap, spec, body, errors):
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
