import datetime

import pytest

from taxi import config
from taxi.core import async
from taxi.core import db
from taxi.internal import dbh
from taxi.internal.taximeter_balance_changes import model_makers
from taxi.internal.taximeter_balance_changes import models
from taxi.internal.taximeter_balance_changes import update_changes
from taxi.internal.taximeter_balance_changes import update_missing_changes

NOW = datetime.datetime(2018, 1, 12, 0, 0)

_reschedule_function_path = (
    'taxi_stq.client.update_taximeter_balance_changes_call_later'
)


@async.inline_callbacks
def _run_job():
    yield update_changes.run('task_id')


class DummyYtClient(object):
    def __init__(self, data):
        self.data = data

    def read_table(self, *args, **kwargs):
        return self.data


@pytest.fixture
def mock_reschedule_function(patch):
    @patch(_reschedule_function_path)
    def _reschedule_task(*args, **kwargs):
        return None

    return _reschedule_task


@pytest.fixture
def mock_uuid(patch):
    @patch('uuid.uuid4')
    def _uuid4():
        class Hex(object):
            hex = 'randomuuid1234'
        return Hex

    return _uuid4


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.inline_callbacks
def test_job_with_empty_bulk(mock_reschedule_function):
    yield _run_job()


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_resizes_for_new_orders(mock_reschedule_function):
    """
    Test that resizes are created correctly for orders with fresh enough
    update date
    """
    resize_cls = dbh.taximeter_balance_changes.Doc
    # order ID -> list of (trust payment id, resize number, delta) tuples
    order_id_to_expected_info = {
        'new_order_1_without_good_transactions': [],
        'new_order_2_zero_resize': [],
        'new_order_3_zero_resize': [
            ('new_order_3_zero_resize', 1, {'ride': -10000}),
        ],
        'new_order_4_nonzero_resize': [
            ('new_order_4_nonzero_resize', 1, {'ride': -10000}),
        ],
        'new_order_5_nonzero_resize': [
            ('new_order_5_nonzero_resize', 1, {'ride': -3000}),
            ('new_order_5_nonzero_resize', 2, {'ride': -7000}),
        ],
        'new_order_6_with_currency_mismatch': [
            ('new_order_6_nonzero_resize', 1, {'ride': -2000}),
        ],
        'new_order_7_nonzero_resize': [
            ('new_order_7_nonzero_resize', 1, {'ride': -40000}),
            ('new_order_7_nonzero_resize', 2, {'ride': -60000}),
        ],
        # New orders, but their transactions were holded too long ago,
        # so no new resizes should be created for them
        'new_order_with_old_transactions_1_without_good_transactions': [],
        'new_order_with_old_transactions_2_zero_resize': [],
        'new_order_with_old_transactions_3_zero_resize': [
            (
                'new_order_with_old_transactions_3_zero_resize',
                1,
                {'ride': -10000}
            ),
        ],
        'new_order_with_old_transactions_4_nonzero_resize': [],
        'new_order_with_old_transactions_5_nonzero_resize': [
            (
                'new_order_with_old_transactions_5_nonzero_resize',
                1,
                {'ride': -3000}
            ),
        ],
        # Orders that are not read from Mongo
        'unfinished_order': [],
        'cash_order': [],
    }
    yield _run_job()
    items = order_id_to_expected_info.iteritems()
    for order_id, expected_resize_infos in items:
        resize_count = yield db.taximeter_balance_changes.find({
            resize_cls.order_id: order_id,
            resize_cls.payment_type: (
                dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE
            )
        }).count()
        assert resize_count == len(expected_resize_infos)
        for expected_resize_info in expected_resize_infos:
            trust_payment_id, resize_number, delta = expected_resize_info
            resize = yield db.taximeter_balance_changes.find_one({
                resize_cls.trust_payment_id: trust_payment_id,
                resize_cls.sequence_number: resize_number,
                resize_cls.payment_type: (
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE
                )
            })
            assert resize
            resize = resize_cls(resize)
            assert resize.currency
            assert resize.clid
            assert resize.db_id
            assert resize.tips_sum_delta == delta.get('tips', 0)
            assert resize.ride_sum_delta == delta.get('ride', 0)


