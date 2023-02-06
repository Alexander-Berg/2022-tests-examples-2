import datetime
import logging

from corp_reports.internal.orders.common import structs
from corp_reports.internal.orders.eats2 import data
from corp_reports.utils.common import exceptions

EATS_REPORT_ANSWER = {
    'orders': [
        {
            'yandex_uid': '12324',
            'user_id': '12324',
            'id': '12324',
            'client_id': '12324',
            'final_cost': '100',
            'created_at': '2021-09-03T11:42:41.224673+00:00',
            'closed_at': '2021-09-03T11:42:41.224673+00:00',
            'status': 'sucess',
        },
    ],
}

EATS_REPORT_ANSWER_EMPTY: dict = {'orders': []}

EATS_REPORT_REQUEST = structs.OrdersReportParams(
    client_id='12324',
    locale='rus',
    department_id='12324',
    requested_by_ip='12324',
    since=datetime.datetime.now(),
    till=datetime.datetime.now(),
)


async def test_eats2_reports(stq3_context, mock_corp_orders):
    mock_corp_orders.data.orders_eats_response = EATS_REPORT_ANSWER

    orders_list = await data.get_orders(stq3_context, EATS_REPORT_REQUEST)

    assert orders_list
    assert mock_corp_orders.data.eats_orders_count == 2


async def test_eats2_reports_400_error(stq3_context, caplog, mock_corp_orders):
    mock_corp_orders.data.eats_must_be_error = True

    caplog.set_level(logging.ERROR)
    try:
        await data.get_orders(stq3_context, EATS_REPORT_REQUEST)
        assert False
    except exceptions.CorpError as exc:
        assert mock_corp_orders.data.eats_orders_count == 0
        assert exc.error.text == 'Request error'
        assert caplog.text
