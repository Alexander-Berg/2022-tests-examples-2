import pytest

from libstall import oa


@pytest.mark.parametrize(
    'body,errors',
    [
        (
            {'f_str': 'sosiska'},
            [],
        ),
        (
            {'f_str': 300},
            [
                {
                    'message': "300 is not of type 'string'",
                    'path': 'body.f_str',
                }
            ],
        ),
        (
            {'f_str': None},
            [
                {
                    'message': "None is not of type 'string'",
                    'path': 'body.f_str',
                }
            ],
        ),
        (
            {'f_str_null': None},
            [],
        ),
        (
            {'f_str_minmax': 'xyz'},
            [],
        ),
        (
            {'f_str_minmax': ''},
            [
                {
                    'message': "'' is too short",
                    'path': 'body.f_str_minmax',
                }
            ],
        ),
        (
            {'f_str_minmax': 'xyzxyz'},
            [
                {
                    'message': "'xyzxyz' is too long",
                    'path': 'body.f_str_minmax',
                }
            ],
        ),
        (
            {'f_str_pattern': 'hello world'},
            [],
        ),
        (
            {'f_str_pattern': 'world'},
            [
                {
                    'message': "'world' does not match '^hello \\\\S+$'",
                    'path': 'body.f_str_pattern',
                }
            ],
        ),
        (
            {'f_str_format_datetime': '1970-01-01T23:59:59Z'},
            [],
        ),
        (
            {'f_str_format_datetime': '1970-01-01 23:59:59'},
            [
                {
                    'message': "'1970-01-01 23:59:59' is not a 'date-time'",
                    'path': 'body.f_str_format_datetime',
                }
            ],
        ),
        (
            {'f_str_format_date': '1970-01-01'},
            [],
        ),
        (
            {'f_str_format_date': '1970/01/01'},
            [
                {
                    'message': "'1970/01/01' is not a 'date'",
                    'path': 'body.f_str_format_date',
                }
            ],
        ),
    ]
)
def test_string(tap, spec, body, errors):
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
            tap.eq(errors, exc.errors, f'есть ошибки: {body}')
        else:
            tap.eq(errors, [], f'нет ошибок: {body}')
