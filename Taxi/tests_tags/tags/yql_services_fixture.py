# pylint: disable=W0612
import json
from typing import Optional

import pytest

from tests_tags.tags import constants

_USERNAME = 'ivanov'
_TAGS_AUTH = 'OAuth tags-robot-token'

DEFAULT_OPERATION_ID = 'operation_id'
YQL_LIMIT = 1000
TMP_PATH = 'tmp/' + _USERNAME + '/88f63051-d0da20b8-370e8722-d51dc23a'


def _get_table_entry(
        index: int,
        chunk: int,
        entity_type: str,
        query_syntax: str,
        ttl_frequency: Optional[int],
        ttl: Optional[str],
):
    if query_syntax != 'SQLv1':
        return {
            entity_type: 'ABC_' + str(int(index % chunk)),
            'tag': 'tag_' + str(int(index / chunk)),
        }

    if ttl_frequency is not None:
        return {
            'entity_value': 'ABC_' + str(int(index % chunk)),
            'entity_type': entity_type,
            'tag': 'tag_' + str(int(index / chunk)),
            'ttl': 'infinity' if (index % ttl_frequency) else ttl,
        }

    return {
        'entity_value': 'ABC_' + str(int(index % chunk)),
        'entity_type': entity_type,
        'tag': 'tag_' + str(int(index / chunk)),
        'ttl': 'infinity',
    }


class YqlContext:
    def __init__(self):
        self.status = 'COMPLETED'
        self.results_data = []
        self.results = {
            'id': DEFAULT_OPERATION_ID,
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
        self.times_called = {'action': 0, 'results_data': 0, 'results': 0}
        self.operation_id = DEFAULT_OPERATION_ID

    def add_status_response(self, status):
        self.status = status

    def gen_results_data_response(
            self,
            rows_count,
            chunk=100,
            entity_type: Optional[str] = None,
            query_syntax: str = 'SQLv1',
            ttl_frequency: Optional[int] = None,
            ttl: Optional[str] = None,
    ):
        self.results_data = None
        if rows_count is not None:
            self.results_data = [
                _get_table_entry(
                    index,
                    chunk,
                    entity_type
                    or constants.SUPPORTED_ENTITY_TYPES[
                        index % len(constants.SUPPORTED_ENTITY_TYPES)
                    ],
                    query_syntax,
                    ttl_frequency,
                    ttl,
                )
                for index in range(rows_count)
            ]
        return self.results_data

    def add_results_response(self, results):
        self.results = results

    def set_operation_id(self, operation_id):
        self.operation_id = operation_id


@pytest.fixture(autouse=True)
def local_yql_services(mockserver):
    context = YqlContext()

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)', regex=True,
    )
    def action_handler(request, operation_id):
        assert request.headers['Authorization'] == _TAGS_AUTH
        assert request.headers['User-Agent'] == constants.USER_AGENT
        assert request.method == 'POST'
        assert operation_id == context.operation_id

        context.times_called['action'] += 1
        body = json.loads(request.get_data())
        assert body['action'] in ('ABORT', 'RUN')  # TODO not used in tests
        status = 'ABORTING' if body['action'] == 'ABORT' else 'RUNNING'
        response = f'{{"id": "{operation_id}", "status": "{status}"}}'
        return mockserver.make_response(response, 200)

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/results_data',
        regex=True,
    )
    def results_data_handler(request, operation_id):
        assert operation_id == context.operation_id

        context.times_called['results_data'] += 1
        args = request.args.to_dict()
        offset = int(args['offset'])
        limit = int(args['limit'])
        assert offset == 0
        assert limit == 1000
        assert int(args['write_index']) == 0
        assert args['format'] == 'CSV'
        assert request.headers['Authorization'] == _TAGS_AUTH
        assert request.headers['User-Agent'] == constants.USER_AGENT

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
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/results', regex=True,
    )
    def results_handler(request, operation_id):
        assert operation_id == context.operation_id

        assert request.headers['Authorization'] == _TAGS_AUTH
        assert request.headers['User-Agent'] == constants.USER_AGENT
        context.times_called['results'] += 1
        return context.results

    @mockserver.json_handler('/yql/api/v2/operations')
    def prepare_handler(request):
        response_yql = (
            f'{{"id": "{context.operation_id}", "status":"{context.status}"}}'
        )
        return mockserver.make_response(response_yql, 200)

    return context
