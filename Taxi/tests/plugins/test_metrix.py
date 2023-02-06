def test_metrix(
        generate_services_and_libraries, default_repository, default_base,
):
    path = 'services/test-service/metrix/'
    default_repository.update(
        {
            path
            + 'metrix.yaml': {
                'labels': {
                    'Labels0': [
                        'agglomeration',
                        {'service': {'default': 'taxi'}},
                    ],
                    'Labels1': [
                        'agglomeration',
                        'dispatch_statuses',
                        {'tariff_group': {}},
                        {'service': {'default': 'taxi'}},
                    ],
                },
                'types': {
                    'Counter': {'predefined_type': 'Counter'},
                    'TimeCounter': {
                        'predefined_type': 'Counter',
                        'value_type': 'std::chrono::microseconds',
                    },
                    'Percentile': {
                        'predefined_type': 'Percentile',
                        'value_type': 'std::uint64_t',
                        'percentiles': [
                            0,
                            10,
                            20,
                            30,
                            40,
                            50,
                            60,
                            70,
                            80,
                            90,
                            95,
                            98,
                            99,
                            100,
                        ],
                    },
                    'PercentileLap': {
                        'predefined_type': 'PercentileLap',
                        'value_type': 'std::chrono::milliseconds',
                        'percentiles': [
                            0,
                            10,
                            20,
                            30,
                            40,
                            50,
                            60,
                            70,
                            80,
                            90,
                            95,
                            98,
                            99,
                            100,
                        ],
                    },
                    'TimePercentile': {
                        'predefined_type': 'Percentile',
                        'value_type': 'std::chrono::milliseconds',
                        'percentiles': [
                            0,
                            10,
                            20,
                            30,
                            40,
                            50,
                            60,
                            70,
                            80,
                            90,
                            95,
                            98,
                            99,
                            100,
                        ],
                    },
                    'AvgCounter': {
                        'predefined_type': 'AvgCounter',
                        'value_type': 'std::chrono::seconds',
                    },
                    'MilliLap': {
                        'predefined_type': 'Lap',
                        'value_type': 'std::chrono::milliseconds',
                    },
                },
                'metrics': {
                    'metric0': {
                        'labels': 'Labels0',
                        'type': 'Counter',
                        'dashboard_params': {
                            'repeat_by_variable': 'var1',
                            'group_lines': 'sum',
                            'collapsed': True,
                        },
                    },
                    'metric1': {'labels': 'Labels1', 'type': 'TimeCounter'},
                    'metric2': {
                        'labels': 'Labels0',
                        'type': 'Percentile',
                        'dashboard_params': {
                            'repeat_by_variable': 'var1',
                            'group_lines': 'sum',
                            'collapsed': True,
                        },
                    },
                    'metric3': {'labels': 'Labels1', 'type': 'TimePercentile'},
                    'metric4': {'labels': 'Labels0', 'type': 'AvgCounter'},
                    'metric5': {'labels': 'Labels0', 'type': 'MilliLap'},
                    'metric6': {'type': 'MilliLap'},
                    'metric7': {'type': 'PercentileLap'},
                },
                'dashboard': {
                    'clownductor_project': 'taxi',
                    'dashboard_title': 'test_dashboard',
                    'variables': [{'name': 'var1', 'multivalue': True}],
                },
            },
        },
    )

    default_repository[
        (
            '../schemas/schemas/configs/declarations/metrix/'
            'METRIX_AGGREGATION.yaml'
        )
    ] = (
        {
            'description': (
                'Настройки аггрегирования лейблов при сборе метрик\n'
            ),
            'default': [],
            'tags': ['notfallback', 'by-service', 'no-edit-without-service'],
            'maintainers': ['dulumdziev', 'alex-tsarkov'],
            'schema': {
                'description': 'Набор применяемых правил',
                'type': 'array',
                'items': {'$ref': '#/definitions/RuleWithValue'},
                'definitions': {
                    'Values': {
                        'type': 'array',
                        'x-taxi-cpp-type': 'std::unordered_set',
                        'items': {'type': 'string'},
                    },
                    'NoneOfRule': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'none_of': {'$ref': '#/definitions/Values'},
                        },
                        'required': ['none_of'],
                    },
                    'AllOfRule': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'all_of': {'$ref': '#/definitions/Values'},
                        },
                        'required': ['all_of'],
                    },
                    'AnyOfRule': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'any_of': {'$ref': '#/definitions/Values'},
                        },
                        'required': ['any_of'],
                    },
                    'SubsetOfRule': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'subset_of': {'$ref': '#/definitions/Values'},
                        },
                        'required': ['subset_of'],
                    },
                    'NotRule': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'not': {
                                'oneOf': [
                                    {'$ref': '#/definitions/NoneOfRule'},
                                    {'$ref': '#/definitions/AllOfRule'},
                                    {'$ref': '#/definitions/AnyOfRule'},
                                    {'$ref': '#/definitions/SubsetOfRule'},
                                ],
                            },
                        },
                        'required': ['not'],
                    },
                    'AndRule': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'and': {
                                'type': 'array',
                                'items': {
                                    'oneOf': [
                                        {'$ref': '#/definitions/NoneOfRule'},
                                        {'$ref': '#/definitions/AllOfRule'},
                                        {'$ref': '#/definitions/AnyOfRule'},
                                        {'$ref': '#/definitions/SubsetOfRule'},
                                    ],
                                },
                            },
                        },
                        'required': ['and'],
                    },
                    'OrRule': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'or': {
                                'type': 'array',
                                'items': {
                                    'oneOf': [
                                        {'$ref': '#/definitions/NoneOfRule'},
                                        {'$ref': '#/definitions/AllOfRule'},
                                        {'$ref': '#/definitions/AnyOfRule'},
                                        {'$ref': '#/definitions/SubsetOfRule'},
                                    ],
                                },
                            },
                        },
                        'required': ['or'],
                    },
                    'Rule': {
                        'oneOf': [
                            {'$ref': '#/definitions/NoneOfRule'},
                            {'$ref': '#/definitions/AllOfRule'},
                            {'$ref': '#/definitions/AnyOfRule'},
                            {'$ref': '#/definitions/SubsetOfRule'},
                            {'$ref': '#/definitions/NotRule'},
                            {'$ref': '#/definitions/AndRule'},
                            {'$ref': '#/definitions/OrRule'},
                        ],
                    },
                    'RuleWithValue': {
                        'type': 'object',
                        'additionalProperties': False,
                        'required': ['rule', 'value'],
                        'properties': {
                            'rule': {'$ref': '#/definitions/Rule'},
                            'value': {
                                'type': 'array',
                                'items': {'$ref': '#/definitions/AggRule'},
                            },
                        },
                    },
                    'AggRule': {
                        'oneOf': [
                            {'$ref': '#/definitions/Whitelist'},
                            {'$ref': '#/definitions/Grouping'},
                        ],
                        'discriminator': {
                            'propertyName': 'rule_type',
                            'mapping': {
                                'whitelist': '#/definitions/Whitelist',
                                'grouping': '#/definitions/Grouping',
                            },
                        },
                    },
                    'Whitelist': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'rule_type': {'type': 'string'},
                            'label_name': {'type': 'string'},
                            'values': {
                                'type': 'array',
                                'items': {'type': 'string'},
                            },
                            'use_others': {'type': 'boolean'},
                        },
                        'required': ['label_name', 'values', 'use_others'],
                    },
                    'Grouping': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'rule_type': {'type': 'string'},
                            'label_name': {'type': 'string'},
                            'groups': {
                                'type': 'array',
                                'items': {'$ref': '#/definitions/Group'},
                            },
                            'use_others': {'type': 'boolean'},
                        },
                        'required': ['label_name', 'groups', 'use_others'],
                    },
                    'Group': {
                        'type': 'object',
                        'additionalProperties': False,
                        'properties': {
                            'group_name': {'type': 'string'},
                            'values': {
                                'type': 'array',
                                'items': {'type': 'string'},
                            },
                        },
                        'required': ['group_name', 'values'],
                    },
                },
            },
        }
    )

    default_repository['services/test-service/service.yaml']['configs'] = {
        'names': ['METRIX_AGGREGATION'],
    }
    generate_services_and_libraries(
        default_repository, 'test_metrix/test_metrix', default_base,
    )
