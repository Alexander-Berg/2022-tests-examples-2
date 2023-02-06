import pytest

from swaggen import exceptions
from swaggen import settings
from swaggen import tracing
from swaggen.validation import fields
from swaggen.validation import schemas


@pytest.fixture(name='minimal_swagger_schema')
def _minimal_swagger_schema():
    def getter():
        return tracing.Dict(
            {
                'swagger': '2.0',
                'info': {'title': 'Title', 'version': '0.0.1a0'},
                'paths': {},
            },
            'api.yaml',
        )

    return getter


@pytest.mark.parametrize(
    'update, error, text',
    (
        ({}, None, None),
        (
            {'aaa': 'bbb'},
            exceptions.SwaggenError,
            'In file api.yaml at root: got extra fields: aaa',
        ),
    ),
)
def test_minimal_swagger_schema(minimal_swagger_schema, update, error, text):
    data = minimal_swagger_schema()
    data.update(update)
    if error:
        with pytest.raises(error) as exc_info:
            schemas.check_api_schema(data)
        assert exc_info.value.args == (text,)
    else:
        schemas.check_api_schema(data)


@pytest.mark.parametrize(
    'value, error, text',
    (
        (
            {},
            exceptions.SwaggenError,
            'In file a.yaml at root: enum must be an array',
        ),
        (
            [],
            exceptions.SwaggenError,
            'In file a.yaml at enum: can not be empty',
        ),
        ([0, 1, 2], None, None),
        (
            [tracing.List([], 'a.yaml', ()), tracing.List([1], 'a.yaml', ())],
            None,
            None,
        ),
        (
            [tracing.List([], 'a.yaml', ()), tracing.List([], 'a.yaml', ())],
            exceptions.SwaggenError,
            'In file a.yaml at enum: '
            'duplicate value at index 1 with value at 0',
        ),
        (
            [
                tracing.Dict({'a': 1, 'b': 1}, 'a.yaml'),
                tracing.Dict({'b': 1, 'a': 1}, 'a.yaml'),
            ],
            exceptions.SwaggenError,
            'In file a.yaml at enum: '
            'duplicate value at index 1 with value at 0',
        ),
        (
            [
                tracing.Dict({'a': 1, 'b': 1}, 'a.yaml'),
                tracing.Dict({'b': 1, 'c ': 1}, 'a.yaml'),
            ],
            None,
            None,
        ),
    ),
)
def test_check_enum(value, error, text):
    data = tracing.Dict({'enum': value}, 'a.yaml')
    if error:
        with pytest.raises(error) as exc_info:
            fields.check_enum(data, 'enum', settings.SWAGGER_SETTINGS)
        assert exc_info.value.args == (text,)
    else:
        fields.check_enum(data, 'enum', settings.SWAGGER_SETTINGS)


@pytest.mark.parametrize(
    'value, error, text',
    (
        ('a/b/#/d/c', None, None),
        ('#/d/c', None, None),
        ('#/aaa', None, None),
        ('bbbb#/aaa', None, None),
        (
            'bbbb#/',
            exceptions.SwaggenError,
            'In file a.yaml at $ref: '
            'invalid value bbbb#/, must match [a/b/c]#/d/e/f',
        ),
        (
            'bbbbb',
            exceptions.SwaggenError,
            'In file a.yaml at $ref: '
            'invalid value bbbbb, must match [a/b/c]#/d/e/f',
        ),
        (
            'b#a',
            exceptions.SwaggenError,
            'In file a.yaml at $ref: '
            'invalid value b#a, must match [a/b/c]#/d/e/f',
        ),
    ),
)
def test_check_ref(value, error, text):
    data = tracing.Dict({'$ref': value}, 'a.yaml')
    if error:
        with pytest.raises(error) as exc_info:
            fields.check_ref(data, '$ref', settings.SWAGGER_SETTINGS)
        assert exc_info.value.args == (text,)
    else:
        fields.check_ref(data, '$ref', settings.SWAGGER_SETTINGS)


@pytest.mark.parametrize(
    'data',
    [
        {},
        {'swagger': '2.0'},
        {'swagger': '1.0'},
        {'swagger': '2.0', 'info': {}},
        {'swagger': '2.0', 'info': {'title': 'Title', 'version': '0.0.1a0'}},
    ],
)
def test_not_met_minimal_requirements(data):
    with pytest.raises(exceptions.SwaggenError):
        schemas.check_api_schema(tracing.Dict(data, 'a.yaml'))


