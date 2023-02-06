import json
import os

from aiohttp import web
import pytest

TARGET_INFO_PREFIX = '/replication/state/yt_target_info/'

RESPONSE_CACHE = {}

RESPONSES_DIR = os.path.join(
    os.path.dirname(__file__), 'static', 'test_send_reports', 'responses',
)
for root, _, filenames in os.walk(RESPONSES_DIR):
    for filename in filenames:
        with open(os.path.join(root, filename)) as response_filename:
            RESPONSE_CACHE[filename] = json.load(response_filename)


@pytest.fixture
def mock_yt(mockserver):
    @mockserver.handler(TARGET_INFO_PREFIX, prefix=True)
    def _get_target_info(request):
        target_name = request.path_qs[len(TARGET_INFO_PREFIX) :]
        if target_name == 'order_proc_admin':
            folder = 'struct'
            table_name = 'order_proc_admin'
        elif target_name.startswith('order_proc_'):
            folder = 'indexes/order_proc'
            if target_name.endswith('_index'):
                table_name = target_name[len('order_proc_') : -len('_index')]
            else:
                table_name = target_name[len('order_proc_') :]
        else:
            folder = 'as_is'
            table_name = target_name
        return mockserver.make_response(
            json={
                'table_path': f'replica/mongo/{folder}/{table_name}',
                'full_table_path': 'full_table_path',
                'target_names': ['does', 'not', 'matter'],
                'clients_delays': 0,  # does not matter
            },
        )

    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    # pylint: disable=W0612
    def _select_rows(request):
        all_rows = RESPONSE_CACHE['archive-api_v1_yt_select_rows.json']
        request_data = json.loads(request.get_data())
        query_string = request_data['query']['query_string']
        query_params = request_data['query']['query_params']
        where_conditions = query_string.split('WHERE ')[1].split(' AND ')
        if not where_conditions:
            return all_rows
        rows = []
        conditions = {}
        for condition, param in zip(where_conditions, query_params[2:]):
            if condition == 'index.created <= -%p':
                conditions['created_from'] = param
            elif condition == 'index.created >= -%p':
                conditions['created_to'] = param
            elif condition == 'index.user_id = %p':
                conditions['user_id'] = param
        for row in all_rows['items']:
            if (
                    row['user_id'] == conditions['user_id']
                    and conditions['created_from']
                    <= row['created']
                    <= conditions['created_to']
            ):
                rows.append(row)
        return {'items': rows}


@pytest.fixture
def mock_user_api(mockserver):
    @mockserver.json_handler('/user_api-api/users/get')
    def _users_get(request):
        request_data = json.loads(request.get_data())
        user_id = request_data['id']
        response = RESPONSE_CACHE.get(f'user-api_users_get_{user_id}.json')
        if response is None:
            return web.json_response(status=404)
        return response

    @mockserver.json_handler('/user_api-api/user_emails/get')
    def _user_emails_get(request):
        request_data = json.loads(request.get_data())
        if request_data.get('phone_ids'):
            if request_data['phone_ids'][0] == 'b869ecf2c92becfb9229fcef':
                return RESPONSE_CACHE['user-api_user_emails_get_1.json']
            if request_data['phone_ids'][0] == 'cb0c709a70937bc713971486':
                return RESPONSE_CACHE['user-api_user_emails_get_2.json']
            if request_data['phone_ids'][0] == '986a3cb8e688f6dca9638fa8':
                return RESPONSE_CACHE['user-api_user_emails_get_4.json']
            if request_data['phone_ids'][0] == '986a3cb8e688f6dca9638fa9':
                return RESPONSE_CACHE['user-api_user_emails_get_5.json']
        if request_data.get('yandex_uids'):
            if request_data['yandex_uids'][0] == '3039949911':
                return RESPONSE_CACHE['user-api_user_emails_get_1.json']
            if request_data['yandex_uids'][0] == '3038843911':
                return RESPONSE_CACHE['user-api_user_emails_get_3.json']
        return {'items': []}


