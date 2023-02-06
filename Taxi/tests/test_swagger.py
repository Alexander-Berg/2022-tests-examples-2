import pytest

from codegen.swagger import exceptions
from codegen.swagger import schema


@pytest.fixture(name='minimal_schema')
def _minimal_schema():
    def getter():
        return {
            'swagger': '2.0',
            'info': {'title': 'Title', 'version': '0.0.1a0'},
            'paths': {},
        }

    return getter


@pytest.fixture(name='operation_data')
def _operation_data():
    def getter():
        return {
            'tags': ['1', '2', '3'],
            'summary': 'op summary',
            'description': 'op description',
            'externalDocs': {'url': 'exdoc url', 'description': 'exdoc descr'},
            'operationId': '1.1.1.1',
            'consumes': ['application/json'],
            'produces': ['application/json'],
            'parameters': [
                {
                    'name': 'this',
                    'in': 'header',
                    'description': 'this descr',
                    'required': True,
                    'type': 'string',
                    'format': 'byte',
                },
            ],
            'responses': {200: {'description': 'ok resp descr'}},
            'schemes': ['http', 'https'],
            'deprecated': True,
        }

    return getter


def test_minimal_swagger_schema(minimal_schema):
    data = minimal_schema()
    swagger_schema = schema.SwaggerSchema(data)
    assert swagger_schema.swagger == '2.0'
    assert swagger_schema.info.title == 'Title'
    assert swagger_schema.info.version == '0.0.1a0'


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
    with pytest.raises(exceptions.ValidationError):
        schema.SwaggerSchema(data)


