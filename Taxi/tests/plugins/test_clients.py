import pathlib

import pytest
import yaml


CLIENT_QOS = {
    'description': 'QoS settings for client-test service',
    'default': {'__default__': {'attempts': 3, 'timeout-ms': 200}},
    'schema': {
        'type': 'object',
        'additionalProperties': {'$ref': '#/definitions/QosInfo'},
        'required': ['__default__'],
        'properties': {'__default__': {'$ref': '#/definitions/QosInfo'}},
        'definitions': {
            'QosInfo': {
                'type': 'object',
                'properties': {
                    'attempts': {
                        'type': 'integer',
                        'default': 3,
                        'minimum': 1,
                    },
                    'timeout-ms': {
                        'type': 'integer',
                        'minimum': 1,
                        'x-taxi-cpp-type': 'std::chrono::milliseconds',
                    },
                },
                'additionalProperties': False,
                'required': ['timeout-ms'],
            },
        },
    },
}


@pytest.mark.parametrize(
    ['client_yaml', 'generate_path'],
    [
        (
            {'middlewares': {'tvm': 'test-tvm'}},
            'test_clients/client_test_service',
        ),
        (
            {'middlewares': {'eats-partners': 'v1'}},
            'test_clients/client_test_service_eats_partners_middleware',
        ),
        ({}, 'test_clients/client_test_service_no_tvm'),
    ],
)
def test_clients(
        generate_services_and_libraries,
        default_repository,
        default_base,
        client_yaml,
        generate_path,
):
    default_repository[
        '../schemas/schemas/services/client-test-service/client.yaml'
    ] = (
        {
            'host': {
                'production': 'https://client-test-service.localhost',
                'testing': 'http://client-test-service.localhost',
                'unstable': 'client-test-service.localhost',
            },
            **client_yaml,
        }
    )
    default_repository[
        '../schemas/schemas/services/client-test-service/api/api-3.0.yaml'
    ] = (
        {
            'openapi': '3.0.0',
            'info': {
                'title': 'Service for clients codegen testing',
                'version': '0.1',
            },
            'x-taxi-client-qos': {
                'taxi-config': 'CLIENT_TEST_SERVICE_CLIENT_QOS',
            },
            'servers': [{'url': 'url', 'description': 'production'}],
            'components': {},
            'paths': {
                '/v1/{my-arg}/smth': {
                    'post': {
                        'parameters': [
                            {
                                'in': 'header',
                                'name': 'X-Test-Header',
                                'schema': {'type': 'string'},
                            },
                            {
                                'in': 'path',
                                'name': 'my-arg',
                                'required': True,
                                'schema': {'type': 'string'},
                            },
                        ],
                        'requestBody': {
                            'required': True,
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'properties': {
                                            'id': {
                                                'type': 'integer',
                                                'minimum': 0,
                                            },
                                            'array': {
                                                'type': 'array',
                                                'items': {'type': 'string'},
                                                'minItems': 1,
                                            },
                                        },
                                        'additionalProperties': False,
                                        'required': ['id'],
                                    },
                                },
                            },
                        },
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {},
                                            'additionalProperties': False,
                                        },
                                    },
                                },
                            },
                            '201': {'description': 'OK'},
                            '404': {'description': 'Resource not found'},
                        },
                    },
                    'get': {
                        'x-taxi-query-log-mode': 'hide',
                        'parameters': [
                            {
                                'in': 'header',
                                'name': 'X-Test-Header',
                                'schema': {'type': 'string'},
                            },
                            {
                                'in': 'path',
                                'name': 'my-arg',
                                'required': True,
                                'schema': {'type': 'string'},
                            },
                        ],
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'properties': {
                                                'ok': {'type': 'string'},
                                            },
                                            'additionalProperties': False,
                                            'required': ['ok'],
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                '/v2/smth': {
                    'x-taxi-client-codegen': False,
                    'post': {
                        'requestBody': {
                            'required': True,
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'additionalProperties': False,
                                    },
                                },
                            },
                        },
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'additionalProperties': False,
                                        },
                                    },
                                },
                            },
                        },
                    },
                    'get': {
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'additionalProperties': False,
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                '/v3/smth': {
                    'post': {
                        'x-taxi-client-codegen': False,
                        'requestBody': {
                            'required': True,
                            'content': {
                                'application/json': {
                                    'schema': {
                                        'type': 'object',
                                        'additionalProperties': False,
                                    },
                                },
                            },
                        },
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'additionalProperties': False,
                                        },
                                    },
                                },
                            },
                        },
                    },
                    'get': {
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'additionalProperties': False,
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        }
    )
    default_repository[
        '../schemas/schemas/services/client-test-service/api/api.yaml'
    ] = (
        {
            'swagger': '2.0',
            'info': {
                'title': 'Service for clients codegen testing',
                'version': '0.1',
            },
            'x-taxi-client-qos': {
                'taxi-config': 'CLIENT_TEST_SERVICE_CLIENT_QOS',
            },
            'paths': {
                '/': {
                    'post': {
                        'parameters': [
                            {
                                'in': 'header',
                                'name': 'X-Test-Header',
                                'type': 'string',
                            },
                            {
                                'in': 'body',
                                'name': 'body',
                                'required': True,
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'id': {
                                            'type': 'integer',
                                            'minimum': 0,
                                        },
                                        'array': {
                                            'type': 'array',
                                            'items': {'type': 'string'},
                                            'minItems': 1,
                                        },
                                    },
                                    'additionalProperties': False,
                                    'required': ['id'],
                                },
                            },
                        ],
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'schema': {
                                    'type': 'object',
                                    'properties': {},
                                    'additionalProperties': False,
                                },
                            },
                            '201': {'description': 'OK'},
                            '404': {'description': 'Resource not found'},
                        },
                    },
                    'get': {
                        'parameters': [
                            {
                                'in': 'query',
                                'name': 'secret',
                                'type': 'string',
                                'x-taxi-query-log-mode': 'hide',
                            },
                            {
                                'in': 'header',
                                'name': 'X-Test-Header',
                                'type': 'string',
                            },
                        ],
                        'responses': {
                            '200': {
                                'description': 'OK',
                                'schema': {
                                    'type': 'object',
                                    'properties': {'ok': {'type': 'string'}},
                                    'additionalProperties': False,
                                    'required': ['ok'],
                                },
                            },
                        },
                    },
                },
            },
        }
    )
    default_repository[
        (
            '../schemas/schemas/configs/declarations/'
            'CLIENT_TEST_SERVICE_CLIENT_QOS.yaml'
        )
    ] = CLIENT_QOS
    default_repository['services/test-service/service.yaml']['clients'] = [
        'client-test-service',
    ]
    generate_services_and_libraries(
        default_repository, generate_path, default_base,
    )