@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'stq-agent', 'src': 'admin-orders'},
        {'dst': 'archive-api', 'src': 'admin-orders'},
    ],
)
@pytest.mark.parametrize(
    [
        'user_id',
        'created_from',
        'created_to',
        'response_status',
        'expected_response_filename',
        'error_code',
        'reports_count',
        'email',
        'expected_email',
    ],
    (
        (
            'dacf93e176d69e5a5adebd17b0babddd',
            '2020-02-04T12:00:00.000000Z',
            '2020-02-06T12:00:00.000000Z',
            200,
            'admin_orders_v1_send_reports_1.json',
            None,
            2,
            None,
            None,
        ),
        (
            'a3c3e25d34dd420c92098efcbe760bc0',
            '2020-02-05T12:00:00.000000Z',
            '2020-02-07T12:00:00.000000Z',
            200,
            'admin_orders_v1_send_reports_2.json',
            None,
            1,
            None,
            None,
        ),
        (
            'dacf93e176d69e5a5adebd17b0babddd',
            '2020-03-04T12:00:00.000000Z',
            '2020-03-06T12:00:00.000000Z',
            404,
            None,
            'orders_not_found',
            0,
            None,
            None,
        ),
        (
            '6f454b18e49cb7e6ce2a152f7c767653',
            '2020-01-01T12:00:00.000000Z',
            '2020-01-02T12:00:00.000000Z',
            404,
            None,
            'orders_not_found',
            0,
            None,
            None,
        ),
        (
            '4ae9f936b1c6dfee2b95b24ca26ea587',
            '2020-02-04T12:00:00.000000Z',
            '2020-02-06T12:00:00.000000Z',
            406,
            None,
            'email_not_bound',
            0,
            None,
            None,
        ),
        (
            'invalid_user_id',
            '2020-01-01T12:00:00.000000Z',
            '2020-01-02T12:00:00.000000Z',
            404,
            None,
            'user_not_found',
            0,
            None,
            None,
        ),
        (
            '1974cabc907f0979e8f7296cbe6ca032',
            '2020-01-01T12:00:00.000000Z',
            '2020-01-02T12:00:00.000000Z',
            406,
            None,
            'no_phone_id_and_uid',
            0,
            None,
            None,
        ),
        (
            'aa9f21d3a2899596c6e7aee25b3a799c',
            '2020-02-04T12:00:00.000000Z',
            '2020-02-06T12:00:00.000000Z',
            406,
            None,
            'email_not_confirmed',
            0,
            None,
            None,
        ),
        (
            'dacf93e176d69e5a5adebd17b0babddd',
            '2020-02-06T12:00:00.000000Z',
            '2020-02-04T12:00:00.000000Z',
            400,
            None,
            'general',
            0,
            None,
            None,
        ),
        (
            'dacf93e176d69e5a5adebd17b0babddd',
            '2016-02-06T12:00:00.000000Z',
            '2020-02-04T12:00:00.000000Z',
            400,
            None,
            'old_orders',
            0,
            None,
            None,
        ),
        (
            'dacf93e176d69e5a5adebd17b0babdde',
            '2020-02-05T12:00:00.000000Z',
            '2020-02-07T12:00:00.000000Z',
            200,
            'admin_orders_v1_send_reports_3.json',
            None,
            1,
            None,
            '186a969be89ae1b61fd69db4',
        ),
        (
            'dacf93e176d69e5a5adebd17b0babdde',
            '2020-02-05T12:00:00.000000Z',
            '2020-02-07T12:00:00.000000Z',
            200,
            'admin_orders_v1_send_reports_3.json',
            None,
            1,
            '186a969be89ae1b61fd69db5',
            '186a969be89ae1b61fd69db5',
        ),
    ),
)
@pytest.mark.usefixtures('mock_yt', 'mock_user_api')
async def test_send_reports(
        taxi_admin_orders_web,
        stq,
        user_id,
        created_from,
        created_to,
        response_status,
        expected_response_filename,
        error_code,
        reports_count,
        email,
        expected_email,
        mongo,
):
    request_dict = {'created_from': created_from, 'created_to': created_to}
    request = f'/v1/report/send_bulk?user_id={user_id}'
    if email:
        request += f'&personal_email_id={email}'
    response = await taxi_admin_orders_web.post(request, json=request_dict)

    assert response.status == response_status
    content = await response.json()
    assert stq.send_ride_report_mail.times_called == reports_count
    if response_status == 200:
        expected_content = RESPONSE_CACHE[expected_response_filename]
        assert content == expected_content, content

        email = stq.send_ride_report_mail.next_call()['kwargs'].get(
            'personal_email_id',
        )
        assert email == expected_email
    else:
        assert content['code'] == error_code
