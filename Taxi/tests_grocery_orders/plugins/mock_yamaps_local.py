import pytest


@pytest.fixture(name='yamaps_local', autouse=True)
def mock_yamaps_local(mockserver, load_json, yamaps):
    class Context:
        def __init__(self):
            self.uri = None
            self.location = None
            self.lang = None
            self.country = None
            self.city = None
            self.street = None
            self.house = None
            self.text_addr = None
            self.place_id = None
            self.is_empty_response = None

        def set_data(
                self,
                uri=None,
                location=None,
                country=None,
                city=None,
                street=None,
                house=None,
                text_addr=None,
                place_id=None,
                lang=None,
                is_empty_response=None,
        ):
            if uri is not None:
                self.uri = uri
            if location is not None:
                self.location = location
            if country is not None:
                self.country = country
            if city is not None:
                self.city = city
            if street is not None:
                self.street = street
            if house is not None:
                self.house = house
            if text_addr is not None:
                self.text_addr = text_addr
            if place_id is not None:
                self.place_id = place_id
            if lang is not None:
                self.lang = lang
            if is_empty_response is not None:
                self.is_empty_response = is_empty_response

        def create_geo_object(self):
            geo_object = load_json('geocoder-response.json')
            addr = geo_object['geocoder']['address']
            if self.country is not None:
                addr['country'] = self.country
            if self.city is not None:
                addr['locality'] = self.city
            if self.street is not None:
                addr['street'] = self.street
            if self.house is not None:
                addr['house'] = self.house
            if self.place_id is not None:
                geo_object['uri'] = self.place_id
            if self.location:
                geo_object['geometry'] = [
                    float(value) for value in self.location.split(',')
                ]
            return geo_object

        def times_called(self):
            return yamaps.times_called()

    context = Context()

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        if context.is_empty_response:
            return {}
        if context.uri:
            assert request.args['uri'] == context.uri
        if context.location:
            if 'ull' in request.args:
                assert request.args['ull'] == context.location
            elif 'll' in request.args:
                assert request.args['ll'] == context.location
            else:
                assert False  # no coordinates in response
        if context.text_addr:
            assert request.args['text'] == context.text_addr
        if context.lang:
            assert request.args['lang'] == context.lang
        return [context.create_geo_object()]

    return context