@pytest.mark.parametrize(
    'resizes_enabled',
    [(False), (True)]
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_config_disables_job(mock_reschedule_function, resizes_enabled):
    yield config.WRITE_TAXIMETER_BALANCE_CHANGES.save(resizes_enabled)
    previous_number_of_resizes = yield db.taximeter_balance_changes.count()
    yield _run_job()
    current_number_of_resizes = yield db.taximeter_balance_changes.count()
    number_should_change = resizes_enabled
    number_changed = (previous_number_of_resizes != current_number_of_resizes)
    assert number_changed == number_should_change


@pytest.mark.filldb(orders='multiple_resizes')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_multiple_resizes(mock_reschedule_function):
    order_id = 'multiple_resizes'
    resize_cls = dbh.taximeter_balance_changes.Doc

    # Step 1: no resizes should be created yet
    yield _run_job()
    resize_count = yield db.taximeter_balance_changes.find({
        resize_cls.order_id: order_id,
        resize_cls.payment_type: (
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE
        ),
    }).count()
    assert resize_count == 0

    # Step 2: change sum, we should create 1 resize
    yield db.orders._collection.update(
        {'_id': order_id},
        {'$set': {'billing_tech.transactions.0.sum': {'ride': 60000}}}
    )
    yield _run_job()
    resize_count = yield db.taximeter_balance_changes.find({
        resize_cls.order_id: order_id,
        resize_cls.payment_type: (
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE
        ),
    }).count()
    assert resize_count == 1

    # Step 3: change sum again, we should create one more resize
    yield db.orders._collection.update(
        {'_id': order_id},
        {'$set': {'billing_tech.transactions.0.sum': {'ride': 0}}}
    )
    yield _run_job()
    resize_count = yield db.taximeter_balance_changes.find({
        resize_cls.order_id: order_id,
        resize_cls.payment_type: (
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE
        ),
    }).count()
    assert resize_count == 2

    # Step 4: sum hasn't changed, no more resizes should be created
    yield _run_job()
    resize_count = yield db.taximeter_balance_changes.find({
        resize_cls.order_id: order_id,
        resize_cls.payment_type: (
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE
        ),
    }).count()
    assert resize_count == 2


@pytest.mark.filldb(orders='test_total_delta')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_resize_total_delta(mock_reschedule_function):
    @async.inline_callbacks
    def get_latest_resize(trust_payment_id):
        payment_cls = dbh.taximeter_balance_changes.Doc
        latest_payments, _ = yield payment_cls.get_latest_payments(
            [trust_payment_id], secondary=False
        )
        key = (
            trust_payment_id, dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE
        )
        latest_resize = latest_payments.get(key)
        async.return_value(latest_resize)

    order_id = 'test_total_delta'
    trust_payment_id = 'test_total_delta_transaction'
    yield _run_job()
    resize = yield get_latest_resize(trust_payment_id)
    assert resize.sequence_number == 1
    assert resize.ride_sum_delta == -30000
    assert resize.total_ride_sum_delta == -30000
    yield db.orders._collection.update(
        {'_id': order_id},
        {'$set': {'billing_tech.transactions.0.sum': {'ride': 0}}}
    )
    yield _run_job()
    resize = yield get_latest_resize(trust_payment_id)
    assert resize.sequence_number == 2
    assert resize.ride_sum_delta == -70000
    assert resize.total_ride_sum_delta == -100000


@pytest.mark.filldb(orders='test_compensation_payments')
@pytest.mark.filldb(taximeter_balance_changes='test_compensation_payments')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_compensation_payments(mock_reschedule_function):
    expected_payments = [
        # trust payment id, total delta, delta, sequence number
        (
            'order_5_new_compensation_compensation_1',
            dbh.taximeter_balance_changes.Delta(ride=1990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=1990000, tips=0),
            1
        ),
        (
            'order_6_two_new_compensations_compensation_1',
            dbh.taximeter_balance_changes.Delta(ride=1990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=1990000, tips=0),
            1
        ),
        (
            'order_6_two_new_compensations_compensation_2',
            dbh.taximeter_balance_changes.Delta(ride=2990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=2990000, tips=0),
            1
        ),
        (
            'order_7_compensation_already_saved_compensation_1',
            dbh.taximeter_balance_changes.Delta(ride=1990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=1990000, tips=0),
            1
        ),
    ]
    yield _run_job()
    payment_count = yield db.taximeter_balance_changes.count()
    assert payment_count == len(expected_payments)
    trust_payment_ids = [item[0] for item in expected_payments]
    latest_payments, _ = yield (
        dbh.taximeter_balance_changes.Doc.get_latest_payments(
            trust_payment_ids, secondary=False
        )
    )
    for expected_info in expected_payments:
        trust_payment_id, total_delta, delta, sequence_number = expected_info
        key = (
            trust_payment_id,
            dbh.taximeter_balance_changes.PAYMENT_TYPE_COMPENSATION
        )
        payment = latest_payments[key]
        assert payment.get_total_delta() == total_delta, trust_payment_id
        assert payment.get_delta() == delta, trust_payment_id
        assert payment.sequence_number == sequence_number, trust_payment_id
        assert payment.cleared_by_ride_sum_with == []
        assert payment.cleared_by_tips_sum_with == []


@pytest.mark.filldb(orders='test_refund_payments')
@pytest.mark.filldb(taximeter_balance_changes='test_refund_payments')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_refund_payments(mock_reschedule_function):
    expected_payments = [
        # trust payment id, total delta, delta, sequence number
        (
            'new_refund',
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            1
        ),
        (
            'transaction_with_two_refunds_refund_1',
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            1
        ),
        (
            'transaction_with_two_refunds_refund_2',
            dbh.taximeter_balance_changes.Delta(ride=-2990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-2990000, tips=0),
            1
        ),
        (
            'already_stored_refund',
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            1
        ),
    ]
    yield _run_job()
    payment_count = yield db.taximeter_balance_changes.find({
        dbh.taximeter_balance_changes.Doc.payment_type: (
            dbh.taximeter_balance_changes.PAYMENT_TYPE_REFUND
        )
    }).count()
    assert payment_count == len(expected_payments)
    trust_payment_ids = [item[0] for item in expected_payments]
    latest_payments, _ = yield (
        dbh.taximeter_balance_changes.Doc.get_latest_payments(
            trust_payment_ids, secondary=False
        )
    )
    for expected_info in expected_payments:
        trust_payment_id, total_delta, delta, sequence_number = expected_info
        key = (
            trust_payment_id, dbh.taximeter_balance_changes.PAYMENT_TYPE_REFUND
        )
        payment = latest_payments[key]
        assert payment.get_total_delta() == total_delta, trust_payment_id
        assert payment.get_delta() == delta, trust_payment_id
        assert payment.sequence_number == sequence_number, trust_payment_id
        assert payment.cleared_by_ride_sum_with == []
        assert payment.cleared_by_tips_sum_with == []


@pytest.mark.filldb(orders='test_compensation_refund_payments')
@pytest.mark.filldb(
    taximeter_balance_changes='test_compensation_refund_payments'
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_compensation_refund_payments(mock_reschedule_function):
    expected_payments = [
        # trust payment id, total delta, delta, sequence number
        (
            'new_refund',
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            1
        ),
        (
            'compensation_with_two_refunds_refund_1',
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            1
        ),
        (
            'compensation_with_two_refunds_refund_2',
            dbh.taximeter_balance_changes.Delta(ride=-2990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-2990000, tips=0),
            1
        ),
        (
            'already_stored_refund',
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-1990000, tips=0),
            1
        ),
    ]
    yield _run_job()
    payment_count = yield db.taximeter_balance_changes.count()
    assert payment_count == len(expected_payments)
    trust_payment_ids = [item[0] for item in expected_payments]
    latest_payments, _ = yield (
        dbh.taximeter_balance_changes.Doc.get_latest_payments(
            trust_payment_ids, secondary=False
        )
    )
    for expected_info in expected_payments:
        trust_payment_id, total_delta, delta, sequence_number = expected_info
        payment = latest_payments[(
            trust_payment_id,
            dbh.taximeter_balance_changes.PAYMENT_TYPE_COMPENSATION_REFUND
        )]
        assert payment.get_total_delta() == total_delta, trust_payment_id
        assert payment.get_delta() == delta, trust_payment_id
        assert payment.sequence_number == sequence_number, trust_payment_id
        assert payment.cleared_by_ride_sum_with == []
        assert payment.cleared_by_tips_sum_with == []


@pytest.mark.filldb(
    orders='test_driverchange', taximeter_balance_changes='empty'
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_driverchange_payments():
    expected_payments = [
        # payment id, total delta, delta, sequence number
        (
            'trust_payment_id_test',
            dbh.taximeter_balance_changes.Delta(ride=-3200000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-3200000, tips=0),
            1
        ),
    ]
    yield _run_job()
    payment_count = yield db.taximeter_balance_changes.count()
    assert payment_count == len(expected_payments)
    payment_ids = [item[0] for item in expected_payments]
    latest_payments, _ = yield (
        dbh.taximeter_balance_changes.Doc.get_latest_payments(
            payment_ids, secondary=False
        )
    )
    for expected_info in expected_payments:
        trust_payment_id, total_delta, delta, sequence_number = expected_info
        key = (
            trust_payment_id,
            dbh.taximeter_balance_changes.PAYMENT_TYPE_CHANGE
        )
        payment = latest_payments[key]
        assert payment.get_total_delta() == total_delta, trust_payment_id
        assert payment.get_delta() == delta, trust_payment_id
        assert payment.sequence_number == sequence_number, trust_payment_id
        assert payment.cleared_by_ride_sum_with == []
        assert payment.cleared_by_tips_sum_with == []


@pytest.mark.parametrize(
    'test_mode_enabled,expected_result_count',
    [
        (False, 0),
        (True, 6)
    ]
)
@pytest.mark.filldb(
    orders='test_orders_without_experiment_are_skipped',
    taximeter_balance_changes='test_orders_without_experiment_are_skipped',
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_orders_without_experiment_are_skipped(
        mock_reschedule_function, test_mode_enabled, expected_result_count):
    yield config.TAXIMETER_BALANCE_CHANGES_TEST_MODE_ENABLED.save(
        test_mode_enabled
    )
    yield _run_job()
    item_count = yield db.taximeter_balance_changes.find({}).count()
    assert item_count == expected_result_count


@pytest.mark.filldb(
    orders='test_job_fails_on_duplicate_payments',
    taximeter_balance_changes='test_job_fails_on_duplicate_payments',
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_job_fails_on_duplicate_compensations(mock_reschedule_function):
    """
    Should not create duplicate one-time payments
    """
    original_item_count = yield db.taximeter_balance_changes.find({}).count()
    yield _run_job()
    item_count = yield db.taximeter_balance_changes.find({}).count()
    assert item_count == original_item_count


@pytest.mark.filldb(orders='test_initial_transaction_sums')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_initial_transaction_sums(mock_reschedule_function):
    expected_payments = [
        # trust payment id, clid, payment type, total delta, delta,
        # sequence number
        (
            'card',
            'payload_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            'RUB',
            1
        ),
        (
            'without_performer_id',
            'without_performer_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            'EUR',
            1
        ),
        (
            'yandex_card',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            'RUB',
            1
        ),
        (
            'sbp',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            'RUB',
            1
        ),
        (
            'applepay',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_APPLEPAY,
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            'RUB',
            1
        ),
        (
            'googlepay',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_GOOGLEPAY,
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            'RUB',
            1
        ),
        (
            'corp',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_CORPORATE,
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=20000, tips=0),
            'RUB',
            1
        ),
    ]
    yield _run_job()
    payment_count = yield db.taximeter_balance_changes.find({
        dbh.taximeter_balance_changes.Doc.payment_type: {
            '$in': [
                dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                dbh.taximeter_balance_changes.PAYMENT_TYPE_APPLEPAY,
                dbh.taximeter_balance_changes.PAYMENT_TYPE_GOOGLEPAY,
                dbh.taximeter_balance_changes.PAYMENT_TYPE_CORPORATE,
            ]
        }
    }).count()
    assert payment_count == len(expected_payments)
    trust_payment_ids = [item[0] for item in expected_payments]
    latest_payments, _ = yield (
        dbh.taximeter_balance_changes.Doc.get_latest_payments(
            trust_payment_ids, secondary=False
        )
    )
    for expected_info in expected_payments:
        (
            trust_payment_id,
            clid,
            payment_type,
            total_delta,
            delta,
            currency,
            sequence_number
        ) = expected_info
        key = (
            trust_payment_id, payment_type
        )
        payment = latest_payments[key]
        assert payment.get_total_delta() == total_delta, trust_payment_id
        assert payment.get_delta() == delta, trust_payment_id
        assert payment.currency == currency
        assert payment.sequence_number == sequence_number, trust_payment_id
        assert payment.clid == clid
        assert payment.cleared_by_ride_sum_with == []
        assert payment.cleared_by_tips_sum_with == []


@pytest.mark.filldb(
    orders='test_transaction_clear_fail',
    taximeter_balance_changes='test_transaction_clear_fail'
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_transaction_clear_fail(mock_reschedule_function):
    # payment type, trust payment id, sequence number, delta, total delta
    expected_changes_by_order_id = {
        # failed order without existing changes
        'order_1': [],
        # failed order with existing changes
        'order_2': [
            (
                dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                'order_2_tr_1',
                1,
                dbh.taximeter_balance_changes.Delta(ride=1000000, tips=0),
                dbh.taximeter_balance_changes.Delta(ride=1000000, tips=0)
            ),
            (
                dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
                'order_2_tr_1',
                1,
                dbh.taximeter_balance_changes.Delta(ride=-100000, tips=0),
                dbh.taximeter_balance_changes.Delta(ride=-100000, tips=0)
            ),
            (
                dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
                'order_2_tr_1',
                2,
                dbh.taximeter_balance_changes.Delta(ride=-200000, tips=0),
                dbh.taximeter_balance_changes.Delta(ride=-300000, tips=0)
            ),
            (
                dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                'order_2_tr_1',
                2,
                dbh.taximeter_balance_changes.Delta(ride=-1000000, tips=0),
                dbh.taximeter_balance_changes.Delta(ride=0, tips=0)
            ),
            (
                dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
                'order_2_tr_1',
                3,
                dbh.taximeter_balance_changes.Delta(ride=300000, tips=0),
                dbh.taximeter_balance_changes.Delta(ride=0, tips=0)
            ),
        ],
        # failed order with already cancelled changes
        'order_3': [
            (
                dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                'order_3_tr_1',
                1,
                dbh.taximeter_balance_changes.Delta(ride=1000000, tips=0),
                dbh.taximeter_balance_changes.Delta(ride=1000000, tips=0)
            ),
            (
                dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
                'order_3_tr_1',
                1,
                dbh.taximeter_balance_changes.Delta(ride=-100000, tips=0),
                dbh.taximeter_balance_changes.Delta(ride=-100000, tips=0)
            ),
            (
                dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
                'order_3_tr_1',
                2,
                dbh.taximeter_balance_changes.Delta(ride=-200000, tips=0),
                dbh.taximeter_balance_changes.Delta(ride=-300000, tips=0)
            ),
            (
                dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                'order_3_tr_1',
                2,
                dbh.taximeter_balance_changes.Delta(ride=-1000000, tips=0),
                dbh.taximeter_balance_changes.Delta(ride=0, tips=0)
            ),
            (
                dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
                'order_3_tr_1',
                3,
                dbh.taximeter_balance_changes.Delta(ride=300000, tips=0),
                dbh.taximeter_balance_changes.Delta(ride=0, tips=0)
            ),
        ]
    }
    change_cls = dbh.taximeter_balance_changes.Doc

    yield _run_job()

    for order_id, change_infos in expected_changes_by_order_id.iteritems():
        changes_count = yield db.taximeter_balance_changes.find({
            change_cls.order_id: order_id
        }).count()
        assert changes_count == len(change_infos), order_id
        for change_info in change_infos:
            (
                payment_type,
                trust_payment_id,
                sequence_number,
                delta,
                total_delta
            ) = change_info
            change = yield db.taximeter_balance_changes.find_one({
                change_cls.trust_payment_id: trust_payment_id,
                change_cls.sequence_number: sequence_number,
                change_cls.payment_type: payment_type
            })
            assert change, order_id
            change = change_cls(change)
            assert change.get_delta() == delta, order_id
            assert change.get_total_delta() == total_delta, order_id
            assert change.cleared_by_ride_sum_with == []  # Not set
            assert change.cleared_by_tips_sum_with == []  # Not set


@pytest.mark.parametrize(
    'order_id,expected_count,expected_umbrella_alias_id',
    [
        (
            'embedded_with_umbrella_alias_id',
            1,
            'umbrella_alias_id',
        ),
        (
            'embedded_without_umbrella_alias_id',
            0,
            None,
        )
    ]
)
@pytest.mark.filldb(orders='test_pool_orders')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_pool_orders(mock_reschedule_function, order_id, expected_count,
                     expected_umbrella_alias_id):
    yield _run_job()
    payments = yield db.taximeter_balance_changes.find({
        dbh.taximeter_balance_changes.Doc.order_id: order_id
    }).run()
    assert len(payments) == expected_count
    for payment in payments:
        assert payment['umbrella_alias_id'] == expected_umbrella_alias_id


@pytest.mark.parametrize(
    'missing_ids,expected_ids',
    [
        (
            [],
            ['3']
        ),
        (
            ['1_ride', '2_ride', '3_ride', '3_tips'],
            ['1', '2', '3']
        )
    ]
)
@pytest.mark.filldb(
    taximeter_balance_changes='test_update_missing_changes',
    missing_taximeter_balance_changes='test_update_missing_changes',
)
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_update_missing_changes(monkeypatch, missing_ids, expected_ids):
    client = DummyYtClient(
        [{'payment_id': payment_id} for payment_id in missing_ids]
    )
    monkeypatch.setattr(
        'taxi.external.yt_wrapper._environments', {'test_cluster': client}
    )

    yield update_missing_changes.run(
        'test_cluster',
        '//output_table_path',
        'lower_key',
        'upper_key',
    )
    stored_changes = yield db.missing_taximeter_balance_changes.find().run()
    ids = [change['_id'] for change in stored_changes]
    assert set(ids) == set(expected_ids)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    WRITE_TAXIMETER_BALANCE_CHANGES=True,
    TAXIMETER_BALANCE_CHANGES_USE_SINGLE_TASK_ID=True,
)
@pytest.inline_callbacks
def test_reschedule_with_single_task(mock_reschedule_function):
    yield _run_job()
    assert mock_reschedule_function.calls == [{
        'args': (),
        'kwargs': {
            'log_extra': {'extdict': {
                'from_date': '2018-01-12T03:00:05+0300',
                'to_date': '2018-01-12T03:00:00+0300'
            }},
            'eta': datetime.datetime(2018, 1, 12, 0, 0, 10),
            'task_id': 'taximeter_balance_changes_task_id',
        }
    }]


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    WRITE_TAXIMETER_BALANCE_CHANGES=True,
    TAXIMETER_BALANCE_CHANGES_USE_SINGLE_TASK_ID=False,
)
@pytest.inline_callbacks
def test_reschedule_without_single_task(mock_reschedule_function, mock_uuid):
    yield _run_job()
    assert mock_reschedule_function.calls == [{
        'args': (),
        'kwargs': {
            'log_extra': {'extdict': {
                'from_date': '2018-01-12T03:00:05+0300',
                'to_date': '2018-01-12T03:00:00+0300'
            }},
            'eta': datetime.datetime(2018, 1, 12, 0, 0, 10),
            'task_id': 'randomuuid1234',
        }
    }]


@pytest.mark.filldb(orders='test_personal_wallet')
@pytest.mark.filldb(taximeter_balance_changes='test_personal_wallet')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.inline_callbacks
def test_personal_wallet():
    yield _run_job()
    payments = yield db.taximeter_balance_changes.find({
        dbh.taximeter_balance_changes.Doc.order_id: 'order_personal_wallet'
    }).run().result
    assert len(payments) == 0


@pytest.mark.filldb(orders='test_cash_order_compensations')
@pytest.mark.filldb(taximeter_balance_changes='empty')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.mark.parametrize(
    'use_new_query_for_taximeter_balance_changes, '
    'expected_trust_payment_ids',
    [
        (
                False,
                []
        ),
        (
                True,
                [
                    'cash_order_with_transactions',
                    'cash_order_with_compensations'
                ]
        ),

    ]
)
@pytest.inline_callbacks
def test_cash_order_compensations(
        use_new_query_for_taximeter_balance_changes,
        expected_trust_payment_ids,
        patch
):
    @patch('taxi.config.USE_NEW_QUERY_FOR_TAXIMETER_BALANCE_CHANGES.get')
    @async.inline_callbacks
    def get():
        yield
        async.return_value(use_new_query_for_taximeter_balance_changes)

    yield _run_job()
    payments = yield db.taximeter_balance_changes.find({
        dbh.taximeter_balance_changes.Doc.order_id: {'$ne': None}
    }).run().result
    trust_payment_ids = [payment['trust_payment_id'] for payment in payments]
    assert sorted(trust_payment_ids) == sorted(expected_trust_payment_ids)


def _make_order_info(
    alias_id='some_alias_id', driver_uuid='some_uuid', clid='some_clid',
    db_id='some_db_id',
):
    return models.OrderInfo(
        currency='RUB',
        id='some_order_id',
        alias_id=alias_id,
        due=datetime.datetime(2021, 1, 1),
        umbrella_alias_id=None,
        driver_uuid=driver_uuid,
        clid=clid,
        db_id=db_id,
        contract_currency='RUB',
        contract_currency_rate='1',
    )


@pytest.mark.parametrize('order_info,transaction,expected', [
    # should return original order_info if transaction_payload is missing
    (
        _make_order_info(),
        {},
        _make_order_info(),
    ),
    # should return modified order_info if transaction_payload is present
    (
        _make_order_info(
            alias_id='some_alias_id',
            driver_uuid='some_uuid',
            clid='some_clid',
            db_id='some_db_id',
        ),
        {
            'transaction_payload': {
                'alias_id': 'payload_alias_id',
                'driver': {
                    'clid': 'payload_clid',
                    'park_id': 'payload_db_id',
                    'driver_profile_id': 'payload_uuid',
                }
            }
        },
        _make_order_info(
            alias_id='payload_alias_id',
            driver_uuid='payload_uuid',
            clid='payload_clid',
            db_id='payload_db_id',
        ),
        # should return original order_info if transaction_payload is broken
    ),
    (
        _make_order_info(),
        {'transaction_payload': {}},
        _make_order_info(),
    )
])
def test_safe_get_effective_order_info(order_info, transaction, expected):
    actual = model_makers._safe_get_effective_order_info(
        order_info, transaction
    )
    assert actual == expected


@pytest.mark.filldb(orders='test_mark_transactions_fact')
@pytest.mark.filldb(taximeter_balance_changes='empty')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_CLEAR_TRANSACTIONS=[
        {
            'from_due': '2000-01-01T00:00:00+03:00',
            'to_due': '2999-01-01T00:00:00+03:00',
        }
    ]
)
@pytest.inline_callbacks
def test_mark_transactions_fact(mock_reschedule_function):
    expected_payments = [
        # trust payment id, clid, payment type, total delta, delta,
        # sequence number, cleared_by_ride_sum_with, cleared_by_tips_sum_with
        (
            'transaction_1',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
            dbh.taximeter_balance_changes.Delta(ride=100000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=100000, tips=0),
            'RUB',
            1,
            [
                [
                    'transaction_1',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
                    1
                ]
            ],
            [],
        ),
        (
            'transaction_1',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
            dbh.taximeter_balance_changes.Delta(ride=-100000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-100000, tips=0),
            'RUB',
            1,
            [
                [
                    'transaction_1',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                    1
                ]
            ],
            [],
        ),
        (
            'transaction_2',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
            dbh.taximeter_balance_changes.Delta(ride=100000, tips=100000),
            dbh.taximeter_balance_changes.Delta(ride=100000, tips=100000),
            'RUB',
            1,
            [],
            [
                [
                    'transaction_2',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
                    1
                ]
            ],
        ),
        (
            'transaction_2',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
            dbh.taximeter_balance_changes.Delta(ride=0, tips=-100000),
            dbh.taximeter_balance_changes.Delta(ride=0, tips=-100000),
            'RUB',
            1,
            [],
            [
                [
                    'transaction_2',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                    1
                ]
            ],
        ),
        (
            'transaction_3',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
            dbh.taximeter_balance_changes.Delta(ride=100000, tips=100000),
            dbh.taximeter_balance_changes.Delta(ride=100000, tips=100000),
            'RUB',
            1,
            [
                [
                    'transaction_3',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
                    1
                ]
            ],
            [
                [
                    'transaction_3',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
                    1
                ]
            ],
        ),
        (
            'transaction_3',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
            dbh.taximeter_balance_changes.Delta(ride=-100000, tips=-100000),
            dbh.taximeter_balance_changes.Delta(ride=-100000, tips=-100000),
            'RUB',
            1,
            [
                [
                    'transaction_3',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                    1
                ]
            ],
            [
                [
                    'transaction_3',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                    1
                ]
            ],
        ),
    ]
    yield _run_job()
    payment_count = yield db.taximeter_balance_changes.find({}).count()
    assert payment_count == len(expected_payments)
    trust_payment_ids = [item[0] for item in expected_payments]
    latest_payments, _ = yield (
        dbh.taximeter_balance_changes.Doc.get_latest_payments(
            trust_payment_ids, secondary=False
        )
    )
    for expected_info in expected_payments:
        (
            trust_payment_id,
            clid,
            payment_type,
            total_delta,
            delta,
            currency,
            sequence_number,
            cleared_by_ride_sum_with,
            cleared_by_tips_sum_with,
        ) = expected_info
        key = (
            trust_payment_id, payment_type
        )
        payment = latest_payments[key]
        assert payment.get_total_delta() == total_delta, trust_payment_id
        assert payment.get_delta() == delta, trust_payment_id
        assert payment.currency == currency
        assert payment.sequence_number == sequence_number, trust_payment_id
        assert payment.clid == clid
        assert payment.cleared_by_ride_sum_with == cleared_by_ride_sum_with
        assert payment.cleared_by_tips_sum_with == cleared_by_tips_sum_with


@pytest.mark.filldb(orders='test_mark_resize_like_hold_fact')
@pytest.mark.filldb(taximeter_balance_changes='test_mark_resize_like_hold_fact')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(WRITE_TAXIMETER_BALANCE_CHANGES=True)
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_UPDATE_INTERVALS_OVERLAP=(1 * 24 * 3600)
)
@pytest.mark.config(TAXIMETER_BALANCE_CHANGES_MAX_PAYMENT_AGE=(2 * 24 * 3600))
@pytest.mark.config(
    TAXIMETER_BALANCE_CHANGES_CLEAR_TRANSACTIONS=[
        {
            'from_due': '2000-01-01T00:00:00+03:00',
            'to_due': '2999-01-01T00:00:00+03:00',
        }
    ]
)
@pytest.inline_callbacks
def test_mark_resize_like_hold_fact(mock_reschedule_function):
    expected_payments = [
        # trust payment id, clid, payment type, total delta, delta,
        # sequence number, cleared_by_ride_sum_with, cleared_by_tips_sum_with
        (
            'transaction_1',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
            dbh.taximeter_balance_changes.Delta(ride=-100000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-100000, tips=0),
            'RUB',
            1,
            [],
            [],
        ),
        (
            'transaction_2',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
            dbh.taximeter_balance_changes.Delta(ride=-100000, tips=0),
            dbh.taximeter_balance_changes.Delta(ride=-100000, tips=0),
            'RUB',
            1,
            [
                [
                    'transaction_2',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                    1
                ]
            ],
            [],
        ),
        (
            'transaction_3',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
            dbh.taximeter_balance_changes.Delta(ride=-100000, tips=-100000),
            dbh.taximeter_balance_changes.Delta(ride=-100000, tips=-100000),
            'RUB',
            1,
            [
                [
                    'transaction_3',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                    1
                ]
            ],
            [
                [
                    'transaction_3',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                    1
                ]
            ],
        ),
        (
            'transaction_4',
            'park_clid',
            dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
            dbh.taximeter_balance_changes.Delta(ride=0, tips=-100000),
            dbh.taximeter_balance_changes.Delta(ride=0, tips=-100000),
            'RUB',
            1,
            [],
            [
                [
                    'transaction_4',
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_CARD,
                    1
                ]
            ],
        ),
    ]
    yield _run_job()
    payment_count = yield db.taximeter_balance_changes.find(
        {
            dbh.taximeter_balance_changes.Doc.payment_type: {
                '$in': [
                    dbh.taximeter_balance_changes.PAYMENT_TYPE_RESIZE,
                ]
            }
        }
    ).count()
    assert payment_count == len(expected_payments)
    trust_payment_ids = [item[0] for item in expected_payments]
    latest_payments, all_payments = yield (
        dbh.taximeter_balance_changes.Doc.get_latest_payments(
            trust_payment_ids, secondary=False
        )
    )
    for expected_info in expected_payments:
        (
            trust_payment_id,
            clid,
            payment_type,
            total_delta,
            delta,
            currency,
            sequence_number,
            cleared_by_ride_sum_with,
            cleared_by_tips_sum_with,
        ) = expected_info
        key = (
            trust_payment_id, payment_type
        )
        payment = latest_payments[key]
        assert payment.get_total_delta() == total_delta, trust_payment_id
        assert payment.get_delta() == delta, trust_payment_id
        assert payment.currency == currency
        assert payment.sequence_number == sequence_number, trust_payment_id
        assert payment.clid == clid
        assert payment.cleared_by_ride_sum_with == cleared_by_ride_sum_with
        assert payment.cleared_by_tips_sum_with == cleared_by_tips_sum_with
