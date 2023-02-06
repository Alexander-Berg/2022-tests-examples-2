import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas
import metrika.admin.python.bishop.frontend.tests.api.schemas.constants as tests_api_constants


class ConfigSchema(tests_api_schemas.BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(ConfigSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['properties'] = tests_api_constants.CONFIG_SCHEMA
        self.schema['properties']['data']['additionalProperties'] = False
        self.schema['properties']['data']['required'] = [
            'id',
            'program',
            'environment',
            'template',
            'hexdigest',
            'active',
            'use_vault',
            'use_hosts',
            'use_networks',
        ]


class ConfigWithTextSchema(ConfigSchema):
    def __init__(self, *args, **kwargs):
        super(ConfigWithTextSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['properties']['text'] = {'type': 'string'}
        self.schema['properties']['data']['required'].append('text')


class ConfigListSchema(tests_api_schemas.ListSchema):
    def __init__(self, *args, **kwargs):
        super(ConfigListSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['items'] = {
            'type': 'object',
            'properties': tests_api_constants.CONFIG_SCHEMA
        }
