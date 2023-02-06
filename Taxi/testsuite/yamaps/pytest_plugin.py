import copy
import json

from google.protobuf import json_format
import pytest
# pylint: disable=import-error
from yandex.maps.proto.arrival import arrival_pb2  # noqa: F401
from yandex.maps.proto.common2 import response_pb2
from yandex.maps.proto.search import address_pb2  # noqa: F401
from yandex.maps.proto.search import business_pb2  # noqa: F401
from yandex.maps.proto.search import experimental_pb2  # noqa: F401
from yandex.maps.proto.search import geocoder_internal_pb2  # noqa: F401
from yandex.maps.proto.search import geocoder_pb2  # noqa: F401
from yandex.maps.proto.search import kind_pb2  # noqa: F401
from yandex.maps.proto.search import photos_2x_pb2  # noqa: F401
from yandex.maps.proto.search import precision_pb2  # noqa: F401
from yandex.maps.proto.search import references_pb2  # noqa: F401
from yandex.maps.proto.search import search_internal_pb2  # noqa: F401
from yandex.maps.proto.search import search_pb2  # noqa: F401
from yandex.maps.proto.uri import uri_pb2  # noqa: F401

RESPONSE_METADATA = '[yandex.maps.proto.search.search.RESPONSE_METADATA]'
RESPONSE_INFO = '[yandex.maps.proto.search.search_internal.RESPONSE_INFO]'

GEOCODER_METADATA = '[yandex.maps.proto.search.geocoder.GEO_OBJECT_METADATA]'
BUSINESS_METADATA = '[yandex.maps.proto.search.business.GEO_OBJECT_METADATA]'
URI_METADATA = '[yandex.maps.proto.uri.GEO_OBJECT_METADATA]'
ARRIVAL_METADATA = '[yandex.maps.proto.arrival.GEO_OBJECT_METADATA]'
EXPERIMENTAL_METADATA = (
    '[yandex.maps.proto.search.experimental.GEO_OBJECT_METADATA]'
)
REFERENCES_METADATA = (
    '[yandex.maps.proto.search.references.GEO_OBJECT_METADATA]'
)
PHOTOS_2X_METADATA = '[yandex.maps.proto.search.photos_2x.GEO_OBJECT_METADATA]'

QR_PAYMENT_SNIPPET_KEY = 'qr_payment/1.x'


def _yamaps_json_to_protobuf(json_dict):
    msg = response_pb2.Response()
    json_format.ParseDict(json_dict, msg)
    return msg.SerializeToString(deterministic=True)


def _get_raw_address(address):
    result = {
        'formatted_address': address['formatted_address'],
        'country_code': 'RU',
        'component': [],
    }
    if 'country' in address:
        result['component'].append(
            {'name': address['country'], 'kind': ['COUNTRY']},
        )
    if 'locality' in address:
        result['component'].append(
            {'name': address['locality'], 'kind': ['LOCALITY']},
        )
    if 'street' in address:
        result['component'].append(
            {'name': address['street'], 'kind': ['STREET']},
        )
    if 'house' in address:
        result['component'].append(
            {'name': address['house'], 'kind': ['HOUSE']},
        )
    if 'entrance' in address:
        result['component'].append(
            {'name': address['entrance'], 'kind': ['ENTRANCE']},
        )
    if 'level' in address:
        result['component'].append(
            {'name': address['level'], 'kind': ['LEVEL']},
        )
    if 'apartment' in address:
        result['component'].append(
            {'name': address['apartment'], 'kind': ['APARTMENT']},
        )
    # empty kind component
    result['component'].append({'name': 'empty_component'})
    return result


def _get_raw_business(formatted):
    # see schemas/proto/yandex/maps/proto/search/business.proto for details
    result = {
        'id': formatted['id'],
        'name': formatted['name'],
        'address': _get_raw_address(formatted['address']),
        'short_name': formatted.get('short_name', formatted['name']),
        'geocode_result': {'house_precision': 'EXACT'},
        'closed': formatted.get('closed', None),
    }
    if 'categories' in formatted and 'class' in formatted:
        raise RuntimeError(
            'both categories and class specified for an org, '
            'please use either of these formats',
        )
    if 'categories' in formatted:
        result['category'] = []
        for category in formatted['categories']:
            cat_class = category['class']
            result['category'].append(
                {
                    'name': category.get('name', f'name_{cat_class}'),
                    'class': cat_class,
                    'tag': category.get('tags', []),
                },
            )
    if 'class' in formatted:
        tags = []
        if 'rubric_id' in formatted:
            rubric_id = formatted['rubric_id']
            tags.append(f'id:{rubric_id}')
        cat_class = formatted['class']
        result['category'] = [
            {'name': f'name_{cat_class}', 'class': cat_class, 'tag': tags},
        ]
    if 'chains' in formatted:
        result['chain'] = []
        for chain in formatted['chains']:
            result['chain'].append(
                {'id': chain.get('id', ''), 'name': chain.get('name', '')},
            )
    if 'phones' in formatted:
        # type is enum [PHONE, FAX, PHONE_FAX]
        # formatted: string
        # details: {country, prefix, number, ext} - all optional strings
        result['phone'] = []
        for fmt_phone in formatted['phones']:
            phone = copy.deepcopy(fmt_phone)
            phone['number'] = 1337  # required deprecated field
            result['phone'].append(phone)
    if 'open_hours' in formatted:
        # see schemas/proto/yandex/maps/proto/search/hours.proto
        result['open_hours'] = formatted['open_hours']
    if 'distance' in formatted:
        result['distance'] = formatted['distance']

    return result


