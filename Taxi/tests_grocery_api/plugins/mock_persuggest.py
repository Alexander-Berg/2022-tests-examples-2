import pytest


@pytest.fixture(name='persuggest', autouse=True)
def mock_persuggest(mockserver):
    class Context:
        def __init__(self):
            self.building_id = None
            self.place_id = None
            self.status = None
            self.country = None
            self.country_code = None
            self.postal_code = None
            self.address_info = None
            self.house = None

        def set_data(
                self,
                building_id=None,
                place_id=None,
                country=None,
                country_code=None,
                postal_code=None,
                status=None,
                house=None,
        ):
            self.building_id = building_id
            self.place_id = place_id
            self.country = country
            self.country_code = country_code
            self.postal_code = postal_code
            self.status = status
            self.house = house

            self.address_info = {
                'ru': {
                    'subtitle_text': 'Москва, Россия',
                    'title_text': 'Симферопольский бульвар, 24к1',
                    'city': 'Москва',
                    'street': 'Варшавское шоссе',
                },
                'en': {
                    'subtitle_text': 'Moscow, Russian Federation',
                    'title_text': 'Simferopolsky Boulevard, 24к1',
                    'city': 'Moscow',
                    'street': 'Varshavskoye Highway',
                },
            }

        @property
        def times_called(self):
            return finalsuggest.times_called

    context = Context()

    @mockserver.json_handler('/persuggest/4.0/persuggest/v1/finalsuggest')
    def finalsuggest(request):
        persuggest_location = request.json['position']
        persuggest_locale = request.headers['X-Request-Language']
        if context.status:
            return mockserver.make_response(status=context.status)
        return mockserver.make_response(
            json={
                'results': [
                    {
                        'lang': '',
                        'log': 'some_log',
                        'method': 'fs_finalize_toponym_eats',
                        'building_id': context.building_id,
                        'position': persuggest_location,
                        'subtitle': {
                            'text': context.address_info[persuggest_locale][
                                'subtitle_text'
                            ],
                            'hl': [],
                        },
                        'text': 'some_text',
                        'title': {
                            'text': context.address_info[persuggest_locale][
                                'title_text'
                            ],
                            'hl': [],
                        },
                        'uri': context.place_id,
                        'type': 'address',
                        'country': context.country,
                        'country_code': context.country_code,
                        'city': context.address_info[persuggest_locale][
                            'city'
                        ],
                        'street': context.address_info[persuggest_locale][
                            'street'
                        ],
                        'house': context.house,
                        'postal_code': context.postal_code,
                    },
                ],
                'zones': {'nearest_zones': []},
                'points': [],
                'points_icon_image_tag': 'custom_pp_icon_black_test',
                'typed_experiments': {
                    'version': 690955,
                    'items': [
                        {
                            'name': 'stick_to_eats_address',
                            'value': {'enabled': True, 'filter_distance': 100},
                        },
                    ],
                },
                'services': {
                    'taxi': {'available': True, 'nearest_zone': 'moscow'},
                },
            },
            status=200,
        )

    return context