def test_schema(minimal_schema):
    # pylint: disable=too-many-statements,protected-access
    data = minimal_schema()
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
                    'readOnly': False,
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
                    'format': 'abracadabra',
                    'allowEmptyValue': True,
                    'collectionFormat': 'pipes',
                    'default': 0,
                    'maximum': 666,
                    'exclusiveMaximum': True,
                    'minimum': -666,
                    'exclusiveMinimum': True,
                    'enum': [1, 2, '3'],
                    'multipleOf': 666,
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
                            'collectionFormat': 'pipes',
                            'default': 0,
                            'maximum': 666,
                            'exclusiveMaximum': True,
                            'minimum': -666,
                            'exclusiveMinimum': True,
                            'enum': [1, 2, '3'],
                            'multipleOf': 666,
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
                                'schema': {'type': 'file'},
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

    swagger = schema.SwaggerSchema(data)

    assert swagger.swagger == '2.0'

    info = swagger.info
    assert info._path == ['info']
    assert info.title == 'info title'
    assert info.version == '0.0.1a0'
    assert info.description == 'info description'
    assert info.terms_of_services == 'at your own risk'
    assert info.contact._path == ['info', 'contact']
    assert info.contact.name == 'seanchaidh'
    assert info.contact.url == 'http://seanchaidh.haze.yandex.net:12345/'
    assert info.contact.email == 'seanchaidh@yandex-team.ru'
    assert info.license._path == ['info', 'license']
    assert info.license.name == 'WTFPL'
    assert info.license.url == 'http://www.wtfpl.net'

    assert swagger.base_path == '/v1'
    assert swagger.schemes == ['http']
    assert swagger.consumes == ['application/json']
    assert swagger.produces == ['application/xml']

    assert swagger.definitions._path == ['definitions']

    pet = swagger.definitions['Pet']
    assert pet._path == ['definitions', 'Pet']
    assert pet.title == 'Pet title'
    assert pet.description == 'Extensive pet entity schema'
    assert pet.type == 'string'

    pet_clone = swagger.definitions['PetClone']
    assert pet_clone._path == ['definitions', 'PetClone']
    assert pet_clone.title == 'Pet title'
    assert pet_clone.description == 'Extensive pet entity schema'
    assert pet_clone.type == 'string'

    pet_clone_clone = swagger.definitions['PetCloneClone']
    assert pet_clone_clone._path == ['definitions', 'PetCloneClone']
    assert pet_clone_clone.title == 'Pet title'
    assert pet_clone_clone.description == 'Extensive pet entity schema'
    assert pet_clone_clone.type == 'string'

    my_pet = swagger.definitions['MyPet']
    assert my_pet._path == ['definitions', 'MyPet']
    assert my_pet.type == 'object'
    friend = my_pet.properties['friend']
    assert friend.type == 'string'
    assert friend.title == 'Pet title'
    assert friend.description == 'Extensive pet entity schema'

    robopet = swagger.definitions['RoboPet']
    assert robopet._path == ['definitions', 'RoboPet']
    assert robopet.all_of[0].type == 'integer'
    assert robopet.all_of[0].maximum == 100
    assert robopet.all_of[0].minimum is None
    assert robopet.all_of[1].type == 'integer'
    assert robopet.all_of[1].maximum is None
    assert robopet.all_of[1].minimum == 1
    assert robopet.external_docs.description == 'zabxab'
    assert robopet.external_docs.url == 'docs url so?'
    assert robopet.example == 'example'

    assert swagger.parameters._path == ['parameters']
    assert swagger.parameters['userdataParam']._path == [
        'parameters',
        'userdataParam',
    ]
    assert swagger.parameters['userdataParam'].name == 'userdata'
    assert swagger.parameters['userdataParam'].in_ == 'query'
    assert swagger.parameters['userdataParam'].description == 'some user data'
    assert swagger.parameters['userdataParam'].required
    assert swagger.parameters['userdataParam'].type == 'integer'

    assert swagger.parameters['BodyParamSchema'].name == 'common-body-param'
    assert swagger.parameters['BodyParamSchema'].in_ == 'body'
    assert swagger.parameters['BodyParamSchema'].schema.type == 'integer'

    assert swagger.parameters['BodyParamRef'].name == 'body-param-ref'
    assert swagger.parameters['BodyParamRef'].in_ == 'body'
    param_schema = swagger.parameters['BodyParamRef'].schema
    assert param_schema.title == 'Pet title'
    assert param_schema.description == 'Extensive pet entity schema'
    assert param_schema.type == 'string'

    hugo = swagger.parameters['Hugo']
    assert hugo.name == 'Hugo'
    assert hugo.in_ == 'query'
    assert hugo.description == 'this is hugo'
    assert not hugo.required
    assert hugo.type == 'integer'
    assert hugo.format == 'abracadabra'
    assert hugo.allow_empty_value
    assert hugo.collection_format == 'pipes'
    assert hugo.default == 0
    assert hugo.maximum == 666
    assert hugo.minimum == -666
    assert hugo.exclusive_minimum
    assert hugo.exclusive_maximum
    assert hugo.enum == [1, 2, '3']
    assert hugo.multiple_of == 666

    assert swagger.responses._path == ['responses']
    not_found = swagger.responses['notFound']
    assert not_found._path == ['responses', 'notFound']
    assert not_found.description == 'hoho'
    assert not_found.schema._path == ['responses', 'notFound', 'schema']
    assert not_found.schema.type == 'integer'
    assert not_found.headers._path == ['responses', 'notFound', 'headers']
    jaja_header = not_found.headers['JaJaNumber']
    assert jaja_header._path == [
        'responses',
        'notFound',
        'headers',
        'JaJaNumber',
    ]
    assert jaja_header.description == 'jaja'
    assert jaja_header.type == 'integer'
    assert jaja_header.format == 'int64'
    assert jaja_header.collection_format == 'pipes'
    assert jaja_header.default == 0
    assert jaja_header.maximum == 666
    assert jaja_header.exclusive_maximum
    assert jaja_header.minimum == -666
    assert jaja_header.exclusive_minimum
    assert jaja_header.enum == [1, 2, '3']
    assert jaja_header.multiple_of == 666
    assert not_found.examples['application/json'] == {'is it real': 'pope'}

    all_ok = swagger.responses['AllOk']
    assert all_ok._path == ['responses', 'AllOk']
    assert all_ok.description == 'all-ok'
    assert all_ok.schema.title == 'Pet title'
    assert all_ok.schema.description == 'Extensive pet entity schema'
    assert all_ok.schema.type == 'string'

    assert swagger.tags._path == ['tags']
    assert swagger.tags[0]._path == ['tags', '0']
    assert swagger.tags[0].name == 'tag name'
    assert swagger.tags[0].description == 'tag descr'
    assert swagger.tags[0].external_docs._path == ['tags', '0', 'externalDocs']
    assert swagger.tags[0].external_docs.description == 'tag docs descr'
    assert swagger.tags[0].external_docs.url == 'tag docs url'

    assert swagger.external_docs._path == ['externalDocs']
    assert swagger.external_docs.description == 'root docs descr'
    assert swagger.external_docs.url == 'root docs url'

    assert swagger.paths._path == ['paths']
    path = swagger.paths['/pets']
    assert path._path == ['paths', '/pets']

    get = swagger.paths['/pets'].get
    assert get._path == ['paths', '/pets', 'get']
    assert get.description == 'Returns pets based on ID'
    assert get.summary == 'Find pets by ID'
    assert get.operation_id == 'getPetsById'
    assert get.responses._path == ['paths', '/pets', 'get', 'responses']
    assert get.responses[200].description == 'pet response'
    assert get.responses[200].schema.type == 'array'
    assert get.responses[200].schema.items.type == 'string'
    assert get.responses[200]._path == [
        'paths',
        '/pets',
        'get',
        'responses',
        '200',
    ]
    assert get.responses[404].description == 'hoho'
    assert get.responses[404]._path == [
        'paths',
        '/pets',
        'get',
        'responses',
        '404',
    ]
    assert get.responses[500].schema.type == 'file'

    assert path.parameters._path == ['paths', '/pets', 'parameters']
    assert path.parameters[0]._path == ['paths', '/pets', 'parameters', '0']
    assert path.parameters[0].name == 'username'
    assert path.parameters[0].in_ == 'header'
    assert path.parameters[0].description == 'username to fetch'
    assert not path.parameters[0].required
    assert path.parameters[0].type == 'string'

    assert path.parameters[1]._path == ['paths', '/pets', 'parameters', '1']
    assert path.parameters[1].name == 'userdata'
    assert path.parameters[1].in_ == 'query'
    assert path.parameters[1].description == 'some user data'
    assert path.parameters[1].required
    assert path.parameters[1].type == 'integer'


