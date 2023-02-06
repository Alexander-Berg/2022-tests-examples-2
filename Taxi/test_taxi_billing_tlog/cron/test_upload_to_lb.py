import datetime as dt
import json

from dateutil import tz
import pytest

from taxi_billing_tlog import logbroker
from taxi_billing_tlog import pgaas
from taxi_billing_tlog.crontasks import upload_to_lb
from taxi_billing_tlog.yt import converters
from taxi_billing_tlog.yt import schemas


@pytest.mark.now('2019-08-05T12:00:00')
@pytest.mark.config(
    BILLING_TLOG_UPLOAD_TO_LB_SETTINGS={
        'test_topic': {'is_enabled': True, 'max_inflight': 10},
    },
    BILLING_TLOG_UPLOAD_TO_LB_MAX_ITERATIONS=5,
    # Actually defined in journal_json
    BILLING_TLOG_UPLOAD_TO_LB_BATCH_SIZE=50000,
    BILLING_TLOG_YT_COLUMNS_FILTERS={
        'revenues': {'contract_id': {'from_date': '2020-06-25'}},
        'expenses': {'contract_id': {'from_date': '2020-06-25'}},
    },
    BILLING_TLOG_UPLOAD_TO_YT_RESTRICTED_PERIODS=[
        {'start': '13:00', 'end': '15:00'},
    ],
    BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
        'order': {'payment': 1, 'refund': -1},
        'coupon': {'payment': -1, 'refund': 1},
        'client_b2b_trip_payment': {'payment': 1, 'refund': -1},
        'driver_workshift': {'payment': 1, 'refund': -1},
        'card_trips_agency_commission': {'payment': 1, 'refund': -1},
        'card_trips_acquiring_commission': {'payment': 1, 'refund': -1},
        'food_payment': {'payment': 1, 'refund': -1},
    },
)
@pytest.mark.parametrize(
    'journal_json,'
    'expected_data_json,'
    'row_filter_cls,'
    'row_converter_cls,'
    'yt_schema_cls',
    [
        (
            'journal.json',
            'revenues.json',
            pgaas.RevenuesRowFilter,
            converters.RevenuesRowConverter,
            schemas.RevenuesYtSchema,
        ),
        (
            'journal.json',
            'expenses.json',
            pgaas.ExpensesRowFilter,
            converters.ExpensesRowConverter,
            schemas.ExpensesYtSchema,
        ),
        (
            'payments_journal.json',
            'payments.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            schemas.PaymentsYtSchema,
        ),
    ],
)
@pytest.mark.nofilldb
async def test_upload_to_lb(
        patch,
        cron_context,
        mock_psycopg2,
        mock_yt_client,
        load_json,
        journal_json,
        expected_data_json,
        row_filter_cls,
        row_converter_cls,
        yt_schema_cls,
):
    journals = load_json(journal_json)
    expected_data = load_json(expected_data_json)

    expected_entries = expected_data['logbroker_entries']

    mock_psycopg2.fetchone_results = journals['max_ids']
    mock_psycopg2.fetchall_results = journals['entries']

    data_chunk_sent = []

    @patch('taxi_billing_tlog.logbroker.wrapper.LogbrokerWrapper.write')
    async def _write(data_chunk, topic, source_id, partition_group=None):
        assert topic == '/test_topic'
        assert source_id == 'test_consumer_id'
        assert partition_group is None
        json_chunks = [json.loads(event.data) for event in data_chunk]
        data_chunk_sent.append(json_chunks)

    await upload_to_lb.upload(
        context=cron_context,
        topic=logbroker.Topic(
            name='test_topic',
            logbroker_path='/test_topic',
            schema=yt_schema_cls(cron_context),
        ),
        row_filter=row_filter_cls(),
        row_converter=row_converter_cls(context=cron_context),
        consumer_id='test_consumer_id',
        journal_table='journal',
        log_extra={},
    )

    assert data_chunk_sent == expected_entries


