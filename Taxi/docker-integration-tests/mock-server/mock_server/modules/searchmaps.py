import collections
import math

from aiohttp import web
from google.protobuf import json_format

# pylint: disable=import-error
from .common.yandex_pb.yandex.maps.proto.common2 import response_pb2
from .common.yandex_pb.yandex.maps.proto.search import (  # noqa: F401
    business_pb2,
)


Address = collections.namedtuple(
    'Address', ['point', 'lang', 'text', 'type', 'data'],
)

BUSINESS_METADATA = '[yandex.maps.proto.search.business.GEO_OBJECT_METADATA]'


def _get_json_response(geo_objects):
    response = {'type': 'FeatureCollection', 'features': []}
    for geo_object in geo_objects:
        address = geo_object['business']['address']
        json_object = (
            {
                'type': 'Feature',
                'geometry': {'coordinates': geo_object['geometry']},
                'properties': {
                    'CompanyMetaData': {
                        'name': geo_object['business']['name'],
                        'id': geo_object['business']['id'],
                        'Geo': {'precision': 'exact'},
                        'Address': {
                            'formatted': address['formatted_address'],
                            'Components': [
                                {
                                    'kind': 'country',
                                    'name': address['country'],
                                },
                                {
                                    'kind': 'locality',
                                    'name': address['locality'],
                                },
                            ],
                        },
                    },
                },
            },
        )
        response['features'].append(json_object)

    return web.json_response(response)


def _get_proto_response(geo_objects):
    response = {'reply': {'geo_object': []}}
    for geo_object in geo_objects:
        address = geo_object['business']['address']
        proto_object = {
            'geometry': [
                {
                    'point': {
                        'lon': geo_object['geometry'][0],
                        'lat': geo_object['geometry'][1],
                    },
                },
            ],
            'metadata': [
                {
                    BUSINESS_METADATA: {
                        'name': geo_object['business']['name'],
                        'id': geo_object['business']['id'],
                        'geocode_result': {'house_precision': 'EXACT'},
                        'address': {
                            'formatted_address': address['formatted_address'],
                            'component': [
                                {
                                    'kind': ['COUNTRY'],
                                    'name': address['country'],
                                },
                                {
                                    'kind': ['LOCALITY'],
                                    'name': address['locality'],
                                },
                            ],
                        },
                    },
                },
            ],
        }
        response['reply']['geo_object'].append(proto_object)

    msg = response_pb2.Response()
    json_format.ParseDict(response, msg)
    return web.Response(
        body=msg.SerializeToString(deterministic=True),
        content_type='application/x-protobuf',
    )


def _make_response(request, geo_objects):
    if request.query['ms'] == 'json':
        return _get_json_response(geo_objects)
    return _get_proto_response(geo_objects)


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.registered_organizations = {}
        # pylint: disable=invalid-name
        self.registered_reverse_geosearch_responses = []
        self.registered_grocery_responses = []

        # Handlers
        self.router.add_get('/search', self.handle)

        # Control
        self.router.add_post(
            '/control/register_reverse_geosearch',
            self.register_reverse_geosearch,
        )

    def handle(self, request):
        if request.query.get('uri') == 'grocery':
            return self.handle_grocery_search(request)

        # GET /?format=json
        #       &lang=ru
        #       &origin=mobile-taxi
        #       &type=geo%2Cbiz
        #       &results=1
        #       &business_show_closed=1
        #       &business_oid=771484755
        if 'business_oid' in request.query:
            return self.handle_org_search(request)

        # GET /?format=json
        #      &key=...
        #      &lang=ru
        #      &origin=mobile-taxi
        #      &type=geo
        #      &results=1
        #      &ll=37.587997%2C55.734529
        #      &spn=0.001000%2C0.001000
        #      &text="Россия, Москва, улица Тимура Фрунзе, 11к8"
        if {'ll', 'text', 'type'}.issubset(request.query):
            return self.handle_reverse_geosearch(request)
        return _make_response(request, [])

    def handle_grocery_search(self, request):
        for addr in self.registered_grocery_responses:
            return _make_response(request, [addr.data])

        return _make_response(request, [])

    def handle_org_search(self, request):
        norm_lang = Application.extract_lang(request.query['lang'])
        key = (request.query['business_oid'], norm_lang)
        value = self.registered_organizations.get(key)
        if value:
            return _make_response(request, [value])
        return _make_response(request, [])

    def handle_reverse_geosearch(self, request):
        coords = [float(t) for t in request.query['ll'].split(',')]
        spn_string = request.query.get('spn', '0.1,0.1')
        spn = [float(t) for t in spn_string.split(',')]
        assert len(coords) == 2
        norm_lang = self.extract_lang(request.query['lang'])
        for addr in self.registered_reverse_geosearch_responses:
            if addr.lang != norm_lang:
                continue
            if request.query['type'] not in addr.type:
                continue
            if request.query['text'] not in (addr.text, request.query['ll']):
                continue
            if (
                    math.fabs(addr.point[0] - coords[0]) < spn[0]
                    and math.fabs(addr.point[1] - coords[1]) < spn[1]
            ):
                return _make_response(request, [addr.data])
        return _make_response(request, [])

    async def register_reverse_geosearch(self, request):
        request_data = await request.json()
        coordinates = request_data['data']['geometry']
        addr = Address(
            point=coordinates,
            lang=request_data['lang'],
            text=request_data['text'],
            type=request_data['type'],
            data=request_data['data'],
        )

        oid = request_data['data']['business']['id']

        if 'grocery' in oid:
            self.registered_grocery_responses.append(addr)
            return web.json_response({})

        if oid is not None:
            key = (oid, request_data['lang'])
            self.registered_organizations[key] = request_data['data']

        self.registered_reverse_geosearch_responses.append(addr)
        return web.json_response({})

    @staticmethod
    def extract_lang(lang):
        return lang.split('_' if '_' in lang else '-')[0].lower()
