import json
import os

import aiohttp
import bson
import bson.json_util
import pytest

RESPONSE_CACHE = {}

RESPONSES_DIR = os.path.join(
    os.path.dirname(__file__), 'static', 'test_send_report', 'responses',
)
for root, _, filenames in os.walk(RESPONSES_DIR):
    for filename in filenames:
        with open(os.path.join(root, filename)) as response_file:
            RESPONSE_CACHE[filename] = bson.json_util.loads(
                response_file.read(),
            )


@pytest.fixture
def mock_yt(order_archive_mock):
    order_archive_mock.set_order_proc(
        RESPONSE_CACHE['order_archive-order_proc-retrieve.json'],
    )


@pytest.fixture
def mock_user_api(mockserver):
    @mockserver.json_handler('/user_api-api/users/get')
    def _users_get(request):
        request_data = json.loads(request.get_data())
        user_id = request_data['id']
        response = RESPONSE_CACHE.get(f'user-api_users_get_{user_id}.json')
        if response is None:
            return aiohttp.web.json_response(status=404)
        return response

    @mockserver.json_handler('/user_api-api/user_emails/get')
    def _user_emails_get(request):
        request_data = json.loads(request.get_data())
        response_items = []
        if request_data.get('phone_ids'):
            email_response = RESPONSE_CACHE['user-api_user_emails_get.json']
            for item in email_response['items']:
                if request_data['phone_ids'][0] == item['phone_id']:
                    response_items.append(item)
        return {'items': response_items}


@pytest.mark.config(
    TVM_RULES=[
        {'dst': 'stq-agent', 'src': 'admin-orders'},
        {'dst': 'archive-api', 'src': 'admin-orders'},
    ],
)
@pytest.mark.parametrize(
    [
        'order_id',
        'response_status',
        'expected_response',
        'reports_count',
        'email',
    ],
    (
        ('49b39429de4f5072a4c32e32f9d6f79d', 200, {}, 1, None),
        (
            'a3c3e25d34dd420c92098efcbe760bc0',
            404,
            dict(code='order_not_found', message='Order not found'),
            0,
            None,
        ),
        (
            'dacf93e176d69e5a5adebd17b0babddd',
            409,
            dict(
                code='old_order',
                message='Заказ создан слишком давно для переотправки отчёта',
            ),
            0,
            None,
        ),
        (
            'fffff936b1c6dfee2b95b24ca26eаааа',
            406,
            dict(
                code='email_not_bound',
                message='Email not bound for user'
                ' with user_id=4ae9f936b1c6dfee2b95b24ca26ea587',
            ),
            0,
            None,
        ),
        (
            '2020cabc907f0979e8f7296cbe6cffff',
            406,
            dict(
                code='no_phone_id_and_uid',
                message='Cannot get phone_id or yandex_uid'
                ' for user_id=1974cabc907f0979e8f7296cbe6ca032.'
                ' User must bind phone number again.',
            ),
            0,
            None,
        ),
        (
            '000021d3a2899596c6e7aee25b3adddd',
            406,
            dict(
                code='email_not_confirmed',
                message='None of emails were confirmed for user'
                ' with user_id=aa9f21d3a2899596c6e7aee25b3a799c',
            ),
            0,
            None,
        ),
        (
            '000021d3a2899596c6e7aee25b3adddd',
            200,
            dict(),
            1,
            '186a969be89ae1b61fd69db1',
        ),
    ),
)
@pytest.mark.usefixtures('mock_yt', 'mock_user_api')
async def test_send_reports(
        taxi_admin_orders_web,
        stq,
        order_id,
        response_status,
        expected_response,
        reports_count,
        email,
        mongo,
):
    request = f'/v1/report/send/?order_id={order_id}'
    if email:
        request += f'&personal_email_id={email}'
    response = await taxi_admin_orders_web.post(
        request, json={}, headers={'X-Yandex-Login': 'simpleman'},
    )

    assert response.status == response_status
    content = await response.json()
    assert content == expected_response
    assert stq.send_ride_report_mail.times_called == reports_count
