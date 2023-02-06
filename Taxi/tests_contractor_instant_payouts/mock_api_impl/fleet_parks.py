NAME = 'fleet-parks'


def _handler_v1_parks_list(context):
    def handler(request):
        parks = []

        for park_id in request.json['query']['park']['ids']:
            for park in context['taxi']['parks']:
                if park['id'] == park_id:
                    parks.append(park)
                    break

        return {
            'parks': [
                {
                    'id': park['id'],
                    'login': 'TESTSUITE',
                    'name': 'TESTSUITE',
                    'is_active': True,
                    'is_billing_enabled': True,
                    'is_franchising_enabled': False,
                    'demo_mode': False,
                    'country_id': 'TESTSUITE',
                    'city_id': 'TESTSUITE',
                    'locale': 'TESTSUITE',
                    'provider_config': {
                        'type': 'production',
                        'clid': park['clid'],
                    },
                    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
                    'tz_offset': 3,
                }
                for park in parks
            ],
        }

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/v1/parks/list', _handler_v1_parks_list(context))

    return mocks
