# pylint: disable=unused-variable
import datetime

import pytest

from taxi_shared_payments.controllers import report as report_controller
from taxi_shared_payments.generated.cron import run_cron
from taxi_shared_payments.repositories import accounts as accounts_repo
from test_taxi_shared_payments.cron.static.test_order_reports import orders

EMAIL = 'engineer@yandex-team.ru'


# pylint: disable=too-many-locals
@pytest.mark.config(COOP_ACCOUNT_ENABLE_REPORTS=True)
@pytest.mark.parametrize(
    (
        'account_id',
        'expected_calls_count',
        'since_date',
        'till_date',
        'next_report_date',
    ),
    [
        pytest.param(
            '7',
            1,
            datetime.datetime(2019, 9, 2, 0, 0),
            datetime.datetime(2019, 9, 9, 0, 0),
            datetime.datetime(2019, 9, 16, 4, 0),
            marks=[pytest.mark.now('2019-09-11T12:08:12')],
            id='account with id==7 will receive a report',
        ),
        pytest.param(
            None,
            0,
            None,
            None,
            None,
            marks=[pytest.mark.now('2019-09-10T12:08:12')],
            id='day before, should be no reports this day',
        ),
        pytest.param(
            '7',
            1,
            datetime.datetime(2019, 9, 2, 0, 0),
            datetime.datetime(2019, 9, 9, 0, 0),
            datetime.datetime(2019, 9, 16, 4, 0),
            marks=[pytest.mark.now('2019-09-12T12:08:12')],
            id='day after, one account left unprocessed - must send a report',
        ),
        pytest.param(
            '8',
            3,
            datetime.datetime(2019, 9, 2, 0, 0),
            datetime.datetime(2019, 9, 9, 0, 0),
            datetime.datetime(2019, 9, 16, 4, 0),
            marks=[pytest.mark.now('2019-09-15T12:08:12')],
            id='check cron runs on Sunday but next_report_date is Wednesday',
        ),
        pytest.param(
            '9',
            4,
            datetime.datetime(2019, 9, 1, 0, 0),
            datetime.datetime(2019, 9, 30, 23, 59, 59, 999999),
            datetime.datetime(2019, 11, 1, 10, 11, 0),
            marks=[pytest.mark.now('2019-10-02T12:08:12')],
            id='mothly report',
        ),
    ],
)
async def test_cron_task(
        cron_context,
        patch,
        since_date,
        till_date,
        expected_calls_count,
        next_report_date,
        account_id,
):
    @patch('taxi_shared_payments.controllers.report.get_yt_orders_for_account')
    async def _get_order_procs(*args, **kwargs):
        return orders.ORDERS

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(data_type, request_id, *args, **kwargs):
        return {'email': request_id}

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_user_phones(phone_ids, *args, **kwargs):
        return [{'phone': ph_id, 'id': ph_id} for ph_id in phone_ids]

    @patch('taxi_shared_payments.controllers.report._send')
    async def _send_report(cron_context, email, report, locale):
        pass

    await run_cron.main(
        ['taxi_shared_payments.crontasks.order_reports', '-t', '0'],
    )

    # get personal data == email
    assert (len(_retrieve.calls)) == expected_calls_count

    # get orders
    assert (len(_get_order_procs.calls)) == expected_calls_count

    # check send email
    if expected_calls_count > 0:
        report_call = [
            call
            for call in _send_report.calls
            if call['report'].account.id == account_id
        ][0]
        assert not _send_report.calls  # now empty

        # verify email
        email = report_call['email']
        assert email == EMAIL

        report = report_call['report']

        # check report fields
        assert report.since_date == since_date
        assert report.till_date == till_date
        for order in report.orders:
            del order['name']
            del order['phone']
        assert report.orders == orders.ORDERS

        # check updated next_report_date
        upd_acc = await accounts_repo.get_one_by_id(cron_context, account_id)
        assert upd_acc.next_report_date == next_report_date


async def test_get_yt_orders_for_account(cron_context, patch):
    @patch('taxi.clients.archive_api.ArchiveApiClient.select_rows')
    async def _select_rows(*args, **kwargs):
        return orders.SELECT_ROWS_RESULT

    account_id = '7'
    phone_ids = ['phone_id']
    since_date = datetime.datetime(2019, 9, 4, 0, 0)
    till_date = datetime.datetime(2019, 9, 11, 0, 0)

    class FakeConfig:
        ARCHIVE_API_YT_RUNTIME_REPLICATION_DELAY = 9999

    class FakeArchiveApi:
        def __init__(self):
            self.prefix = '//home/taxi/YT/'
            self.index_prefix = '{}replica/mongo/indexes/'.format(self.prefix)
            self.struct_prefix = '{}replica/mongo/struct/'.format(self.prefix)
            self.select_rows = _select_rows

    yt_orders = await report_controller.get_yt_orders_for_account(
        cron_context,
        account_id,
        phone_ids,
        since_date,
        till_date,
        order_fields=report_controller.ORDER_FIELDS,
    )

    select_rows_args = _select_rows.call

    query_string = select_rows_args['args'][0]
    assert query_string == (
        'order.id, order.created_proc, order.cost,'
        ' order.performer_tariff_currency, order.performer_car,'
        ' order.performer_car_number, order.user_id, order.city,'
        ' order.request_source, order.request_destinations,'
        ' order.request_comment, order.request_requirements,'
        ' order.status_updated, order.performer_tariff_class, order.calc_info,'
        ' order.statistics, index.phone_id'
        ' FROM %t as index JOIN %t AS order ON index.id=order.id'
        ' WHERE order.payment_tech_main_card_payment_id = \'7\''
        ' AND index.phone_id IN (%p)'
        ' AND index.created <= -%p'
        ' AND index.created > -%p'
        ' AND NOT is_null(order.created_proc)'
        ' AND NOT is_null(order.cost)'
        ' AND order.cost > 0'
        ' AND order.payment_tech_type = \'coop_account\''
        ' AND order.status != \'cancelled\''
        ' ORDER BY index.created'
        ' LIMIT %p'
    )

    query_params = select_rows_args['args'][1]
    assert query_params == (
        '//home/taxi/unstable/replica/mongo/indexes/order_proc'
        '/phone_id_created',
        '//home/taxi/unstable/replica/mongo/struct/orders_full',
        phone_ids[0],
        1567555200,
        1568160000,
        1000,
    )

    assert yt_orders == orders.ORDERS