@pytest.mark.now('2019-08-05T12:00:00')
@pytest.mark.config(
    BILLING_TLOG_UPLOAD_TO_LB_SETTINGS={
        'test_topic': {'is_enabled': True, 'max_inflight': 10},
    },
    BILLING_TLOG_UPLOAD_TO_LB_MAX_ITERATIONS=1,
    # Actually defined in journal_json
    BILLING_TLOG_UPLOAD_TO_LB_BATCH_SIZE=50000,
    BILLING_TLOG_YT_COLUMNS_FILTERS={
        'revenues': {'contract_id': {'from_date': '2020-06-25'}},
        'expenses': {'contract_id': {'from_date': '2020-06-25'}},
    },
    BILLING_TLOG_UPLOAD_TO_YT_RESTRICTED_PERIODS=[
        {'start': '13:00', 'end': '15:00'},
    ],
    BILLING_TLOG_AGGREGATION_SIGN_BY_PRODUCT={
        'order': {'payment': 1, 'refund': -1},
        'coupon': {'payment': -1, 'refund': 1},
        'client_b2b_trip_payment': {'payment': 1, 'refund': -1},
        'driver_workshift': {'payment': 1, 'refund': -1},
        'card_trips_agency_commission': {'payment': 1, 'refund': -1},
        'card_trips_acquiring_commission': {'payment': 1, 'refund': -1},
        'food_payment': {'payment': 1, 'refund': -1},
    },
    BILLING_TLOG_SCHEDULER_ENABLED=True,
    BILLING_TLOG_SCHEDULER_SETTINGS={
        'jitter': 0,
        'lag': 300,
        'shifts': ['10:00'],
        'concurrency': 2,
    },
)
@pytest.mark.parametrize(
    'journal_json,'
    'expected_data_json,'
    'row_filter_cls,'
    'row_converter_cls,'
    'yt_schema_cls,'
    'expected_stq_calls',
    [
        (
            'journal.json',
            'revenues.json',
            pgaas.RevenuesRowFilter,
            converters.RevenuesRowConverter,
            schemas.RevenuesYtSchema,
            [
                (
                    'bci/7634/2019-08-06T10:00:00+00:00',
                    dt.datetime(2019, 8, 6, 10, 5, tzinfo=tz.tzutc()),
                ),
            ],
        ),
        (
            'journal.json',
            'expenses.json',
            pgaas.ExpensesRowFilter,
            converters.ExpensesRowConverter,
            schemas.ExpensesYtSchema,
            [
                (
                    'bci/7634/2019-08-06T10:00:00+00:00',
                    dt.datetime(2019, 8, 6, 10, 5, tzinfo=tz.tzutc()),
                ),
            ],
        ),
        (
            'payments_journal.json',
            'payments.json',
            pgaas.AllowAllRowFilter,
            converters.IdentityRowConverter,
            schemas.PaymentsYtSchema,
            [
                (
                    'bci/7634/2019-08-06T10:00:00+00:00',
                    dt.datetime(2019, 8, 6, 10, 5, tzinfo=tz.tzutc()),
                ),
            ],
        ),
    ],
)
@pytest.mark.nofilldb
async def test_upload_to_lb_with_scheduler(
        patch,
        cron_context,
        mock_psycopg2,
        mock_yt_client,
        load_json,
        journal_json,
        expected_data_json,
        expected_stq_calls,
        row_filter_cls,
        row_converter_cls,
        yt_schema_cls,
):
    journals = load_json(journal_json)

    mock_psycopg2.fetchone_results = journals['max_ids']
    mock_psycopg2.fetchall_results = journals['entries']

    stq_tasks = []

    @patch('taxi_billing_tlog.logbroker.wrapper.LogbrokerWrapper.write')
    async def _write(data_chunk, topic, source_id, partition_group=None):
        pass

    @patch('taxi.clients.stq_agent.StqAgentClient.put_task')
    async def _put_task(queue, eta=None, task_id=None, args=None, kwargs=None):
        assert queue == 'billing_functions_netting_scheduler'
        stq_tasks.append((task_id, eta))

    await upload_to_lb.upload(
        context=cron_context,
        topic=logbroker.Topic(
            name='test_topic',
            logbroker_path='/test_topic',
            schema=yt_schema_cls(cron_context),
        ),
        row_filter=row_filter_cls(),
        row_converter=row_converter_cls(context=cron_context),
        consumer_id='test_consumer_id',
        journal_table='journal',
        log_extra={},
    )

    assert stq_tasks == expected_stq_calls
