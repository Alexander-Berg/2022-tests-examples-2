import jsonschema


class BishopApiSchema(object):
    def __init__(self,
                 data,
                 ):
        self.data = data
        self.schema = {
            'type': 'object',
            'properties': {
                'result': {
                    'type': 'boolean',
                },
                'errors': {
                    'type': 'array',
                },
                'data': {
                    'type': 'object',
                },
                '_meta': {
                    'type': 'object',
                    'properties': {
                        'node': {
                            'dc': 'string',
                        },
                    },
                },
                'messages': {
                    'type': 'array',
                }
            },
            'required': [
                'result',
                'errors',
                'messages',
                'data',
                '_meta',
            ],
            'additionalProperties': False,
        }

    def validate(self):
        jsonschema.validate(
            self.data,
            self.schema,
        )
        return True


class BishopAjaxSchema(BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(BishopAjaxSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['valid'] = {
            'type': 'boolean',
        }
        for item in ('actions', 'html', 'html_title', 'label'):
            self.schema['properties'][item] = {
                'type': 'string',
            }


class ErrorSchema(BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(ErrorSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['errors']['minItems'] = 1
        self.schema['properties']['result']['enum'] = [False]


class SuccessSchema(BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(SuccessSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['result']['enum'] = [True]


class SuccessMessageSchema(SuccessSchema):
    def __init__(self, *args, **kwargs):
        super(SuccessMessageSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['messages']['minItems'] = 1


class ListSchema(BishopApiSchema):
    def __init__(self, *args, **kwargs):
        super(ListSchema, self).__init__(*args, **kwargs)
        self.schema['properties']['data']['type'] = 'array'
