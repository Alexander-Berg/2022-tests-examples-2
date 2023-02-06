# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import json
import uuid

from google.protobuf import json_format
import pytest
from yandex.maps.proto.common2.geo_object_pb2 import GeoObject
from yandex.maps.proto.common2.geometry_pb2 import Geometry
from yandex.maps.proto.common2.metadata_pb2 import Metadata
from yandex.maps.proto.common2.response_pb2 import Response
from yandex.maps.proto.masstransit.common_pb2 import Stop
from yandex.maps.proto.masstransit.line_pb2 import LINE_METADATA
from yandex.maps.proto.masstransit.stop_pb2 import BriefSchedule
from yandex.maps.proto.masstransit.stop_pb2 import LineAtStop
from yandex.maps.proto.masstransit.stop_pb2 import STOP_METADATA
from yandex.maps.proto.masstransit.stop_pb2 import ThreadAtStop

from masstransit_plugins import *  # noqa: F403 F401


def pytest_configure(config):
    config.addinivalue_line('markers', 'mtinfo: mtinfo')
    config.addinivalue_line('markers', 'stops_file: stops file')


@pytest.fixture(autouse=True)
def mock_stops_cache_proxy(
        request, mockserver, pytestconfig, load_json, build_dir,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/shuttles/list',
    )
    def handler_shuttle_shuttles_list(request):
        response = load_json('shuttles_list.json')
        if 'shuttle_ids' in request.json:
            return [
                item
                for item in response
                if item['id'] in request.json['shuttle_ids']
            ]
        return response

    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/stops/list',
    )
    def handler_shuttle_stops_list(request):
        return load_json('shuttle_stops.json')

    # pylint: disable=unused-variable
    @mockserver.json_handler('/sandbox/api/v1.0/resource')
    def handler_sandbox_resource(request):
        req_id = uuid.uuid4().int & ((1 << 63) - 1)
        proxy = mockserver.url('sandbox/1')
        response = {'items': [{'id': req_id, 'http': {'proxy': proxy}}]}
        return response

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/routes/list',
    )
    def handler_shuttle_routes_list(request):
        return []

    markers = list(request.node.iter_markers('stops_file'))

    # pylint: disable=unused-variable
    @mockserver.json_handler('/sandbox/1/stops')
    def handler_sandbox_1_stops(request):
        result = ''
        if markers:
            for marker in markers:
                data = load_json(marker.kwargs['filename'])
                for stop in data['stops']:
                    result += stop['id'] + '\t'
                    result += stop['parent_id'] + '\t'
                    result += stop['name'] + '\t'
                    result += stop['type'] + '\t'
                    result += str(stop['lat']) + '\t'
                    result += str(stop['lon']) + '\n'
        # hack to fight with the empty cache
        result += '-' + '\t'
        result += '-' + '\t'
        result += '-' + '\t'
        result += 'stop' + '\t'
        result += '1000' + '\t'
        result += '1000' + '\n'

        return mockserver.make_response(result)

    # pylint: disable=unused-variable
    @mockserver.json_handler('/sandbox/1/thread_stops')
    def handler_sandbox_1_thread_stops(request):
        return mockserver.make_response(
            '\n'.join(
                '\t'.join([thread_id, '-', stop['id']])
                for marker in markers
                for stop in load_json(marker.kwargs['filename'])['stops']
                for thread_id in stop.get('threads') or []
            ),
        )

    # pylint: disable=unused-variable
    @mockserver.json_handler('/sandbox/1/threads')
    def handler_sandbox_1_threads(request):
        return mockserver.make_response(
            '\n'.join(
                '\t'.join([thread_id, route['id']])
                for marker in markers
                for route in load_json(marker.kwargs['filename'])['routes']
                for thread_id in route.get('threads') or []
            ),
        )

    # pylint: disable=unused-variable
    @mockserver.json_handler('/sandbox/1/routes')
    def handler_sandbox_1_routes(request):
        return mockserver.make_response(
            '\n'.join(
                '\t'.join(
                    [
                        route['id'],
                        route['type'],
                        route['name'],
                        route.get('color') or '',
                        route.get('uri') or '',
                        route.get('time_zone') or '',
                    ],
                )
                for marker in markers
                for route in load_json(marker.kwargs['filename'])['routes']
            ),
        )

    # pylint: disable=unused-variable
    @mockserver.json_handler('/sandbox/1/transitions')
    def handler_sandbox_1_transitions(request):
        return mockserver.make_response(
            '\n'.join(
                '\t'.join([src_stop['id'], dst_stop, str(duration)])
                for marker in markers
                for src_stop in load_json(marker.kwargs['filename'])['stops']
                for dst_stop, duration in src_stop.get(
                    'transitions', {},
                ).items()
            ),
        )


