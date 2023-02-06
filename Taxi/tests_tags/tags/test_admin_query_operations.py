from typing import Dict
from typing import List
import urllib.parse


import pytest

from tests_tags.tags import constants


_TEST_SHARED_ID = 'XL15AAlSshlfAw44s4E1lUtwCkmt2cKTumKON1zwgqQ='
_YQL_URL_PREFIX = 'https://yql.yandex-team.ru/Operations/'
_OAUTH_ARG = 'Authorization'
_USER_AGENT_ARG = 'User-Agent'


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['pg_tags_queries.sql'])
@pytest.mark.parametrize(
    'query_id, newer_than, older_than, response_code, response_indexes',
    [
        pytest.param(
            'first_name',
            '2018-00-25T16:34:56+0000',
            '2018-08-22T06:34:56+0000',
            400,
            None,
            id='Can\'t parse datetime: 2018-00-25T16:34:56+0000',
        ),
        pytest.param(
            'first_name',
            '2018-08-22T02:34:56+0000',
            '2018-08-22T01:34:57+0000',
            400,
            None,
            id='invalid timestamp range',
        ),
        pytest.param(
            'wrong',
            '2018-08-22T02:34:56+0000',
            '2018-08-22T14:34:56+0000',
            404,
            None,
            id='query with name "wrong" was not found',
        ),
        pytest.param(
            'first_name',
            '2018-08-22T02:33:56+0000',
            '2018-08-22T02:37:56+0000',
            200,
            [0, 2, 7, 8],
            id='select all',
        ),
        pytest.param(
            'first_name',
            '2018-08-22T02:34:57+0000',
            '2018-08-22T02:37:56+0000',
            200,
            [2, 7, 8],
            id='select particular (lower bound)',
        ),
        pytest.param(
            'first_name',
            '2018-08-22T02:34:57+0000',
            '2018-08-22T02:36:55+0000',
            200,
            [2],
            id='select particular (lower & upper bounds)',
        ),
        pytest.param(
            'name_extended',
            '2018-08-22T02:34:56+0000',
            '2018-08-22T14:34:56+0000',
            200,
            [6],
            id='select one',
        ),
        pytest.param(
            'name_extended',
            '2018-08-22T01:34:56+0000',
            '2018-08-22T02:34:55+0000',
            200,
            [],
            id='select none by time range',
        ),
        pytest.param(
            'nayme_with_error',
            '2018-08-22T02:34:56+0000',
            '2018-08-22T03:34:56+0000',
            200,
            [1, 3],
            id='select all (exact time range)',
        ),
        pytest.param(
            'surname_not_last',
            '2018-08-22T02:34:56+0000',
            '2018-08-22T03:04:56+0000',
            200,
            [4, 5],
            id='select all (large time range)',
        ),
        pytest.param(
            'the_last_name',
            '2018-08-22T02:34:56+0000',
            '2018-08-22T14:34:56+0000',
            200,
            [],
            id='no launchs',
        ),
    ],
)
async def test_admin_queries_history(
        taxi_tags,
        query_id: str,
        newer_than: str,
        older_than: str,
        response_code: int,
        response_indexes: List[int],
):
    responses = [
        (
            '5d92fb9b9dee76d0a1e0a72f',
            'completed',
            '2018-08-22T05:34:56+0300',
            8,
            5,
            4,
            0,
        ),
        (
            '5d92f9b9095c4eba55cd0013',
            'completed',
            '2018-08-22T05:40:56+0300',
            9,
            3,
            7,
            3,
        ),
        (
            '5d92f8149dee76d0a1e0a60b',
            'failed',
            '2018-08-22T05:35:56+0300',
            'failed to process operation: no dbid_uuid',
        ),
        (
            '5d92fa319dee76d0a1e0a6d3',
            'completed',
            '2018-08-22T06:00:56+0300',
            1,
            0,
            0,
            0,
        ),
        (
            '5d92f63153f354d3cdf42a4a',
            'completed',
            '2018-08-22T05:34:56+0300',
            6,
            4,
            0,
            4,
        ),
        (
            '5d92f79b9f4b9eac6652cf6e',
            'failed',
            '2018-08-22T06:04:56+0300',
            'operation failed: ERROR',
        ),
        (
            '5d92f414095c4eba55ccfe48',
            'completed',
            '2018-08-22T05:34:56+0300',
            8,
            0,
            0,
            3,
        ),
        ('5d92f9b968a6f554a5a8fbb3', 'running', '2018-08-22T05:36:56+0300'),
        ('5d92f9b968a6f554a5a8fbee', 'aborted', '2018-08-22T05:37:56+0300'),
    ]

    def _create_operation(index):
        data = responses[index]
        response = {'id': data[0], 'status': data[1], 'started': data[2]}
        if data[1] == 'failed':
            response['failure_description'] = data[3]
        if data[1] == 'completed':
            response['total_count'] = data[3]
            response['added_count'] = data[4]
            response['removed_count'] = data[5]
            response['malformed_count'] = data[6]
        return response

    url = (
        'v1/admin/queries/operations/history?'
        'query_id={}&newer_than={}&older_than={}'.format(
            query_id,
            urllib.parse.quote_plus(newer_than),
            urllib.parse.quote_plus(older_than),
        )
    )
    response = await taxi_tags.get(url)
    assert response.status_code == response_code
    if response_indexes is not None:
        response_body = {
            'operations': [
                _create_operation(index) for index in response_indexes
            ],
        }
        assert response.json() == response_body


@pytest.mark.nofilldb()
@pytest.mark.pgsql('tags', files=['pg_tags_queries.sql'])
@pytest.mark.parametrize(
    'operation_id, response_code, response_body',
    [
        (
            'non-exist-operation-id',
            404,
            {
                'code': '404',
                'message': (
                    'operation \'non-exist-operation-id\' was not found'
                ),
            },
        ),
        (
            '5d92fb9b9dee76d0a1e0a72f',
            200,
            {'link': _YQL_URL_PREFIX + _TEST_SHARED_ID},
        ),
        (
            '5d92f9b968a6f554a5a8fbb3',
            200,
            {'link': _YQL_URL_PREFIX + _TEST_SHARED_ID},
        ),
    ],
)
async def test_query_operations_share(
        taxi_tags,
        mockserver,
        operation_id: str,
        response_code: int,
        response_body: Dict[str, str],
):
    @mockserver.json_handler(f'/yql/api/v2/operations/{operation_id}/share_id')
    def handler(request):
        assert request.headers[_OAUTH_ARG] == constants.TAGS_AUTH
        assert request.headers[_USER_AGENT_ARG] == constants.USER_AGENT

        # add commas
        return mockserver.make_response('\"' + _TEST_SHARED_ID + '\"', 200)

    url = f'v1/admin/queries/operations/share?id={operation_id}'
    response = await taxi_tags.get(url)
    assert response.status_code == response_code
    assert response.json() == response_body

    assert handler.times_called == (1 if response_code == 200 else 0)
