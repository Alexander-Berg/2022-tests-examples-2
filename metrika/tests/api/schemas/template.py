import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas
import metrika.admin.python.bishop.frontend.tests.api.schemas.constants as tests_api_constants


class TemplateSchema(tests_api_schemas.BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(TemplateSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['properties'] = tests_api_constants.TEMPLATE_SCHEMA
        self.schema['properties']['data']['additionalProperties'] = False


class TemplateListSchema(tests_api_schemas.ListSchema):
    def __init__(self, *args, **kwargs):
        super(TemplateListSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['items'] = {
            'type': 'object',
            'properties': tests_api_constants.TEMPLATE_SCHEMA,
        }