def test_operation(operation_data):
    data = operation_data()
    oper = schema.Operation(data, ['root'], None)
    assert oper.tags == ['1', '2', '3']
    assert oper.summary == 'op summary'
    assert oper.description == 'op description'
    assert oper.external_docs.description == 'exdoc descr'
    assert oper.external_docs.url == 'exdoc url'
    assert oper.external_docs.url == 'exdoc url'
    assert oper.operation_id == '1.1.1.1'
    assert oper.consumes == ['application/json']
    assert oper.produces == ['application/json']
    assert oper.parameters[0].name == 'this'
    assert oper.parameters[0].in_ == 'header'
    assert oper.parameters[0].description == 'this descr'
    assert oper.parameters[0].required
    assert oper.parameters[0].type == 'string'
    assert oper.parameters[0].format == 'byte'
    assert oper.responses[200].description == 'ok resp descr'


@pytest.mark.parametrize(
    'data,result',
    [
        ([1, 2, 3], False),
        (('1', '2', '3'), True),
        ('1234', True),
        ({'a': 1, 'b': 2}, True),
        ((i for i in range(10)), False),
    ],
)
def test_is_all_strings(data, result):
    assert schema.is_all_strings(data) == result


@pytest.mark.parametrize(
    'schema_update, error_msg',
    [
        (
            {
                'definitions': {
                    'Flower': {
                        'title': 'Flower title',
                        'description': 'Flowers of the country',
                        'type': 'object',
                        'properties': {
                            'name': {'type': 'string'},
                            'color': {'type': 'string'},
                            'field': {'type': 'string'},
                        },
                        'required': ['name', 'color', 'size'],
                    },
                },
            },
            '[\'definitions\', \'Flower\']: '
            'required fields are not subset of properties,'
            ' excess fields are [\'size\']',
        ),
        (
            {
                'definitions': {
                    'Pet': {
                        'title': 'Pet title',
                        'description': 'Extensive pet entity schema',
                        'type': 'string',
                    },
                    'PetClone': {'$ref': '#/definitions/Pet'},
                    'MyPet': {
                        'type': 'object',
                        'properties': {
                            'friend': {'$ref': '#/definitions/Pet'},
                        },
                        'required': ['friend'],
                    },
                    'RoboPet': {
                        'type': 'object',
                        'properties': {
                            'link': {'$ref': '#/definitions/Pet'},
                            'clone_link': {'$ref': '#/definitions/PetClone'},
                            'new_link': {'$ref': '#/definitions/MyPet'},
                        },
                        'required': [
                            'link',
                            'clone_link',
                            'new_link',
                            'missed_link',
                        ],
                    },
                },
            },
            '[\'definitions\', \'RoboPet\']: '
            'required fields are not subset of properties,'
            ' excess fields are [\'missed_link\']',
        ),
        (
            {
                'definitions': {
                    'FlowersDetails': {
                        'description': 'Flowers details',
                        'type': 'object',
                        'properties': {
                            'flower_data': {
                                'type': 'object',
                                'properties': {
                                    'id': {'type': 'string'},
                                    'code': {'type': 'string'},
                                    'name': {'type': 'string'},
                                    'is_rising': {'type': 'boolean'},
                                    'stages': {
                                        'description': 'stages for flowers',
                                        'type': 'array',
                                        'items': {
                                            'type': 'object',
                                            'properties': {
                                                'code': {'type': 'string'},
                                                'name': {'type': 'string'},
                                            },
                                            'required': [
                                                'worst_required',
                                                'bad',
                                            ],
                                        },
                                    },
                                },
                                'required': [
                                    'code',
                                    'is_rising',
                                    'stages',
                                    'bad_required',
                                ],
                            },
                        },
                        'required': ['flower_data, wrong_required'],
                    },
                },
            },
            '[\'definitions\', \'FlowersDetails\', \'properties\', '
            '\'flower_data\', \'properties\', \'stages\', \'items\']'
            ': required fields are not subset of properties,'
            ' excess fields are [\'bad\', \'worst_required\']',
        ),
        (
            {
                'paths': {
                    '/acquire_candidate': {
                        'parameters': [
                            {
                                'in': 'body',
                                'name': 'body_parameters',
                                'description': 'search parameters',
                                'schema': {
                                    'type': 'object',
                                    'required': ['order_id', 'wrong_id'],
                                    'properties': {
                                        'order_id': {
                                            'type': 'string',
                                            'description': 'order for id',
                                        },
                                        'force': {
                                            'type': 'boolean',
                                            'description': 'force',
                                        },
                                    },
                                },
                            },
                        ],
                    },
                },
            },
            '[\'paths\', \'/acquire_candidate\', \'parameters\', '
            '\'0\', \'schema\']: '
            'required fields are not subset of properties,'
            ' excess fields are [\'wrong_id\']',
        ),
    ],
)
def test_validation_for_required_params(
        schema_update, error_msg, minimal_schema,
):
    data = minimal_schema()
    data.update(schema_update)
    with pytest.raises(exceptions.ValidationError) as excinfo:
        schema.SwaggerSchema(data)
    assert excinfo.value.args == (error_msg,)


