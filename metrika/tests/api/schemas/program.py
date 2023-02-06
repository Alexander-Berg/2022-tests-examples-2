import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas
import metrika.admin.python.bishop.frontend.tests.api.schemas.constants as tests_api_constants


class ProgramSchema(tests_api_schemas.BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(ProgramSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['properties'] = tests_api_constants.PROGRAM_SCHEMA
        self.schema['properties']['data']['additionalProperties'] = False
        self.schema['properties']['data']['required'] = [
            'name',
            'template',
        ]


class ProgramListSchema(tests_api_schemas.ListSchema):
    def __init__(self, *args, **kwargs):
        super(ProgramListSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['items'] = {
            'type': 'object',
            'properties': tests_api_constants.PROGRAM_SCHEMA
        }
