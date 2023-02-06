import jsonschema

import metrika.admin.python.cms.frontend.tests.api.walle.schemas.constants as schemas_constants


class WalleApiSchema:
    def __init__(self,
                 data,
                 schema,
                 ):
        self.data = data
        self.schema = schema

    def validate(self):
        jsonschema.validate(
            self.data,
            self.schema,
        )
        return True


class PostSchema(WalleApiSchema):
    def __init__(self,
                 data,
                 ):
        super(PostSchema, self).__init__(
            data,
            schemas_constants.POST_RESPONSE,
        )


class GetSchema(WalleApiSchema):
    def __init__(self,
                 data,
                 ):
        super(GetSchema, self).__init__(
            data,
            schemas_constants.GET_RESPONSE,
        )


class GetListSchema(WalleApiSchema):
    def __init__(self,
                 data,
                 ):
        super(GetListSchema, self).__init__(
            data,
            schemas_constants.GET_LIST_RESPONSE,
        )


class ErrorSchema(WalleApiSchema):
    def __init__(self,
                 data,
                 ):
        super(ErrorSchema, self).__init__(
            data,
            schemas_constants.ERROR_RESPONSE,
        )
