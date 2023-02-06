export const DOMAINS_EMPTY_RESTRICTIONS = [];

export const DOMAINS_ONE_RESTRICTION = [
    {
        'handler': {
            'path': '/foo/bar',
            'method': 'GET',
        },
        'predicate': {
            'init': {
                'set': [],
                'arg_name': 'headers:X-WFM-Domain',
                'set_elem_type': 'string',
            },
            'type': 'in_set',
            'method': 'json',
        },
    },
    {
        'handler': {
            'path': '/v1/skills/values',
            'method': 'GET',
        },
        'predicate': {
            'init': {
                'set': [
                    'taxi',
                    'eats',
                    'eats',
                ],
                'arg_name': 'headers:X-WFM-Domain',
                'set_elem_type': 'string',
            },
            'type': 'in_set',
            'method': 'json',
        },
    },
    {
        'handler': {
            'path': '/v1/skills/trash',
            'method': 'GET',
        },
        'predicate': {
            'init': {
                'set': [],
                'arg_name': 'headers:X-WFM-Domain',
                'set_elem_type': 'string',
            },
            'type': 'in_set',
            'method': 'json',
        },
    },
];

export const DOMAINS_SEVERAL_RESTRICTIONS = [
    {
        'handler': {
            'path': '/foo/bar',
            'method': 'GET',
        },
        'predicate': {
            'init': {
                'set': [],
                'arg_name': 'headers:X-WFM-Domain',
                'set_elem_type': 'string',
            },
            'type': 'in_set',
            'method': 'json',
        },
    },
    {
        'handler': {
            'path': '/v1/skills/values',
            'method': 'GET',
        },
        'predicate': {
            'init': {
                'set': [
                    'taxi',
                    'eats',
                ],
                'arg_name': 'headers:X-WFM-Domain',
                'set_elem_type': 'string',
            },
            'type': 'in_set',
            'method': 'json',
        },
    },
    {
        'handler': {
            'path': '/v1/skills/values',
            'method': 'GET',
        },
        'predicate': {
            'init': {
                'set': [
                    'taxi',
                    'eats_foo_bar',
                    '',
                    'test',
                ],
                'arg_name': 'headers:X-WFM-Domain',
                'set_elem_type': 'string',
            },
            'type': 'in_set',
            'method': 'json',
        },
    },
    {
        'handler': {
            'path': '/v1/skills/trash',
            'method': 'GET',
        },
        'predicate': {
            'init': {
                'set': [],
                'arg_name': 'headers:X-WFM-Domain',
                'set_elem_type': 'string',
            },
            'type': 'in_set',
            'method': 'json',
        },
    },
    {
        'handler': {
            'path': '/v1/skills/values',
            'method': 'GET',
        },
        'predicate': {
            'init': {
                'set': [
                    'eats',
                    '123',
                ],
                'arg_name': 'headers:X-WFM-Domain',
                'set_elem_type': 'string',
            },
            'type': 'in_set',
            'method': 'json',
        },
    },
];