def get_schedule_entry(json_bs):
    schedule_entry = BriefSchedule.ScheduleEntry()
    if 'scheduled' in json_bs:
        json_format.Parse(
            json.dumps(json_bs['scheduled']), schedule_entry.scheduled,
        )
    if 'periodical' in json_bs:
        json_format.Parse(
            json.dumps(json_bs['periodical']), schedule_entry.periodical,
        )
    return schedule_entry


def get_essential_stop(json_stop):
    essential_stop = Stop()
    essential_stop.id = json_stop['id']
    essential_stop.name = json_stop['name']
    return essential_stop


def serialize_line(line):
    line_md = LineAtStop()
    line_md.line.id = line['line']['id']
    line_md.line.name = line['line']['name']
    line_md.line.vehicle_type.extend([line['line']['vehicle_type']])
    thread = ThreadAtStop()
    thread.brief_schedule.schedule_entry.extend(
        [
            get_schedule_entry(x)
            for x in line['thread_at_stop']['brief_schedule']
        ],
    )
    thread.thread.id = line['thread_at_stop']['thread']['id']
    thread.thread.essential_stop.extend(
        [
            get_essential_stop(x)
            for x in line['thread_at_stop']['thread']['essential_stop']
        ],
    )
    thread.no_boarding = False
    thread.no_drop_off = False
    line_md.thread_at_stop.extend([thread])
    return line_md


def process_stops(stops):
    res = Response()
    reply = res.reply
    for stop in stops:
        stop_go = GeoObject()
        geometry = Geometry()
        geometry.point.lon = stop['point']['lon']
        geometry.point.lat = stop['point']['lat']
        stop_go.geometry.extend([geometry])
        metadata = Metadata()
        stop_md = metadata.Extensions[STOP_METADATA]
        stop_md.stop.id = stop['stop']['id']
        stop_md.stop.name = stop['stop']['name']
        stop_md.line_at_stop.extend(
            [serialize_line(x) for x in stop['line_at_stop']],
        )
        stop_go.metadata.extend([metadata])
        reply.geo_object.extend([stop_go])
    return res.SerializeToString()


def process_line(line):
    res = Response()
    reply = res.reply
    line_go = GeoObject()
    metadata = Metadata()
    line_md = metadata.Extensions[LINE_METADATA]
    json_format.Parse(json.dumps(line['line']), line_md.line)
    line_go.metadata.extend([metadata])
    reply.geo_object.extend([line_go])
    return res.SerializeToString()


@pytest.fixture(autouse=True)
def mock_mtinfo_proto(request, mockserver, pytestconfig, load_json, build_dir):
    markers = list(request.node.iter_markers('mtinfo'))
    stops = {}
    lines = {}
    vehicles = {}
    if markers:
        for marker in markers:
            if 'v2_stop' in marker.kwargs:
                data = load_json(marker.kwargs['v2_stop'])
                stops.update(data)
            if 'v2_line' in marker.kwargs:
                data = load_json(marker.kwargs['v2_line'])
                lines.update(data)
            if 'v2_vehicle' in marker.kwargs:
                data = load_json(marker.kwargs['v2_vehicle'])
                vehicles.update(data)

    # pylint: disable=unused-variable
    @mockserver.json_handler('/mtinfo/v2/stop')
    def mtinfo_v2_stop(request):
        stop_ids = request.args['id'].split(',')
        stops_data = []
        try:
            stops_data.extend([stops[stop_id] for stop_id in stop_ids])
        except KeyError as exc:
            return mockserver.make_response(f'Not found, {exc}', status=404)
        return mockserver.make_response(
            process_stops(stops_data), content_type='application/x-protobuf',
        )

    # pylint: disable=unused-variable
    @mockserver.json_handler('/mtinfo/v2/line')
    def mtinfo_v2_line(request):
        line_id = request.args['id']
        if line_id not in lines:
            return mockserver.make_response('Not found', status=404)
        return mockserver.make_response(
            process_line(lines[line_id]),
            content_type='application/x-protobuf',
        )