def _get_raw_geo_object(formatted):
    result = {
        'metadata': [],
        'geometry': [
            {
                'point': {
                    'lon': formatted['geometry'][0],
                    'lat': formatted['geometry'][1],
                },
            },
        ],
        'name': formatted['name'],
        'description': formatted['description'],
    }
    if 'geocoder' in formatted:
        geocoder = formatted['geocoder']
        result['metadata'].append(
            {
                GEOCODER_METADATA: {
                    'house_precision': geocoder.get('precision', 'EXACT'),
                    'address': _get_raw_address(geocoder['address']),
                    'id': geocoder.get('id', None),
                },
            },
        )
    if 'business' in formatted:
        result['metadata'].append(
            {BUSINESS_METADATA: _get_raw_business(formatted['business'])},
        )
    if 'uri' in formatted:
        result['metadata'].append(
            {URI_METADATA: {'uri': [{'uri': formatted['uri']}]}},
        )
    if 'arrival_points' in formatted:
        arrival_points = []
        for ar_point in formatted['arrival_points']:
            arrival_points.append(
                {
                    'point': {
                        'lon': ar_point['point'][0],
                        'lat': ar_point['point'][1],
                    },
                    'name': ar_point['name'],
                },
            )
        result['metadata'].append(
            {ARRIVAL_METADATA: {'arrival_point': arrival_points}},
        )
    if 'qr_payment_snippet' in formatted:
        # see schemas/proto/yandex/maps/proto/search/experimental.proto
        result['metadata'].append(
            {
                EXPERIMENTAL_METADATA: {
                    'experimental_storage': {
                        'item': [
                            {
                                'key': QR_PAYMENT_SNIPPET_KEY,
                                'value': json.dumps(
                                    formatted['qr_payment_snippet'],
                                ),
                            },
                        ],
                    },
                },
            },
        )
    if 'references' in formatted:
        # see schemas/proto/yandex/maps/proto/search/references.proto
        result['metadata'].append(
            {REFERENCES_METADATA: {'reference': formatted['references']}},
        )
    if 'photos' in formatted:
        # see schemas/proto/yandex/maps/proto/search/photos_2x.proto
        result['metadata'].append(
            {
                PHOTOS_2X_METADATA: {
                    'count': formatted['photos'].get('count', 322),
                    'photo': formatted['photos']['items'],
                },
            },
        )

    return result


def _get_raw_bbox(formatted):
    lon1, lat1, lon2, lat2 = formatted
    assert lon1 < lon2
    assert lat1 < lat2
    return {
        'lower_corner': {'lon': lon1, 'lat': lat1},
        'upper_corner': {'lon': lon2, 'lat': lat2},
    }


def _get_raw_metadata(formatted):
    result = {}
    result['found'] = formatted['found']
    result['bounded_by'] = _get_raw_bbox(formatted['bounded_by'])
    result[RESPONSE_INFO] = {
        'context': 'some_context',
        'display': 'MULTIPLE',
        'reqid': 'some_requid',
        'serpid': 'some_serpid',
    }
    return [{RESPONSE_METADATA: result}]


@pytest.fixture(name='yamaps')
def mock_yamaps(mockserver, load_json):
    class Context:
        def __init__(self):
            self.geo_objects = []
            self.metadata = []
            self.request_checks = None
            self.fmt_geo_objects_callback = None
            self.debug_logs_enabled = False

        def add_geo_object(self, geo_object):
            self.geo_objects.append(geo_object)

        def set_fmt_geo_objects(self, fmt_objects):
            self.geo_objects = [
                _get_raw_geo_object(fmt) for fmt in fmt_objects
            ]

        def add_fmt_geo_object(self, formatted):
            self.add_geo_object(_get_raw_geo_object(formatted))

        def set_fmt_metadata(self, formatted):
            self.metadata = _get_raw_metadata(formatted)

        def set_fmt_response(self, response):
            self.set_fmt_geo_objects(response['geoobjects'])
            self.set_fmt_metadata(response['metadata'])

        def set_checks(self, checks):
            self.request_checks = checks

        def set_fmt_geo_objects_callback(self, callback):
            self.fmt_geo_objects_callback = callback

        def enable_debug_logging(self):
            self.debug_logs_enabled = True

        def create_response(self, request):
            geo_objects = self.geo_objects
            if self.fmt_geo_objects_callback:
                fmt_items = self.fmt_geo_objects_callback(request)
                geo_objects = [_get_raw_geo_object(fmt) for fmt in fmt_items]
            response = {
                'reply': {
                    'geo_object': geo_objects,
                    'metadata': self.metadata,
                },
            }
            if self.debug_logs_enabled:
                print(
                    '[DEBUG] yamaps response for',
                    request.args,
                    ':',
                    json.dumps(response, ensure_ascii=False, indent=2),
                )
            return response

        def times_called(self):
            return mock_geosearch.times_called

    context = Context()

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_geosearch(request):
        assert 'results' in request.args
        if 'uri' in request.args:
            assert 'type' not in request.args
        else:
            assert 'type' in request.args
            assert 'text' in request.args or 'business_oid' in request.args
        if context.request_checks:
            checked_keys = {
                key: value
                for key, value in request.args.items()
                if key in context.request_checks
            }
            assert checked_keys == context.request_checks
        return mockserver.make_response(
            _yamaps_json_to_protobuf(context.create_response(request)),
        )

    return context
