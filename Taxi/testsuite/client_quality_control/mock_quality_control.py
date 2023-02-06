import json

import pytest


# pylint: disable=too-many-instance-attributes
class QualityControlContext:
    def __init__(self):
        self.states = {}
        self.passes = {}
        self.confirmed_data = {}
        self.pass_update_request = {}
        self.pass_update = {}
        self.pass_data_request = {}
        self.pass_data = {}
        self.resolution_status = {}
        self.pass_list_data = {}
        self.pass_list_reqs = []

    def set_state(self, exam_type, dbid_uuid, exam, filename):
        self.states['State:' + exam_type + dbid_uuid + exam] = filename

    def set_pass(self, pass_id, filename):
        self.passes['Pass:' + pass_id] = filename

    def set_confirmed_data(self, exam_type, dbid_uuid, filename):
        self.confirmed_data['Confirmed:' + exam_type + dbid_uuid] = filename

    def set_pass_update(self, pass_id, request, response):
        key = 'Update:' + pass_id
        self.pass_update_request[key] = request
        self.pass_update[key] = response

    def set_pass_data(self, pass_id, request, response):
        key = 'Data:' + pass_id
        self.pass_data_request[key] = request
        self.pass_data[key] = response

    def set_pass_list_data(self, data):
        self.pass_list_data = data

    def get_pass_list_reqs(self):
        return self.pass_list_reqs


@pytest.fixture(name='quality_control')
def _quality_control(mockserver, load_json):
    context = QualityControlContext()

    @mockserver.handler('/quality-control/api/v1/state')
    def _api_v1_state(request):
        exam_type = request.args.get('type')
        dbid_uuid = request.args.get('id')
        exam = request.args.get('exam', 'default')
        if not exam_type or not dbid_uuid:
            return mockserver.make_response('empty param', 400)

        key = 'State:' + exam_type + dbid_uuid + exam
        if key not in context.states:
            return mockserver.make_response('no state', 404)

        return mockserver.make_response(
            json.dumps(load_json(context.states[key])), 200,
        )

    @mockserver.handler('/quality-control/api/v1/pass')
    def _api_v1_pass(request):
        pass_id = request.args.get('pass_id')
        if not pass_id:
            return mockserver.make_response('empty param', 400)

        key = 'Pass:' + pass_id
        if key not in context.passes:
            return mockserver.make_response('not found', 404)

        return mockserver.make_response(
            json.dumps(load_json(context.passes[key])), 200,
        )

    @mockserver.handler('/quality-control/api/v1/data/confirmed')
    def _api_v1_data_confirmed(request):
        exam_type = request.args.get('type')
        dbid_uuid = request.args.get('id')
        if not exam_type or not dbid_uuid:
            return mockserver.make_response('empty param', 400)

        key = 'Confirmed:' + exam_type + dbid_uuid
        if key not in context.confirmed_data:
            return mockserver.make_response('not found', 404)

        return mockserver.make_response(
            json.dumps(load_json(context.confirmed_data[key])), 200,
        )

    @mockserver.handler('/quality-control/api/v1/pass/update')
    def _api_v1_pass_update(request):
        pass_id = request.args.get('pass_id')
        media = request.json.get('media')
        data = request.json.get('data')
        if not pass_id or (media is None and data is None):
            return mockserver.make_response('empty param', 400)

        key = 'Update:' + pass_id
        if key not in context.pass_update_request:
            return mockserver.make_response('empty param', 400)

        expected_request = context.pass_update_request[key]
        if media != expected_request.get(
                'media',
        ) or data != expected_request.get('data'):
            return mockserver.make_response('empty param', 400)

        if key not in context.pass_update:
            return mockserver.make_response('not found', 404)

        return mockserver.make_response(
            json.dumps(load_json(context.pass_update[key])), 200,
        )

    @mockserver.handler('/quality-control/api/v1/pass/data')
    def _api_v1_pass_data(request):
        pass_id = request.args.get('pass_id')
        data = request.json.get('data', [])

        if not pass_id or not data:
            return mockserver.make_response('empty param', 400)

        key = 'Data:' + pass_id
        if key not in context.pass_data_request:
            return mockserver.make_response('empty param', 400)

        expected_request = context.pass_data_request[key]
        if data.keys() != expected_request['data'].keys():
            return mockserver.make_response('empty param', 400)

        if key not in context.pass_data:
            return mockserver.make_response('not found', 404)

        return mockserver.make_response(
            json.dumps(context.pass_data[key]), 200,
        )

    @mockserver.handler('/quality-control/api/v1/pass/resolve')
    def _api_v1_pass_resolve(request):
        context.resolution_status = request.json.get('status')
        return mockserver.make_response('{}', 200)

    @mockserver.handler('/quality-control/api/v1/pass/list')
    def _api_v1_pass_list(request):
        context.pass_list_reqs.append({k: v for k, v in request.args.items()})

        sorted_items = list(context.pass_list_data)
        sorted_items.sort(key=lambda d: d['modified'], reverse=False)

        limit = int(request.args.get('limit'))
        if request.args.get('cursor'):
            start = int(request.args.get('cursor'))
        else:
            start = next(
                k
                for k, v in enumerate(sorted_items)
                if v['modified'] > request.args.get('modified_from')
            )
        end = min(start + limit, len(sorted_items))

        return mockserver.make_response(
            json.dumps(
                {
                    'cursor': str(end),
                    'items': sorted_items[start:end],
                    'modified': sorted_items[-1]['modified'],
                },
            ),
            200,
        )

    return context
