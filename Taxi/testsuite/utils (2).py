RULES_SIMPLE = [
    {
        'input': {'http-path-prefix': '/test'},
        'output': {'tvm-service': 'test', 'upstream': {'$mockserver': ''}},
        'proxy': {},
    },
]

AM_RULES_SIMPLE = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'common_components',
            'prefix': '/test',
            'priority': 100,
            'rule_name': '/test',
        },
        'output': {
            'attempts': 1,
            'timeout_ms': 100,
            'tvm_service': 'test',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {},
        'rule_type': 'int-authproxy',
    },
]


RULES_REWRITE = [
    {
        'input': {'http-path-prefix': '/test'},
        'output': {'tvm-service': 'test', 'upstream': {'$mockserver': ''}},
        'proxy': {'path-rewrite-strict': '/tost'},
    },
]

AM_RULES_REWRITE = [
    {
        'input': {
            'description': '(imported from taxi config)',
            'maintained_by': 'common_components',
            'prefix': '/test',
            'priority': 100,
            'rule_name': '/test',
        },
        'output': {
            'attempts': 1,
            'rewrite_path_prefix': '/tost',
            'timeout_ms': 100,
            'tvm_service': 'test',
            'upstream': {'$mockserver': ''},
        },
        'proxy': {},
        'rule_type': 'int-authproxy',
    },
]