def test_response_object_schema(minimal_schema):
    data = minimal_schema()
    data.update(
        {
            'paths': {
                '/ping': {
                    'get': {
                        'responses': {
                            '200': {
                                'description': 'ok',
                                'schema': {
                                    'type': 'object',
                                    'properties': {'name': {'type': 'string'}},
                                },
                            },
                        },
                    },
                },
            },
            'responses': {
                'Error': {
                    'description': 'error',
                    'schema': {
                        'type': 'object',
                        'properties': {'code': {'type': 'string'}},
                    },
                },
            },
        },
    )
    swagger = schema.SwaggerSchema(data)
    assert swagger.paths['/ping'].get.responses[200].schema.type == 'object'
    assert swagger.responses['Error'].schema.type == 'object'


def test_one_of(minimal_schema):
    data = minimal_schema()
    data.update(
        {
            'definitions': {
                'Pet': {
                    'description': 'something',
                    'oneOf': [
                        {'type': 'string'},
                        {
                            'oneOf': [
                                {'type': 'integer'},
                                {
                                    'type': 'object',
                                    'properties': {'name': {'type': 'string'}},
                                },
                            ],
                        },
                    ],
                },
            },
        },
    )

    swagger = schema.SwaggerSchema(data)
    pet = swagger.definitions['Pet']
    assert pet.one_of[0].type == 'string'
    inner_one_of = pet.one_of[1].one_of
    assert inner_one_of[0].type == 'integer'
    assert inner_one_of[1].type == 'object'
    assert inner_one_of[1].properties['name'].type == 'string'


