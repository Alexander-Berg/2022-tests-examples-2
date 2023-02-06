import pytest

from test_taxi_shared_payments.web.static.test_report import orders


UID_HEADER = 'X-Yandex-UID'


@pytest.mark.parametrize(
    ['data'],
    [
        pytest.param(
            {
                'account_id': '7',
                'since_date': '2019-09-04',
                'till_date': '2019-09-11',
            },
            id='usual send',
        ),
        pytest.param(
            {
                'account_id': '7',
                'since_date': '2019-09-04',
                'till_date': '2019-09-11',
                'send_email': 'some@email.com',
            },
            id='send with defined email',
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'shared-payments'}])
async def test_admin_send_report(
        web_app_client, mockserver, mock_all_api, patch, data,
):
    @patch('taxi_shared_payments.controllers.report.get_yt_orders_for_account')
    async def _get_order_procs(*args, **kwargs):
        return orders.ORDERS

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _retrieve(request):
        return {'id': request.json['id'], 'value': request.json['id']}

    @patch('taxi_shared_payments.controllers.report._send')
    async def _send_report(cron_context, email, report, locale):
        if 'send_email' in data:
            assert email == data['send_email']

    response = await web_app_client.post(
        '/v1/admin/send_account_report', json=data,
    )
    content = await response.json()
    assert response.status == 200, content
    assert len(_send_report.calls) == 1


@pytest.mark.parametrize(
    ['data', 'expected_status', 'expected_message'],
    [
        pytest.param(
            {
                'account_id': '1',
                'since_date': '2019-09-04',
                'till_date': '2019-09-11',
            },
            404,
            'account with id 1 does not exist',
            id='unknown account',
        ),
        pytest.param(
            {
                'account_id': '2',
                'since_date': '2019-09-04',
                'till_date': '2019-09-11',
            },
            404,
            'account with id 2 does not have email',
            id='account without email',
        ),
    ],
)
async def test_admin_send_report_fail(
        web_app_client, data, expected_status, expected_message,
):
    response = await web_app_client.post(
        '/v1/admin/send_account_report', json=data,
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content['system_message'] == expected_message


@pytest.mark.parametrize(
    ['data', 'expected_status', 'expected_message'],
    [
        pytest.param(
            {
                'account_id': '7',
                'since_date': '2019-09-04',
                'till_date': '2019-09-11',
            },
            400,
            'Unexpected error while send report to account_id 7',
            id='unknown account',
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'shared-payments'}])
async def test_admin_send_report_external_fail(
        web_app_client, mockserver, data, expected_status, expected_message,
):
    @mockserver.json_handler('/archive-api/v1/yt/select_rows')
    async def _select_rows(*args, **kwargs):
        return mockserver.make_response('bad request', status=400)

    @mockserver.json_handler('/personal/v1/emails/retrieve')
    def _retrieve(request):
        return {'id': request.json['id'], 'value': request.json['id']}

    response = await web_app_client.post(
        '/v1/admin/send_account_report', json=data,
    )
    content = await response.json()
    assert response.status == expected_status, content
    assert content['system_message'] == expected_message


@pytest.mark.translations(
    reports={'order.title': {'ru': 'Отчет'}},
    tariff={'name.comfortplus': {'ru': 'Комфорт+'}},
)
@pytest.mark.parametrize(
    'uid, account_id, since_date, till_date, lang,'
    'expected_status, expected_headers, expected_json_response',
    [
        pytest.param(
            'user1',
            '7',
            '2019-09-04',
            '2019-09-11',
            'ru',
            200,
            {
                'Content-Disposition': (
                    'attachment; filename=report_04.09.2019-11.09.2019.xlsx'
                ),
            },
            None,
            id='report generated',
        ),
        pytest.param(
            'user1',
            '2',
            '2019-09-04',
            '2019-09-11',
            'ru',
            403,
            {},
            {
                'code': 'GENERAL',
                'message': '',
                'system_message': 'yandex_uid does not match owner_id',
                'details': {},
            },
            id='account_id does no match uid',
        ),
    ],
)
async def test_coop_acc_export_account_report(
        web_app_client,
        mockserver,
        mock_all_api,
        patch,
        uid,
        account_id,
        since_date,
        till_date,
        lang,
        expected_status,
        expected_headers,
        expected_json_response,
):
    @patch('taxi_shared_payments.controllers.report.get_yt_orders_for_account')
    async def _get_order_procs(*args, **kwargs):
        return orders.ORDERS

    response = await web_app_client.get(
        '/4.0/coop_account/export_account_report',
        params={
            'account_id': account_id,
            'since_date': since_date,
            'till_date': till_date,
            'lang': lang,
        },
        headers={UID_HEADER: uid},
    )

    assert response.status == expected_status
    assert response.headers.items() >= expected_headers.items()
    if expected_json_response is not None:
        assert await response.json() == expected_json_response


@pytest.mark.parametrize(
    'uid, account_id, since_date, till_date, lang',
    [('user1', '7', '2019-09-04', '2019-09-11', 'bad-lang')],
)
async def test_coop_acc_export_account_report_unsupported_lang(
        web_app_client,
        mockserver,
        mock_all_api,
        patch,
        uid,
        account_id,
        since_date,
        till_date,
        lang,
):
    @patch('taxi_shared_payments.controllers.report.get_yt_orders_for_account')
    async def _get_order_procs(*args, **kwargs):
        return orders.ORDERS

    response = await web_app_client.get(
        '/4.0/coop_account/export_account_report',
        params={
            'account_id': account_id,
            'since_date': since_date,
            'till_date': till_date,
            'lang': lang,
        },
        headers={UID_HEADER: uid},
    )

    assert response.status == 400
    response_json = await response.json()
    assert response_json['code'] == 'unsupported lang'
