import jsonschema

from sandbox.projects.browser.maintenance import BrowserPitstopCheck

SCHEMA = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'id': {'type': 'string'},
            'conditions': {
                'type': 'object',
                'properties': {
                    'tag': {
                        'type': 'string',
                        'pattern': '^[A-Z0-9_]+$',
                    },
                    'cores': {'type': 'number'},
                },
                'additionalProperties': False,
            },
            'properties': {'$ref': '#/definitions/build_properties'},
            'dep_properties': {
                'type': 'object',
                'patternProperties': {
                    '^.*$': {'$ref': '#/definitions/build_properties'},
                },
            },
        },
        'required': ['id'],
        'additionalProperties': False,
    },
    'definitions': {
        'build_properties': {
            'type': 'object',
            'patternProperties': {
                '^.*$': {'type': 'string'},
            },
        },
    },
}


def test_pitstop_builds():
    jsonschema.validate(BrowserPitstopCheck.load_config(), SCHEMA)
