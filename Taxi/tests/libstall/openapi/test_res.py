import pytest

from libstall import oa


def test_validated_response(tap, spec):
    with tap.plan(2, 'норм респонс'):
        result = spec.validate_response(
            '/pets',
            'post',
            200,
            content_type='application/json',
            params={
                'header': {
                    'Authorization': 'Token 300',
                    'X-Yandex-ID': '300',
                },
            },
            body=[
                {'f_num': 300},
                {'f_str': '300'},
            ],
        )

        tap.eq(
            result.header,
            {
                'Authorization': 'Token 300',
                'X-Yandex-ID': '300',
            },
            'есть хедеры',
        )
        tap.eq(
            result.body,
            [
                {'f_num': 300},
                {'f_str': '300'},
            ],
            'боди на месте',
        )


def test_er_path(tap, spec, uuid):
    with tap.plan(1):
        with tap.raises(oa.ErPath, 'путь в спеке не найден'):
            spec.validate_response(
                uuid(),
                'post',
                200,
                content_type='application/json',
                body={'f_num': 300},
            )


@pytest.mark.parametrize('http_method', ['get', 'head', 'put'])
def test_er_method(tap, spec, http_method):
    with tap.plan(1):
        with tap.raises(
                oa.ErMethod,
                f'метод {http_method} не определен в path',
        ):
            spec.validate_response(
                '/pets',
                http_method,
                200,
                content_type='application/json',
                body={'f_num': 300},
            )


@pytest.mark.parametrize('http_status', [201, 404, 502])
def test_er_status(tap, spec, http_status):
    with tap.plan(1):
        with tap.raises(
                oa.ErStatus,
                f'статус {http_status} не определен в path',
        ):
            spec.validate_response(
                '/pets',
                'post',
                http_status,
                content_type='application/json',
                body={'f_num': 300},
            )


def test_er_content_type(tap, spec):
    with tap.plan(1):
        with tap.raises(oa.ErContentType, 'некорректный content-type'):
            spec.validate_response(
                '/pets',
                'post',
                200,
                content_type='text/plain',
                body={'f_num': 300},
            )