def test_aliases_merge(
        generate_services_and_libraries,
        multi_unit_repository,
        multi_unit_base,
):
    multi_unit_repository.update(
        {
            'services/test-service/docs/api/api-3.0.yaml': {
                'openapi': '3.0.0',
                'info': {
                    'title': 'Service for clients codegen testing',
                    'version': '0.1',
                },
                'x-taxi-client-qos': {
                    'taxi-config': 'CLIENT_TEST_SERVICE_CLIENT_QOS',
                },
                'servers': [{'url': 'url', 'description': 'production'}],
                'components': {},
                'paths': {
                    '/v1/{my-arg}/smth': {
                        'post': {
                            'requestBody': {
                                'required': True,
                                'content': {
                                    'application/json': {
                                        'schema': {
                                            'type': 'object',
                                            'additionalProperties': False,
                                            'properties': {},
                                        },
                                    },
                                },
                            },
                            'responses': {'200': {'description': 'OK'}},
                        },
                    },
                },
            },
        },
    )
    multi_unit_repository[
        (
            '../schemas/schemas/configs/declarations/'
            'CLIENT_TEST_SERVICE_CLIENT_QOS.yaml'
        )
    ] = CLIENT_QOS
    generate_services_and_libraries(
        multi_unit_repository,
        'test_clients/test_aliases_merge',
        multi_unit_base,
    )


def test_unix_socket(
        generate_services_and_libraries,
        default_repository,
        default_base,
        uservices_path,
):
    default_repository[
        '../schemas/schemas/services/client-test-service/client.yaml'
    ] = (
        {
            'host': {
                'production': 'unix:/var/lib/abc',
                'testing': 'unix:/var/lib/abc',
            },
        }
    )
    default_repository[
        '../schemas/schemas/services/client-test-service/api/api.yaml'
    ] = (
        {
            'swagger': '2.0',
            'info': {
                'title': 'Service for clients codegen testing',
                'version': '0.1',
            },
            'x-taxi-client-qos': {
                'taxi-config': 'CLIENT_TEST_SERVICE_CLIENT_QOS',
            },
            'paths': {},
        }
    )

    default_repository['services/test-service/service.yaml']['clients'] = [
        'client-test-service',
    ]
    generate_services_and_libraries(
        default_repository, 'test_clients/test_unix_socket', default_base,
    )

    filepath = pathlib.Path(uservices_path).joinpath(
        'tests-pytest/tests/plugins/static/test_clients/test_unix_socket/'
        'build/services/test-service/configs/config_vars.production.yaml',
    )
    with filepath.open() as ifile:
        variables = yaml.safe_load(ifile)

        # Assert that the unix socket name is not adjusted
        assert (
            variables['client-test-service-client-base-url']
            == 'unix:/var/lib/abc'
        )


@pytest.mark.skip(reason='broken')
def test_multiunit(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository[
        '../schemas/schemas/services/client-test-service/aliases.yaml'
    ] = {'taxi': 'unit-taxi', 'bank': 'unit-bank'}
    default_repository[
        (
            '../schemas/schemas/services/client-test-service/clients/'
            'unit-taxi/client.yaml'
        )
    ] = (
        {
            'host': {
                'production': 'unix:/var/lib/taxi',
                'testing': 'unix:/var/lib/taxi',
            },
        }
    )
    default_repository[
        (
            '../schemas/schemas/services/client-test-service/clients/'
            'unit-bank/client.yaml'
        )
    ] = (
        {
            'host': {
                'production': 'unix:/var/lib/bank',
                'testing': 'unix:/var/lib/bank',
            },
        }
    )
    default_repository[
        (
            '../schemas/schemas/services/client-test-service/clients/'
            'unit-smth/client.yaml'
        )
    ] = (
        {
            'host': {
                'production': 'unix:/var/lib/smth',
                'testing': 'unix:/var/lib/smth',
            },
        }
    )
    default_repository[
        '../schemas/schemas/services/client-test-service/api/api.yaml'
    ] = (
        {
            'swagger': '2.0',
            'info': {
                'title': 'Service for clients codegen testing',
                'version': '0.1',
            },
            'x-taxi-client-qos': {
                'taxi-config': 'CLIENT_TEST_SERVICE_CLIENT_QOS',
            },
            'paths': {},
        }
    )

    default_repository['services/test-service/service.yaml']['clients'] = [
        'client-test-service@unit-bank',
        'client-test-service@unit-taxi',
    ]
    generate_services_and_libraries(
        default_repository, 'test_clients/test_multiunit', default_base,
    )
