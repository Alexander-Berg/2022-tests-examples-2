NAME = 'driver-profiles'


def _handler_v1_driver_profiles_retrieve(context):
    def handler(request):
        undscr_id_set = request.json['id_in_set']

        contractors = []
        for undscr_id in undscr_id_set:
            park_id, contractor_id = undscr_id.split('_')
            found_contractor = None
            for contractor in context['contractors']:
                if (
                        contractor['park_id'] == park_id
                        and contractor['id'] == contractor_id
                ):
                    found_contractor = contractor
                    break
            contractors.append(found_contractor)

        return {
            'profiles': [
                {
                    'park_driver_profile_id': undscr_id,
                    'data': (
                        None
                        if contractor is None
                        else {'full_name': {'first_name': contractor['name']}}
                    ),
                }
                for undscr_id, contractor in zip(undscr_id_set, contractors)
            ],
        }

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add(
        '/v1/driver/profiles/retrieve',
        _handler_v1_driver_profiles_retrieve(context),
    )

    return mocks
