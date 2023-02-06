import metrika.admin.python.bishop.frontend.tests.api.schemas as tests_api_schemas
import metrika.admin.python.bishop.frontend.tests.api.schemas.constants as tests_api_constants


class ActivationRequestSchema(tests_api_schemas.BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(ActivationRequestSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['properties'] = tests_api_constants.ACTIVATION_REQUEST_SCHEMA
        self.schema['properties']['data']['additionalProperties'] = False
        self.schema['properties']['data']['required'] = [
            'status',
            'status_at',
            'created',
            'created_by',
            'id',
            'program',
            'environment',
        ]


class ActivationRequestListSchema(tests_api_schemas.ListSchema):
    def __init__(self, *args, **kwargs):
        super(ActivationRequestListSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['items'] = {
            'type': 'object',
            'properties': tests_api_constants.ACTIVATION_REQUEST_SCHEMA
        }


class ActivationRequestDeploySchema(tests_api_schemas.BishopApiSchema):
    pass
