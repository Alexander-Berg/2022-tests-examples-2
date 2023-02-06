import copy

import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas
import metrika.admin.python.bishop.frontend.tests.api.schemas.constants as tests_api_constants


class EnvironmentSchema(tests_api_schemas.BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(EnvironmentSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['properties'] = tests_api_constants.ENVIRONMENT_SCHEMA
        self.schema['properties']['data']['additionalProperties'] = False


class SingleEnvironmentSchema(tests_api_schemas.BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(SingleEnvironmentSchema, self).__init__(*args, **kwargs)
        self.schema = tests_api_constants.ENVIRONMENT_SCHEMA


class SingleEnvironmentRootSchema(tests_api_schemas.BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(SingleEnvironmentRootSchema, self).__init__(*args, **kwargs)
        root_schema = copy.deepcopy(tests_api_constants.ENVIRONMENT_SCHEMA)
        root_schema['parent']['type'] = None
        del root_schema['parent']['properties']
        self.schema = root_schema


class VariableSchema(tests_api_schemas.BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(VariableSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['properties'] = tests_api_constants.VARIABLE_SCHEMA
        self.schema['properties']['data']['additionalProperties'] = False
        self.schema['properties']['data']['required'] = [
            'type',
            'value',
            'is_link',
            'name',
            'environment',
        ]


class SingleVariableSchema(tests_api_schemas.BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(SingleVariableSchema, self).__init__(*args, **kwargs)
        self.schema['properties'] = tests_api_constants.VARIABLE_SCHEMA
        self.schema['additionalProperties'] = False
        self.schema['type'] = 'object'
        self.schema['required'] = [
            'type',
            'value',
            'is_link',
            'name',
            'environment',
        ]


class StringVariableSchema(VariableSchema):
    def __init__(self, *args, **kwargs):
        super(StringVariableSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['properties']['value']['type'] = 'string'


class IntegerVariableSchema(VariableSchema):
    def __init__(self, *args, **kwargs):
        super(IntegerVariableSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['properties']['value']['type'] = 'integer'


class BooleanVariableSchema(VariableSchema):
    def __init__(self, *args, **kwargs):
        super(BooleanVariableSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['properties']['value']['type'] = 'boolean'


class JsonVariableSchema(VariableSchema):
    def __init__(self, *args, **kwargs):
        super(JsonVariableSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['properties']['value']['type'] = [
            'object',
            'array',
        ]


class SingleStringVariableSchema(SingleVariableSchema):
    def __init__(self, *args, **kwargs):
        super(SingleStringVariableSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['value']['type'] = [
            'string',
        ]


class SingleIntegerVariableSchema(SingleVariableSchema):
    def __init__(self, *args, **kwargs):
        super(SingleIntegerVariableSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['value']['type'] = [
            'integer',
        ]


class SingleBooleanVariableSchema(SingleVariableSchema):
    def __init__(self, *args, **kwargs):
        super(SingleBooleanVariableSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['value']['type'] = [
            'boolean',
        ]


class SingleJsonVariableSchema(SingleVariableSchema):
    def __init__(self, *args, **kwargs):
        super(SingleJsonVariableSchema, self).__init__(*args, **kwargs)
        self.schema = copy.deepcopy(self.schema)
        self.schema['properties']['value']['type'] = [
            'object',
            'array',
        ]


class VariableListSchema(tests_api_schemas.ListSchema):
    def __init__(self,
                 *args,
                 **kwargs
                 ):
        super(VariableListSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['type'] = 'object'
        self.schema['properties']['data']['properties'] = {
            'self': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': tests_api_constants.VARIABLE_SCHEMA,
                }
            },
            'inherited': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': tests_api_constants.VARIABLE_SCHEMA,
                }
            },
        }
