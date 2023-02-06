import datetime
import logging

from corp_reports.internal.orders.common import structs
from corp_reports.internal.orders.drive import data
from corp_reports.utils.common import exceptions


DRIVE_REPORT_ANSWER = {
    'orders': [
        {
            'yandex_uid': '12324',
            'user_id': '12324',
            'id': '12324',
            'client_id': '12324',
        },
    ],
}

DRIVE_REPORT_REQUEST = structs.OrdersReportParams(
    client_id='12324',
    locale='rus',
    department_id='12324',
    requested_by_ip='12324',
    since=datetime.datetime.now(),
    till=datetime.datetime.now(),
)


async def test_drive_reports(stq3_context, mock_corp_orders):
    mock_corp_orders.data.orders_drive_response = DRIVE_REPORT_ANSWER

    orders_list = await data.get_orders(stq3_context, DRIVE_REPORT_REQUEST)
    assert orders_list
    assert mock_corp_orders.data.drive_orders_count == 2
    assert orders_list[0]['user_id']


async def test_drive_reports_400_error(stq3_context, caplog, mock_corp_orders):
    mock_corp_orders.data.drive_must_be_error = True

    caplog.set_level(logging.ERROR)
    try:
        await data.get_orders(stq3_context, DRIVE_REPORT_REQUEST)
        assert False
    except exceptions.CorpError as exc:
        assert mock_corp_orders.data.drive_orders_count == 0
        assert exc.error.text == 'Client Exception(for example timeout)'
        assert caplog.text
