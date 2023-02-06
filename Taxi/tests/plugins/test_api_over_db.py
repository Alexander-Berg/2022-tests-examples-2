def test_api_over_db(
        generate_services_and_libraries, default_repository, default_base,
):
    default_repository['services/test-service/service.yaml']['api-over-db'] = {
        'enabled': True,
    }
    default_repository['services/test-service/api_over_db.yaml'] = {
        'generate-docs': True,
        'replicas': {
            'replica3': {
                'model-schema': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'some3-field3': {
                            'type': 'string',
                            'json-name': 'data.json-some3-field3',
                        },
                        'some3-field1': {
                            'type': 'bool',
                            'json-name': 'data.json-some3-field1',
                            'db-name': 'mongo-some3-field1',
                        },
                        'some3-field2': {
                            'type': 'date',
                            'json-name': 'data.json-some3-field2',
                            'bson-use-convert-to': True,
                        },
                        'some3-id': {
                            'type': 'string',
                            'json-name': 'json-some3-id',
                        },
                        'some3-revision': {
                            'type': 'string',
                            'json-name': 'json-some3-revision',
                        },
                        'some3-updated': {
                            'type': 'timestamp',
                            'db-name': 'mongo-some3-updated',
                        },
                        'some3-deleted': {
                            'type': 'bool',
                            'json-name': 'json-some3-deleted',
                        },
                    },
                    'required': ['some3-field3', 'some3-field1'],
                },
                'id-field': 'some3-id',
                'revision-field': 'some3-revision',
                'updated-field': 'some3-updated',
                'is-deleted-field': 'some3-deleted',
                'mongo-collection-name': 'some3_mongo_collection_name',
                'dumper': {
                    'dump-version': '8',
                    'prefix': 'some3-dump-prefix',
                    'component-name': 'some3-dump-component',
                },
                'cache': {
                    'component-name': 'some3-cache-component',
                    'update-deletions': False,
                },
                'handlers': {
                    'updates': {
                        'component-name': 'some3-updates-component',
                        'handler-name': 'v3/updates',
                        'array-name': 'some3-updates-data',
                        'path': '/v3/updates',
                    },
                    'retrieve': {
                        'component-name': 'some3-retrieve-component',
                        'handler-name': 'v3/retrieve',
                        'array-name': 'some3-retrieve-data',
                        'path': '/v3/retrieve',
                    },
                },
            },
            'replica1': {
                'model-schema': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'some1-field3': {
                            'type': 'string',
                            'json-name': 'data.json-some1-field3',
                        },
                        'some1-field1': {
                            'type': 'array',
                            'json-name': 'data.json-some1-field1',
                            'db-name': 'mongo-some1-field1',
                            'bson-use-convert-to': True,
                            'json-no-default-items': True,
                            'items': {'type': 'string'},
                        },
                        'some1-field2': {
                            'type': 'int',
                            'json-name': 'data.json-some1-field2',
                        },
                        'some1-id': {
                            'type': 'string',
                            'json-name': 'json-some1-id',
                        },
                        'some1-revision': {
                            'type': 'string',
                            'json-name': 'json-some1-revision',
                        },
                        'some1-updated': {
                            'type': 'timestamp',
                            'db-name': 'mongo-some1-updated',
                        },
                        'some1-deleted': {
                            'type': 'bool',
                            'json-name': 'json-some1-deleted',
                        },
                    },
                    'required': ['some1-field3', 'some1-field1'],
                },
                'id-field': 'some1-id',
                'revision-field': 'some1-revision',
                'updated-field': 'some1-updated',
                'is-deleted-field': 'some1-deleted',
                'mongo-collection-name': 'some1_mongo_collection_name',
                'dumper': {
                    'dump-version': '8',
                    'prefix': 'some1-dump-prefix',
                    'component-name': 'some1-dump-component',
                },
                'cache': {
                    'component-name': 'some1-cache-component',
                    'update-deletions': False,
                },
                'handlers': {
                    'updates': {
                        'component-name': 'some1-updates-component',
                        'handler-name': 'v1/updates',
                        'array-name': 'some1-updates-data',
                        'path': '/v1/updates',
                    },
                    'retrieve': {
                        'component-name': 'some1-retrieve-component',
                        'handler-name': 'v1/retrieve',
                        'array-name': 'some1-retrieve-data',
                        'path': '/v1/retrieve',
                    },
                },
            },
            'replica2': {
                'model-schema': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'some2-field': {
                            'type': 'string',
                            'json-name': 'data.json-some2-field',
                        },
                        'some2-id': {
                            'type': 'string',
                            'json-name': 'json-some2-id',
                        },
                        'some2-revision': {
                            'type': 'string',
                            'json-name': 'json-some2-revision',
                        },
                        'some2-updated': {
                            'type': 'timestamp',
                            'db-name': 'mongo-some2-updated',
                        },
                        'some2-deleted': {
                            'type': 'bool',
                            'json-name': 'json-some2-deleted',
                        },
                    },
                },
                'id-field': 'some2-id',
                'revision-field': 'some2-revision',
                'updated-field': 'some2-updated',
                'is-deleted-field': 'some2-deleted',
                'mongo-collection-name': 'some2_mongo_collection_name',
                'dumper': {
                    'dump-version': '8',
                    'prefix': 'some2-dump-prefix',
                    'component-name': 'some2-dump-component',
                },
                'cache': {
                    'component-name': 'some2-cache-component',
                    'update-deletions': False,
                },
                'handlers': {
                    'updates': {
                        'component-name': 'some2-updates-component',
                        'handler-name': 'v2/updates',
                        'array-name': 'some2-updates-data',
                        'path': '/v2/updates',
                    },
                    'retrieve': {
                        'component-name': 'some2-retrieve-component',
                        'handler-name': 'v2/retrieve',
                        'array-name': 'some2-retrieve-data',
                        'path': '/v2/retrieve',
                    },
                },
            },
        },
        'proxies': {
            'proxy1': {
                'model-schema': {
                    'type': 'object',
                    'additionalProperties': False,
                    'properties': {
                        'some2-field': {
                            'type': 'string',
                            'json-name': 'data.json-some2-field',
                        },
                        'some2-id': {
                            'type': 'string',
                            'json-name': 'json-some2-id',
                        },
                    },
                },
                'id-field': 'some2-id',
                'mongo-collection-name': 'some2_mongo_collection_name',
                'handlers': {
                    'proxy-retrieve': {
                        'component-name': 'some2-proxy-retrieve-component',
                        'handler-name': 'v2/proxy_retrieve',
                        'array-name': 'some2-retrieve-data',
                        'path': '/v2/retrieve',
                    },
                },
            },
        },
    }
    generate_services_and_libraries(
        default_repository, 'test_api_over_db/test', default_base,
    )
