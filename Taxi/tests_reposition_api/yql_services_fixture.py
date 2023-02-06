# pylint: disable=W0612, C5521, W0621
import json

import pytest

from .conftest import USER_AGENT

USERNAME = 'ivanov'
OAUTH = 'OAuth taxi-robot-token'

OPERATION_ID = 'operation_id'
YQL_LIMIT = 1000
TMP_PATH = 'tmp/' + USERNAME + '/88f63051-d0da20b8-370e8722-d51dc23a'


class YqlContext:
    def __init__(self):
        self.status = 'COMPLETED'
        self.results_data = []
        self.results = {
            'id': OPERATION_ID,
            'status': 'COMPLETED',
            'data': [
                {
                    'Write': [
                        {
                            'Ref': [
                                {
                                    'Reference': ['yt', 'yt-test', TMP_PATH],
                                    'Columns': ['driver_license', 'tag'],
                                },
                            ],
                            'Data': [{'x-skip-additional-validation': True}],
                        },
                    ],
                },
            ],
            'updatedAt': '2019-06-18T07:04:50.528Z',
        }
        self.times_called = {
            'status': 0,
            'action': 0,
            'results_data': 0,
            'results': 0,
        }
        self.auth = OAUTH

    def add_status_response(self, status):
        self.status = status

    def gen_results_data_response(self, rows_count, chunk=100):
        self.results_data = None
        if rows_count is not None:
            self.results_data = [
                {
                    'driver_license': 'ABC_' + str(int(index % chunk)),
                    'tag': 'tag_' + str(int(index / chunk)),
                }
                for index in range(rows_count)
            ]
        return self.results_data

    def add_results_response(self, results):
        self.results = results


@pytest.fixture(autouse=True)
def local_yql_services(mockserver):
    context = YqlContext()

    @mockserver.json_handler('/yql/api/v2/operations/%s' % OPERATION_ID)
    def status_handler(request):
        assert request.headers['Authorization'] == context.auth
        assert request.headers['User-Agent'] == USER_AGENT
        if request.method == 'GET':
            context.times_called['status'] += 1
            response = '{"id": "%s", "username": "%s", "status": "%s"}' % (
                OPERATION_ID,
                USERNAME,
                context.status,
            )
            return mockserver.make_response(response, 200)

        if request.method == 'POST':
            context.times_called['action'] += 1
            body = json.loads(request.get_data())
            assert body['action'] == 'ABORT'
            response = '{"id": "%s"}' % OPERATION_ID
            return mockserver.make_response(response, 200)

        return mockserver.make_response('{}', 404)

    @mockserver.json_handler(
        '/yql/api/v2/operations/%s/results_data' % OPERATION_ID,
    )
    def results_data_handler(request):
        context.times_called['results_data'] += 1
        args = request.args.to_dict()
        offset = int(args['offset'])
        limit = int(args['limit'])
        assert offset == 0
        assert limit == 1000
        assert int(args['write_index']) == 0
        assert args['format'] == 'CSV'
        assert request.headers['Authorization'] == context.auth
        assert request.headers['User-Agent'] == USER_AGENT

        results_data = ''
        if context.results_data is None:
            return mockserver.make_response(results_data, 400)

        end = min(offset + limit, len(context.results_data), YQL_LIMIT)
        if offset < end:
            results_data = 'tag,driver_license\r\n'
            for index in range(offset, end):
                item = context.results_data[index]
                results_data += (
                    item['tag'] + ',' + item['driver_license'] + '\r\n'
                )
        return mockserver.make_response(results_data, 200)

    @mockserver.json_handler(
        '/yql/api/v2/operations/%s/results' % OPERATION_ID,
    )
    def results_handler(request):
        assert request.headers['Authorization'] == context.auth
        assert request.headers['User-Agent'] == USER_AGENT
        context.times_called['results'] += 1
        args = request.args.to_dict()
        assert args['filters'] == 'DATA'
        return context.results

    return context
