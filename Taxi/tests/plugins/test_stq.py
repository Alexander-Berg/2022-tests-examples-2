def test_stq(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['stq-client'] = {
        'queues': [
            {'name': 'queue3', 'args_schema': False},
            {'name': 'queue1', 'args_schema': False},
            {'name': 'queue2', 'args_schema': False},
            {'name': 'test'},
        ],
    }
    default_repository['services/test-service/service.yaml']['stq-worker'] = {
        'queues': [{'name': 'test', 'args_schema': True}],
    }
    object_schema = {
        'TestObject': {
            'type': 'object',
            'properties': {
                'string_property': {'type': 'string'},
                'bool_property': {'type': 'boolean'},
            },
            'required': ['string_property'],
            'additionalProperties': False,
        },
        'DateProperty': {'type': 'string', 'format': 'date-time'},
        'Datetime': {
            'type': 'object',
            'format': 'bson-date-time',
            'additionalProperties': False,
            'properties': {'$date': {'$ref': '#/DateProperty'}},
            'required': ['$date'],
        },
    }
    # for worker
    schema = {
        'name': 'test',
        'arguments': [
            {'name': 'simple_string', 'schema': {'type': 'string'}},
            {
                'name': 'array',
                'schema': {'type': 'array', 'items': {'type': 'string'}},
            },
            {
                'name': 'optional_number',
                'schema': {'type': 'number'},
                'required': False,
            },
            {
                'name': 'object_field',
                'required': False,
                'schema': {'$ref': 'test_definitions.yaml#/TestObject'},
            },
            {
                'name': 'datetime_field',
                'required': False,
                'schema': {'$ref': 'test_definitions.yaml#/Datetime'},
            },
        ],
    }
    default_repository['services/test-service/docs/stq/test.yaml'] = schema
    default_repository[
        'services/test-service/docs/stq/definitions/test_definitions.yaml'
    ] = object_schema

    # for client
    schema = {
        'name': 'test',
        'arguments': [
            {'name': 'simple_string', 'schema': {'type': 'string'}},
            {
                'name': 'array',
                'schema': {'type': 'array', 'items': {'type': 'string'}},
            },
            {
                'name': 'optional_number',
                'schema': {'type': 'number'},
                'required': False,
            },
            {
                'name': 'object_field',
                'schema': {'$ref': 'test_definitions.yaml#/TestObject'},
                'required': False,
            },
        ],
    }
    default_repository[
        '../schemas/schemas/stq/definitions/test_definitions.yaml'
    ] = object_schema
    default_repository['../schemas/schemas/stq/test.yaml'] = schema
    generate_services_and_libraries(
        default_repository, 'test_stq/test', default_base,
    )
