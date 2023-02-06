# pylint: disable=protected-access,not-callable

import pathlib
import random

import pytest

from libstall import oa


@pytest.mark.parametrize(
    'path',
    [
        'tests/openapi/data/petstore.yaml',
        'tests/openapi/data/ok_spec.yaml',
    ]
)
def validate_ok_spec(tap, path):
    with tap.plan(1, 'валидируем норм спеки'):
        spec = oa.Spec.from_file(pathlib.Path(path).absolute(), validate=True)
        tap.ok(spec, 'норм спека')


@pytest.mark.parametrize(
    'path',
    [
        'tests/openapi/data/er_spec_broken_local_ref.yaml',
        'tests/openapi/data/er_spec_broken_file_ref.yaml',
        'tests/openapi/data/er_spec_no_paths.yaml',
        'tests/openapi/data/er_spec_no_responses.yaml',
    ]
)
def test_er_spec(tap, path):
    with tap.plan(1, 'валидируем плохие спеки'):
        with tap.raises(oa.ErSpec, 'плохая спека'):
            oa.Spec.from_file(pathlib.Path(path).absolute(), validate=True)


def test_find_path(tap):
    with tap.plan(5, 'поиск куска спеки по path'):
        spec = oa.Spec(
            {
                'paths': {
                    '/': {},
                    '/hello/': {},
                    '/hello/world': {},
                    '/hello/world/{id}': {},
                }
            },
            rel_path='doc/api/v1.yaml',
            validate=False,
        )

        tap.eq(spec._find_path('/api/v1/'), '/', '/')
        tap.eq(spec._find_path('/api/v1/hello/'), '/hello/', '/hello/')
        tap.eq(
            spec._find_path('/api/v1/hello/world'),
            '/hello/world',
            '/hello/world',
        )

        with tap.raises(oa.ErPath, 'шаблоны не поддерживаем'):
            spec._find_path('/hello/world/300')

        with tap.raises(oa.ErPath, 'нет такого пути'):
            spec._find_path('/foo/bar/')


def test_spec_path(tap, uuid):
    with tap.plan(3, 'в спеке задан только путь'):
        spec = oa.Spec(
            {
                'paths': {
                    '/pets': {},
                },
            },
            validate=False,
        )

        tap.eq(
            spec.validator,
            {
                '/pets': {},
            },
            'минимально возможная спека: любые запросы/ответы на /pets'
        )

        validated_req = spec.validate_request(
            '/pets',
            random.choice(['get', 'post']),
            content_type=uuid(),
            body={uuid(): uuid()},
            params={'headers': {uuid(): uuid()}},
        )
        tap.ok(validated_req, 'любой запрос на /pets')

        validated_res = spec.validate_response(
            '/pets',
            random.choice(['get', 'post']),
            random.choice([200, '300', 400]),
            content_type=uuid(),
            body={uuid(): uuid()},
            params={'headers': {uuid(): uuid()}},
        )
        tap.ok(validated_res, 'любой ответ на /pets')


def test_spec_path_method(tap, uuid):
    with tap.plan(3, 'в спеке задан путь и метод'):
        spec = oa.Spec(
            {
                'paths': {
                    '/pets': {
                        'post': {
                            'responses': {
                                '200': {
                                    'description': 'успех',
                                },
                                '500': {
                                    'description': 'не успех',
                                },
                            },
                        },
                    },
                },
            },
            validate=False,
        )

        tap.eq(
            spec.validator,
            {
                '/pets': {
                    'post': {
                        'request': {},
                        'response': {
                            '200': {},
                            '500': {},
                        },
                    },
                },
            },
            'запросы/ответы на /pets только постом',
        )

        validated_req = spec.validate_request(
            '/pets',
            'post',
            content_type=uuid(),
            body={uuid(): uuid()},
            params={'headers': {uuid(): uuid()}},
        )
        tap.ok(validated_req, 'запрос на /pets постом')

        validated_res = spec.validate_response(
            '/pets',
            'post',
            random.choice([200, 500]),
            content_type=uuid(),
            body={uuid(): uuid()},
            params={'headers': {uuid(): uuid()}},
        )
        tap.ok(validated_res, 'ответ на /pets постом')
