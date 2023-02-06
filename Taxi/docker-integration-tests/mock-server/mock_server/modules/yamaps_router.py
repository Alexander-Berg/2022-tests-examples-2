from aiohttp import web

from mock_server.modules.common import geometry
from .common.yandex_pb.yandex.maps.proto.common2 import attribution_pb2  # noqa
from .common.yandex_pb.yandex.maps.proto.common2 import geo_object_pb2  # noqa
from .common.yandex_pb.yandex.maps.proto.common2 import geometry_pb2  # noqa
from .common.yandex_pb.yandex.maps.proto.common2 import i18n_pb2  # noqa
from .common.yandex_pb.yandex.maps.proto.common2 import metadata_pb2  # noqa
from .common.yandex_pb.yandex.maps.proto.common2 import response_pb2  # noqa

from .common.yandex_pb.yandex.maps.proto.driving import annotation_pb2  # noqa
from .common.yandex_pb.yandex.maps.proto.driving import flags_pb2  # noqa
from .common.yandex_pb.yandex.maps.proto.driving import route_pb2  # noqa
from .common.yandex_pb.yandex.maps.proto.driving import section_pb2  # noqa
from .common.yandex_pb.yandex.maps.proto.driving import summary_pb2  # noqa
from .common.yandex_pb.yandex.maps.proto.driving import weight_pb2  # noqa


AVG_SPEED = 8.
TRAFFIC_COEFFICIENT = 1


def _to_sint32(val):
    return int(val[0] * 1000000), int(val[1] * 1000000)


class RoutePB2:
    def __init__(self, first_point, final_point):
        distance = geometry.approx_distance(first_point, final_point)
        time_ = distance / AVG_SPEED

        self._time = time_
        self._time_with_traffic = time_ * TRAFFIC_COEFFICIENT
        self._distance = distance

    def _get_weight(self):
        time = i18n_pb2.LocalizedValue(value=self._time, text=str(self._time))
        time_with_traffic = i18n_pb2.LocalizedValue(
            value=self._time_with_traffic, text=str(self._time_with_traffic),
        )
        distance = i18n_pb2.LocalizedValue(
            value=self._distance, text=str(self._distance),
        )

        weight = weight_pb2.Weight(
            time=time, time_with_traffic=time_with_traffic, distance=distance,
        )
        return weight

    @staticmethod
    def _get_flags():
        return flags_pb2.Flags(
            blocked=False,
            has_tolls=False,
            has_ferries=False,
            crosses_borders=False,
            requires_access_pass=False,
        )

    @staticmethod
    def _get_annotation():
        return annotation_pb2.Annotation(
            description='Test annotation description',
            action_metadata=annotation_pb2.ActionMetadata(),
        )

    def generate_route(self):
        return route_pb2.Route(
            weight=self._get_weight(),
            flags=self._get_flags(),
        )

    def generate_section(self):
        return section_pb2.Section(
            leg_index=0,
            weight=self._get_weight(),
            annotation=self._get_annotation(),
        )

    def generate_summary(self):
        summary = summary_pb2.Summary(
            weight=self._get_weight(),
            flags=self._get_flags(),
        )
        return summary_pb2.Summaries(summaries=[summary])


class ResponseBuilder:
    def __init__(self, routes):
        self._routes = routes

    @staticmethod
    def _get_geometry(route):
        route32 = [_to_sint32(val) for val in route]
        lon, lat = route32[0]
        lon_deltas = [b[0] - a[0] for a, b in zip(route32, route32[1:])]
        lat_deltas = [b[1] - a[1] for a, b in zip(route32, route32[1:])]
        lon_seq = geometry_pb2.CoordSequence(first=lon, deltas=lon_deltas)
        lat_seq = geometry_pb2.CoordSequence(first=lat, deltas=lat_deltas)

        road = geometry_pb2.Polyline(lons=lon_seq, lats=lat_seq)
        return geometry_pb2.Geometry(polyline=road)

    @staticmethod
    def _get_bounding_box(route):
        lon1, lat1 = route[0]
        lon2, lat2 = route[-1]
        lower_corner = geometry_pb2.Point(
            lat=max(lat1, lat2), lon=max(lon1, lon2),
        )
        upper_corner = geometry_pb2.Point(
            lat=min(lat1, lat2), lon=min(lon1, lon2),
        )

        return geometry_pb2.BoundingBox(
            lower_corner=lower_corner,
            upper_corner=upper_corner,
        )

    @staticmethod
    def _get_metadata(route, metadata_type):
        route = RoutePB2(route[0], route[-1])

        if metadata_type == route_pb2.ROUTE_METADATA:
            route_for_result = route.generate_route()
        else:
            route_for_result = route.generate_section()

        metadata = metadata_pb2.Metadata()
        # pylint: disable=no-member
        metadata.Extensions[
            metadata_type
        ].CopyFrom(route_for_result)
        return metadata

    def generate_summary(self):
        return RoutePB2(
            self._routes[0][0],
            self._routes[-1][-1],
        ).generate_summary()

    def generate_full(self):
        boundaries = [self._routes[0][0], self._routes[-1][-1]]

        inner_geos = [geo_object_pb2.GeoObject(
            bounded_by=self._get_bounding_box(route),
            metadata=[self._get_metadata(route, section_pb2.SECTION_METADATA)],
            geometry=[self._get_geometry(route)],
        ) for route in self._routes]
        middle_geo = geo_object_pb2.GeoObject(
            metadata=[
                self._get_metadata(boundaries, route_pb2.ROUTE_METADATA),
            ],
            geo_object=inner_geos,
        )
        outer_geo = geo_object_pb2.GeoObject(
            bounded_by=self._get_bounding_box(boundaries),
            geo_object=[middle_geo],
        )

        attribution_map = attribution_pb2.AttributionMap()

        response = response_pb2.Response(
            attribution=attribution_map,
            reply=outer_geo,
        )

        return response


class Application(web.Application):
    def __init__(self):
        super().__init__()

        # Handlers
        self.router.add_get('/route/', self.handle)
        self.router.add_get('/route_jams/', self.handle)

    def handle(self, request):
        # /?lang=ru-RU
        # &origin=yataxi
        # &rll=37.58799716,55.73452861~37.900479,55.414348
        # &output=all
        # &intent=TAXIONTHEWAY
        # &user_id=
        source, destination = self.parse_path(request)
        report_builder = ResponseBuilder(
            [[source, destination, destination]],
        )

        if request.query.get('output') == 'time':
            answer_body = report_builder.generate_summary()
        else:
            answer_body = report_builder.generate_full()

        return web.Response(
            body=answer_body.SerializeToString(),
            content_type='application/x-protobuf',
        )

    @staticmethod
    def parse_path(request):
        text = request.query['rll']
        assert '~' in text
        source, destination, *_ = [
            val.split(',') for val in text.split('~')
        ]

        def to_float(lst):
            return [float(val) for val in lst]

        return to_float(source), to_float(destination)
