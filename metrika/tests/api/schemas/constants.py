TEMPLATE_SCHEMA = {
    'name': {
        'type': 'string',
    },
    'format': {
        'type': 'string',
    },
    'text': {
        'type': 'string',
    },
}


PROGRAM_SCHEMA = {
    'name': {
        'type': 'string',
    },
    'template': {
        'type': 'object',
        'properties': TEMPLATE_SCHEMA,
    },
}


ENVIRONMENT_SCHEMA = {
    'name': {
        'type': 'string',
    },
    'is_root': {
        'type': 'boolean',
    },
    'parent': {
        'type': 'object',
        'properties': {
            'name': {
                'type': 'string',
            },
            'is_root': {
                'type': 'boolean',
            },
        },
    },
    'has_children': {
        'type': 'boolean',
    },
}


TARGET_VARIABLE_SCHEMA = {
    'name': {
        'type': 'string',
    },
    'environment': {
        'type': 'object',
        'properties': ENVIRONMENT_SCHEMA,
    },
}


VARIABLE_SCHEMA = {
    'type': {
        'type': 'string',
    },
    'value': {},
    'is_link': {
        'type': 'boolean',
    },
    'link': {
        'type': 'object',
        'properties': TARGET_VARIABLE_SCHEMA,
    },
    'name': {
        'type': 'string',
    },
    'environment': {
        'type': 'object',
        'properties': ENVIRONMENT_SCHEMA,
    },
}


ACTIVATION_REQUEST_SCHEMA = {
    'status': {
        'type': 'string',
    },
    'status_at': {
        'type': 'string',
    },
    'created': {
        'type': 'string',
    },
    'created_by': {
        'type': 'string',
    },
    'id': {
        'type': 'integer',
    },
    'program': {
        'type': 'string',
    },
    'environment': {
        'type': 'string',
    },
}


CONFIG_SCHEMA = {
    'id': {
        'type': 'integer',
    },
    'format': {
        'type': 'string',
    },
    'program': {
        'type': 'string',
    },
    'environment': {
        'type': 'string',
    },
    'template': {
        'type': 'string',
    },
    'hexdigest': {
        'type': 'string',
    },
    'active': {
        'type': 'boolean',
    },
    'use_vault': {
        'type': 'boolean',
    },
    'use_hosts': {
        'type': 'boolean',
    },
    'use_networks': {
        'type': 'boolean',
    },
}
