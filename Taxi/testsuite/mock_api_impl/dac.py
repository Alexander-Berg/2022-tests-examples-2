NAME = 'dispatcher-access-control'


def _handler_create(context):
    def handler(request):
        print(request.json)
        return {
            'offset': 0,
            'users': [
                {
                    'id': uid + '_ID',
                    'park_id': request.json['query']['park']['id'],
                    'passport_uid': uid,
                    'display_name': uid + '_NAME',
                    'is_enabled': True,
                    'is_confirmed': True,
                    'is_superuser': False,
                    'is_usage_consent_accepted': True,
                }
                for uid in request.json['query']['user']['passport_uid']
            ],
        }

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/v1/parks/users/list', _handler_create(context))

    return mocks
