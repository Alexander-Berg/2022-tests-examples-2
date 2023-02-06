NAME = 'parks'


def _handler_driver_profiles_list(context):
    def handler(request):
        offset = request.json.get('offset', 0)
        limit = request.json.get('limit', 100)
        query = request.json.get('query', {})

        park = query.get('park', {})
        park_id = park.get('id')
        park_dp = park.get('driver_profile', {})

        contractor_id_set = park_dp.get('id')
        # dp_wr = park_dp.get('work_rule_id')
        # dp_ws = park_dp.get('work_status')

        parks = []
        contractors = []
        for park in context['taxi']['parks']:
            if park['id'] != park_id:
                continue
            for contractor in context['taxi']['contractors']:
                if contractor['park_id'] != park_id:
                    continue
                if (
                        contractor_id_set
                        and contractor['id'] not in contractor_id_set
                ):
                    continue
                contractors.append(contractor)
            parks.append(park)

        return {
            'limit': limit,
            'offset': offset,
            'driver_profiles': [
                {
                    'driver_profile': {
                        'id': contractor['id'],
                        'first_name': contractor['name'],
                    },
                }
                for contractor in contractors[offset : offset + limit]
            ],
            'parks': [{'id': park['id']} for park in parks],
            'total': len(contractors),
        }

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add('/driver-profiles/list', _handler_driver_profiles_list(context))

    return mocks