def test_schema_object_description(minimal_schema):
    data = minimal_schema()
    data.update(
        {
            'definitions': {
                'Pet': {
                    'title': 'Pet title',
                    'description': 'Pet description',
                    'type': 'string',
                },
                'WeirdPet': {
                    'type': 'object',
                    'properties': {
                        'pets': {
                            'type': 'array',
                            'items': {
                                'description': 'Some Pet',
                                '$ref': '#/definitions/Pet',
                            },
                        },
                        'cats': {
                            'description': 'Some Cat',
                            '$ref': '#/definitions/Pet',
                        },
                    },
                },
                'NewPet': {
                    'description': 'something',
                    'oneOf': [
                        {
                            'description': 'Hidden Devil',
                            '$ref': '#/definitions/Pet',
                        },
                        {
                            'type': 'object',
                            'properties': {
                                'name': {
                                    'description': 'Some Puppy',
                                    '$ref': '#/definitions/Pet',
                                },
                            },
                        },
                    ],
                },
            },
        },
    )

    swagger = schema.SwaggerSchema(data)
    weird_pet = swagger.definitions['WeirdPet']
    new_pet = swagger.definitions['NewPet']
    assert weird_pet.properties['pets'].items.description == 'Some Pet'
    assert weird_pet.properties['cats'].description == 'Some Cat'
    assert new_pet.one_of[0].description == 'Hidden Devil'
    assert new_pet.one_of[1].properties['name'].description == 'Some Puppy'


def test_schema_required_with_default(minimal_schema):
    data = minimal_schema()
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

    with pytest.raises(exceptions.ValidationError) as exc_info:
        schema.SwaggerSchema(data)

    assert exc_info.value.args == (
        '[\'definitions\', \'Pet\']: required property `name` '
        'must not have a default value',
    )


def test_schema_required_with_ref_default(minimal_schema):
    data = minimal_schema()
    data.update(
        {
            'definitions': {
                'SomeString': {'type': 'string', 'default': 'Rex'},
                'Pet': {
                    'title': 'Pet title',
                    'description': 'Pet description',
                    'type': 'object',
                    'properties': {
                        'name': {'$ref': '#/definitions/SomeString'},
                        'bane': {'type': 'string'},
                        'lame': {'type': 'string'},
                    },
                    'required': ['name', 'bane'],
                },
            },
        },
    )

    swagger = schema.SwaggerSchema(data)
    assert swagger.definitions['Pet'].properties['name'].default == 'Rex'
