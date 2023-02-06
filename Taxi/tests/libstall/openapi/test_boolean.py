import pytest

from libstall import oa


@pytest.mark.parametrize(
    'body,errors',
    [
        (
            {'f_bool': True},
            [],
        ),
        (
            {'f_bool': 'True'},
            [
                {
                    'message': "'True' is not of type 'boolean'",
                    'path': 'body.f_bool',
                }
            ],
        ),
        (
            {'f_bool': None},
            [
                {
                    'message': "None is not of type 'boolean'",
                    'path': 'body.f_bool',
                }
            ],
        ),
        (
            {'f_bool_null': None},
            [],
        ),
    ]
)
def test_boolean(tap, spec, body, errors):
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
