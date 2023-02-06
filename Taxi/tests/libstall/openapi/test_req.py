import pytest
from libstall import oa


def test_validated_request(tap, spec):
    with tap.plan(2, 'норм реквест'):
        result = spec.validate_request(
            '/pets',
            'post',
            content_type='application/json',
            params={
                'header': {
                    'Authorization': 'Token 300',
                    'X-Yandex-ID': '300',
                },
            },
            body={'f_num': 1},
        )

        tap.eq(
            result.header,
            {
                'Authorization': 'Token 300',
                'X-Yandex-ID': '300',
            },
            'есть хедеры',
        )
        tap.ok(
            result.body,
            {'f_num': 1},
            'боди на месте',
        )


def test_validate_additional(tap, spec):
    with tap.plan(5, 'реквест с дополнительной шнягой'):
        result = spec.validate_request(
            '/work/{work_id}',
            'post',
            content_type='application/json',
            params={
                'header': {
                    'header_id': 'param',
                },
                'path': {
                    'work_id': 'param',
                },
                'query': {
                    'query_id': 'param',
                },
                'cookie': {
                    'cookie_id': 'param',
                },
            },
            body={'f_num': 1},
        )
        tap.eq(result.header, {'header_id': 'param'}, 'хедер на месте')
        tap.eq(result.cookie, {'cookie_id': 'param'}, 'кука на месте')
        tap.eq(result.query, {'query_id': 'param'}, 'квери на месте')
        tap.eq(result.path, {'work_id': 'param'}, 'inpath на месте')
        tap.ok(result.body, {'f_num': 1}, 'боди на месте')


def test_validate_broken_inpath(tap, spec):
    with tap.plan(1, 'сломанный inpath'):
        with tap.raises(oa.ErValidation, 'некорректный inpath'):
            spec.validate_request(
                '/work/{work_id}',
                'post',
                content_type='application/json',
                params={
                    'path': {
                        'work_id': 'notparam',
                    }
                },
                body={'f_num': 1},
            )


def test_validate_broken_query(tap, spec):
    with tap.plan(1, 'сломанный query'):
        with tap.raises(oa.ErValidation, 'некорректный query'):
            spec.validate_request(
                '/work/{work_id}',
                'post',
                content_type='application/json',
                params={
                    'path': {
                        'work_id': 'param',
                    },
                    'query': {
                        'query_id': 'notparam',
                    },
                },
                body={'f_num': 1},
            )


def test_validate_broken_cookie(tap, spec):
    with tap.plan(1, 'сломанный cookie'):
        with tap.raises(oa.ErValidation, 'некорректный cookie'):
            spec.validate_request(
                '/work/{work_id}',
                'post',
                content_type='application/json',
                params={
                    'path': {
                        'work_id': 'param',
                    },
                    'cookie': {
                        'cookie_id': 'notparam',
                    },
                },
                body={'f_num': 1},
            )


@pytest.mark.skip(reason='fix after arcadia')
async def test_er_path(tap, spec, uuid, http_api):
    with tap.plan(3, 'тестим кривые пути'):
        with tap.raises(oa.ErPath, 'путь в спеке не найден'):
            spec.validate_request(
                uuid(),
                'post',
                content_type='application/json',
                params={'header': {'Authorization': 'Token 300'}},
                body={'f_num': 1},
            )

        t = await http_api()
        res = await t.client.request('get', 'api/dev/ping/')
        tap.eq(res.status, 404, 'путь не найден')
        res = await t.client.request('get', 'api/dev/dev/ping')
        tap.eq(res.status, 404, 'путь не найден')


@pytest.mark.parametrize('http_method', ['get', 'head', 'put'])
def test_er_method(tap, spec, http_method):
    with tap.plan(1):
        with tap.raises(
                oa.ErMethod,
                f'метод {http_method} не определен в path',
        ):
            spec.validate_request(
                '/pets',
                http_method,
                content_type='application/json',
                params={'header': {'Authorization': 'Token 300'}},
                body={'f_num': 1},
            )


def test_er_content_type(tap, spec):
    with tap.plan(1):
        with tap.raises(oa.ErContentType, 'некорректный content-type'):
            spec.validate_request(
                '/pets',
                'post',
                content_type='text/xml',
                params={'header': {'Authorization': 'Token 300'}},
                body={'f_num': 1},
            )


# pylint: disable=invalid-name
def test_er_validation_headers_required(tap, spec):
    with tap.plan(3, 'проверяем обязательный хедер'):
        try:
            spec.validate_request(
                '/pets',
                'post',
                content_type='application/json',
                body={'f_num': 1},
            )
        except oa.ErValidation as exc:
            tap.eq(len(exc.errors), 1, 'есть одна ошибка')
            tap.eq(
                exc.errors[0]['message'],
                "'Authorization' is a required property",
                'сообщение для людей',
            )
            tap.eq(exc.errors[0]['path'], 'header', 'путь до ошибки')


# pylint: disable=invalid-name
def test_er_validation_headers_not_required(tap, spec):
    with tap.plan(3, 'проверяем опциональный хедер'):
        try:
            spec.validate_request(
                '/pets',
                'post',
                content_type='application/json',
                params={
                    'header': {
                        'Authorization': 'Token 300',
                        'X-Yandex-ID': 'hello',
                    },
                },
                body={'f_num': 1},
            )
        except oa.ErValidation as exc:
            tap.eq(len(exc.errors), 1, 'есть одна ошибка')
            tap.like(
                exc.errors[0]['message'],
                "'hello' does not match",
                'сообщение для людей',
            )
            tap.eq(
                exc.errors[0]['path'],
                'header.X-Yandex-ID',
                'путь до ошибки',
            )