def test_schema(minimal_swagger_schema):
    data = minimal_swagger_schema()
    data.update(
        {
            'info': {
                'title': 'info title',
                'description': 'info description',
                'termsOfService': 'at your own risk',
                'contact': {
                    'name': 'seanchaidh',
                    'url': 'http://seanchaidh.haze.yandex.net:12345/',
                    'email': 'seanchaidh@yandex-team.ru',
                },
                'license': {'name': 'WTFPL', 'url': 'http://www.wtfpl.net'},
                'version': '0.0.1a0',
            },
            'basePath': '/v1',
            'schemes': ['http'],
            'consumes': ['application/json'],
            'produces': ['application/xml'],
            'definitions': {
                'Pet': {
                    'title': 'Pet title',
                    'description': 'Extensive pet entity schema',
                    'type': 'string',
                },
                'PetClone': {'$ref': '#/definitions/Pet'},
                'PetCloneClone': {'$ref': '#/definitions/PetClone'},
                'MyPet': {
                    'type': 'object',
                    'properties': {'friend': {'$ref': '#/definitions/Pet'}},
                },
                'RoboPet': {
                    'allOf': [
                        {'type': 'integer', 'maximum': 100},
                        {'type': 'integer', 'minimum': 1},
                    ],
                    'externalDocs': {
                        'description': 'zabxab',
                        'url': 'docs url so?',
                    },
                    'example': 'example',
                },
            },
            'parameters': {
                'userdataParam': {
                    'name': 'userdata',
                    'in': 'query',
                    'description': 'some user data',
                    'required': True,
                    'type': 'integer',
                },
                'BodyParamSchema': {
                    'name': 'common-body-param',
                    'in': 'body',
                    'schema': {'type': 'integer'},
                },
                'BodyParamRef': {
                    'name': 'body-param-ref',
                    'in': 'body',
                    'schema': {'$ref': '#/definitions/Pet'},
                },
                'Hugo': {
                    'name': 'Hugo',
                    'in': 'query',
                    'description': 'this is hugo',
                    'required': False,
                    'type': 'integer',
                    'default': 0,
                    'maximum': 666,
                    'exclusiveMaximum': True,
                    'minimum': -666,
                    'exclusiveMinimum': True,
                    'enum': [1, 2, '3'],
                },
            },
            'responses': {
                'notFound': {
                    'description': 'hoho',
                    'schema': {'type': 'integer'},
                    'headers': {
                        'JaJaNumber': {
                            'description': 'jaja',
                            'type': 'integer',
                            'format': 'int64',
                            'maximum': 666,
                            'exclusiveMaximum': True,
                            'minimum': -666,
                            'exclusiveMinimum': True,
                            'enum': [1, 2, '3'],
                        },
                    },
                    'examples': {'application/json': {'is it real': 'pope'}},
                },
                'AllOk': {
                    'description': 'all-ok',
                    'schema': {'$ref': '#/definitions/Pet'},
                },
            },
            'tags': [
                {
                    'name': 'tag name',
                    'description': 'tag descr',
                    'externalDocs': {
                        'description': 'tag docs descr',
                        'url': 'tag docs url',
                    },
                },
            ],
            'externalDocs': {
                'description': 'root docs descr',
                'url': 'root docs url',
            },
            'paths': {
                '/pets': {
                    'get': {
                        'description': 'Returns pets based on ID',
                        'summary': 'Find pets by ID',
                        'operationId': 'getPetsById',
                        'responses': {
                            200: {
                                'description': 'pet response',
                                'schema': {
                                    'type': 'array',
                                    'items': {'$ref': '#/definitions/Pet'},
                                },
                            },
                            404: {'$ref': '#/responses/notFound'},
                            500: {
                                'description': 'funny internal error',
                                'schema': {
                                    'type': 'string',
                                    'format': 'binary',
                                },
                            },
                        },
                    },
                    'parameters': [
                        {
                            'name': 'username',
                            'in': 'header',
                            'description': 'username to fetch',
                            'required': False,
                            'type': 'string',
                        },
                        {'$ref': '#/parameters/userdataParam'},
                    ],
                },
            },
        },
    )
    schemas.check_api_schema(data)


def test_schema_required_with_default(minimal_swagger_schema):
    data = minimal_swagger_schema()
    data.update(
        {
            'definitions': {
                'Pet': {
                    'title': 'Pet title',
                    'description': 'Pet description',
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string', 'default': 'Rex'},
                    },
                    'required': ['name'],
                },
            },
        },
    )

    with pytest.raises(exceptions.SwaggenError) as exc_info:
        schemas.check_api_schema(data)

    assert exc_info.value.args == (
        'In file api.yaml at definitions.Pet.properties.name.default: '
        'required property can not have default value',
    )


def test_response_header_default(minimal_swagger_schema):
    data = minimal_swagger_schema()
    data['paths'] = {
        '/pets': {
            'get': {
                'description': 'Returns pets based on ID',
                'summary': 'Find pets by ID',
                'operationId': 'getPetsById',
                'responses': {
                    200: {
                        'description': 'pet response',
                        'headers': {
                            'BACBAC': {'type': 'string', 'default': 'abacaba'},
                        },
                    },
                },
            },
        },
    }
    with pytest.raises(exceptions.SwaggenError) as exc_info:
        schemas.check_api_schema(data)

    assert exc_info.value.args == (
        'In file api.yaml at paths./pets.get.responses.200.headers.BACBAC: '
        'got extra fields: default',
    )
