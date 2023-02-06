NAME = 'fleet-parks'


def _handler_parks_list_post(context, mockserver):
    def handler(request):
        park_id = request.json['query']['park']['ids'][0]
        return {
            'parks': [
                {
                    'id': park_id,
                    'login': 'hahaha',
                    'name': 'HaHaHa',
                    'is_active': True,
                    'city_id': 'Moscow',
                    'locale': 'ru',
                    'is_billing_enabled': True,
                    'is_franchising_enabled': True,
                    'country_id': 'rus',
                    'provider_config': {
                        'type': 'none',
                        'clid': 'clid_' + park_id,
                    },
                    'demo_mode': False,
                    'geodata': {'lon': 53, 'lat': 57, 'zoom': 1},
                },
            ],
        }

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/v1/parks/list', _handler_parks_list_post(context, mockserver))

    return mocks
