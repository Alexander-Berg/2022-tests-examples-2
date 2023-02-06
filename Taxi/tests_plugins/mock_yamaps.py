import pytest

from taxi_tests import json_util


class YamapsContext:
    def __init__(self):
        self.locations = {}
        self.uri_points = {}

    def location_add(self, point, response, lang='ru', uri=None):
        key = make_key(point, lang)
        self.locations[key] = response
        if uri:
            self.uri_points[uri] = point

    def location_get(self, point, lang):
        key = make_key(point, lang)
        return self.locations.get(key, {})

    def location_get_uri(self, uri, lang):
        point = self.get_point_by_uri(uri)
        return self.location_get(point, lang)

    def get_point_by_uri(self, uri):
        return self.uri_points[uri]


def make_key(point, lang):
    return '%.04f,%04f,%s' % (point[0], point[1], lang)


@pytest.fixture(autouse=True)
def yamaps(mockserver, load_json):
    context = YamapsContext()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        if 'll' not in request.args and 'uri' not in request.args:
            return mockserver.make_response('not implemented', 501)

        lang = request.args.get('lang')
        if 'uri' in request.args:
            uri = request.args['uri']
            if uri == 'empty_object':
                return load_json('yamaps-empty-response.json')

            variables = {
                'point': context.get_point_by_uri(uri),
                'short_text': request.args.get('text', ''),
                'full_text': request.args.get('text', ''),
                'description': request.args.get('text', ''),
            }
            variables.update(context.location_get_uri(uri, lang))
        else:

            point = list(map(float, request.args['ll'].split(',')))
            variables = {
                'point': point,
                'short_text': request.args.get('text', ''),
                'full_text': request.args.get('text', ''),
                'description': request.args.get('text', ''),
            }
            variables.update(context.location_get(point, lang))
        return load_json(
            'yamaps-default-response.json',
            object_hook=json_util.VarHook(variables),
        )

    return context


@pytest.fixture
def maps_router(mockserver, load_binary):
    @mockserver.json_handler('/maps-router/route_jams/')
    def route_jams(request):
        assert request.headers['Accept'] == 'application/x-protobuf'
        return mockserver.make_response(
            load_binary('route_jams.protobuf'),
            content_type='application/x-protobuf',
        )
