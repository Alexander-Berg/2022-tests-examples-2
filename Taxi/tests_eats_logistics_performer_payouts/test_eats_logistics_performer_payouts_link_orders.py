import dateutil
import pytest


# Kwarg helpers:


def order_kwargs(external_performer_id, external_order_id, event_triggered_at):
    return {
        'order_id': external_order_id,
        'performer_id': external_performer_id,
        'triggered_at': event_triggered_at,
    }


# DB helpers:


def get_all_ids(pg_cursor):
    query = """
SELECT external_id
FROM eats_logistics_performer_payouts.subjects
ORDER BY id;
    """
    pg_cursor.execute(query)
    ids = []
    pg_ids = pg_cursor.fetchall()
    for pg_id in pg_ids:
        ids.append(pg_id[0])

    return ids


def get_linked_shift_id(cursor, order_id):
    # $1 - external order ID
    query_template = """
SELECT shift_sbj.external_id AS id
FROM eats_logistics_performer_payouts.subjects_subjects AS rel
    JOIN eats_logistics_performer_payouts.subjects AS order_sbj
    ON order_sbj.id = rel.subject_id AND order_sbj.subject_type_id = 8
    JOIN eats_logistics_performer_payouts.subjects AS shift_sbj
    ON shift_sbj.id = rel.related_subject_id AND shift_sbj.subject_type_id = 2
WHERE order_sbj.external_id = '{}';
    """
    cursor.execute(query_template.format(order_id))
    related_shift = cursor.fetchone()

    return related_shift['id'] if related_shift is not None else None


# Pulse helpers:


# pulse_value is a string with format 'yyyy-mm-dd HH:MM:SS+03'
def upsert_pulse(pg_cursor, pulse_name, pulse_value):
    # $1 - pulse name (aka id)
    # $2 - pulse value
    query_template = """
INSERT
INTO eats_logistics_performer_payouts.pulses ( id, timestamp_at, updated_at )
VALUES ( '{}', '{}'::TIMESTAMPTZ, NOW() )
ON CONFLICT ( id )
DO
    UPDATE
    SET timestamp_at = EXCLUDED.timestamp_at,
        updated_at = EXCLUDED.updated_at;
    """
    pg_cursor.execute(query_template.format(pulse_name, pulse_value))


PULSE_PERFORMER = 'PERFORMER_FETCH'
PULSE_SHIFT = 'SHIFT_FETCH'


# Cfg shortcuts:

CFG_LINKING_SETTINGS = {
    'point_linkage_interval_cf': 2.0,
    'segment_linkage_interval_s': 1800,  # 30 min
    'max_time_since_previous_shift_s': 1800,  # 30 min
    'reschedule_delay_ms': 60000,
}

CFG_FETCH_SETTINGS = {
    'periodic_courier_profiles': {
        'period_ms': 60000,
        'entry_limit': 100,
        'initial_cursor': '',
        'is_enabled': True,
    },
    'periodic_courier_services': {
        'period_ms': 3600000,
        'entry_limit': 100,
        'initial_cursor': '',
        'is_enabled': True,
    },
    'periodic_courier_shifts': {
        'period_ms': 60000,  # 1 min
        'entry_limit': 100,
        'initial_cursor': '',
        'is_enabled': True,
    },
    'periodic_salary_adjustments': {
        'period_ms': 3600000,
        'entry_limit': 100,
        'initial_cursor': '',
        'is_enabled': True,
    },
}


# DB shortcuts:

DB_NAME = 'eats_logistics_performer_payouts'
DB_FILES = ['eats_logistics_performer_payouts/insert_orders_subjects.sql']


# Tests:


# Check linkfing of order to shift (multiple cases).
@pytest.mark.pgsql(DB_NAME, files=DB_FILES)
@pytest.mark.config(
    EATS_LOGISTICS_PERFORMER_PAYOUTS_SHIFT_ORDER_LINKING_SETTINGS_V2=(  # noqa: E501
        CFG_LINKING_SETTINGS
    ),
    EATS_LOGISTICS_PERFORMER_PAYOUTS_FETCH_SETTINGS_V2=CFG_FETCH_SETTINGS,
)
@pytest.mark.parametrize(
    'current_time,pulse_time_pg,stq_order_kwargs,reschedule_count,'
    + 'linked_shift_id',
    [
        # Happy path
        pytest.param(
            '2021-12-24T17:06:47+00:00',
            '2021-12-24 20:06:00+03',
            order_kwargs('42', '42-73', '2021-12-24T17:05:47+00:00'),
            0,
            '1',
            id='in progress; order within the shift; point; linked',
        ),
        # Sanity check - that timestamps are handled fairly
        pytest.param(
            '2021-12-24T20:06:47+03:00',
            '2021-12-24 20:06:00+03',
            order_kwargs('42', '42-73', '2021-12-24T20:05:47+03:00'),
            0,
            '1',
            id=(
                'in progress; order within the shift; point; linked; '
                'custom timezone'
            ),
        ),
        # If there were no shift '1', point-linking would fail and when
        # segment-linking will apply it would certainly be linked to shift '2'
        pytest.param(
            '2021-12-24T09:17:30+00:00',
            '2021-12-24 12:17:00+03',
            order_kwargs('42', '42-73', '2021-12-24T09:16:30+00:00'),
            0,
            '1',
            id='in progress; order at the beginning; point; linked',
        ),
        # Linked, because 'max_time_until_previous_shift' is greater, than
        # 'event_timestamp' - 'planned_end_at'. Order "magnets" to the shift
        pytest.param(
            '2021-12-24T17:25:40+00:00',
            '2021-12-24 21:20:00+03',
            order_kwargs('42', '42-73', '2021-12-24T17:18:28+00:00'),
            0,
            '1',
            id='in progress; order a bit after planned end; segment; linked',
        ),
        # Not linked - far too after the 'planned_end_at' to "magnet" to the
        # shift
        pytest.param(
            '2021-12-24T18:05:40+00:00',
            '2021-12-24 10:55:00+03',
            order_kwargs('42', '42-73', '2021-12-24T17:51:03+00:00'),
            0,
            None,
            id=(
                'in progress; order far too after planned end; segment; '
                'not linked'
            ),
        ),
        # Linked to the shift '2'
        pytest.param(
            '2021-12-24T08:54:30+00:00',
            '2021-12-24 11:54:00+03',
            order_kwargs('42', '42-73', '2021-12-24T08:53:30+00:00'),
            0,
            '2',
            id='finished; order at the end; point; linked',
        ),
        # Linked to the shift '2'. '09:10:30+00' does not really belong to
        # a working interval - neither for '1', nor for '2'. But it still links
        # to shift '2', because of "magneting" -
        # <time-passed-after-end> < 'max_time_until_previous_shift'
        pytest.param(
            '2021-12-24T09:13:30+00:00',
            '2021-12-24 12:12:00+03',
            order_kwargs('42', '42-73', '2021-12-24T09:10:30+00:00'),
            0,
            '2',
            id='finished; order a bit after actual end; segment; linked',
        ),
        # Not linked
        pytest.param(
            '2021-12-24T06:13:30+00:00',
            '2021-12-24 09:11:00+03',
            order_kwargs('42', '42-73', '2021-12-24T06:10:30+00:00'),
            0,
            None,
            id='None; before start of any shift; segment; not linked',
        ),
    ],
)
async def test_shift_order_linking(
        stq,
        stq_runner,
        pgsql,
        pulse_time_pg,
        testpoint,
        taxi_config,
        mocked_time,
        current_time,
        stq_order_kwargs,
        reschedule_count,
        linked_shift_id,
):
    mocked_time.set(dateutil.parser.isoparse(current_time))

    @testpoint('shift_already_linked')
    def shift_already_linked(data):
        pass

    @testpoint('order_not_linked')
    def order_not_linked(data):
        pass

    pg_cursor = pgsql['eats_logistics_performer_payouts'].dict_cursor()

    order_id = stq_order_kwargs['order_id']
    is_linked = 1 if linked_shift_id is not None else 0

    upsert_pulse(pg_cursor, PULSE_PERFORMER, pulse_time_pg)
    upsert_pulse(pg_cursor, PULSE_SHIFT, pulse_time_pg)

    subjects_before_test = get_all_ids(pg_cursor)
    await stq_runner.eats_logistics_performer_payouts_link_orders.call(
        task_id='dummy_task',
        kwargs=stq_order_kwargs,
        reschedule_counter=reschedule_count,
    )
    subjects_after_test = get_all_ids(pg_cursor)
    assert subjects_before_test == subjects_after_test

    assert linked_shift_id == get_linked_shift_id(pg_cursor, order_id)

    assert shift_already_linked.times_called == 0
    assert order_not_linked.times_called == (1 - is_linked)

    # duplicated event with another task_id
    await stq_runner.eats_logistics_performer_payouts_link_orders.call(
        task_id='dummy_task2', kwargs=stq_order_kwargs,
    )

    subjects_after_reschedule_test = get_all_ids(pg_cursor)
    assert subjects_before_test == subjects_after_reschedule_test

    assert shift_already_linked.times_called == is_linked


# Check, that once linked order cannot be re-linked to another courier's shift.
@pytest.mark.pgsql(DB_NAME, files=DB_FILES)
@pytest.mark.config(
    EATS_LOGISTICS_PERFORMER_PAYOUTS_SHIFT_ORDER_LINKING_SETTINGS_V2=(  # noqa: E501
        CFG_LINKING_SETTINGS
    ),
    EATS_LOGISTICS_PERFORMER_PAYOUTS_FETCH_SETTINGS_V2=CFG_FETCH_SETTINGS,
)
async def test_shift_order_linking_no_relinking(
        stq, stq_runner, pgsql, testpoint, taxi_config, mocked_time,
):
    mocked_time.set(dateutil.parser.isoparse('2021-12-24T17:10:46+00:00'))

    @testpoint('shift_already_linked')
    def shift_already_linked(data):
        pass

    @testpoint('order_not_linked')
    def order_not_linked(data):
        pass

    pg_cursor = pgsql['eats_logistics_performer_payouts'].dict_cursor()

    order_id = '42-73'

    subjects_before_test = get_all_ids(pg_cursor)

    pulse_time_pg = '2021-12-24 20:09:46+03'
    upsert_pulse(pg_cursor, PULSE_PERFORMER, pulse_time_pg)
    upsert_pulse(pg_cursor, PULSE_SHIFT, pulse_time_pg)

    # Link the order to performer-42's shift - assert success
    kwargs_42 = order_kwargs('42', order_id, '2021-12-24T17:05:47+00:00')
    await stq_runner.eats_logistics_performer_payouts_link_orders.call(
        task_id='dummy_task', kwargs=kwargs_42,
    )

    subjects_after_test = get_all_ids(pg_cursor)
    assert subjects_before_test == subjects_after_test

    assert shift_already_linked.times_called == 0
    assert order_not_linked.times_called == 0

    # Link the order to performer-73's shift - assert 'shift_already_linked'
    kwargs_73 = order_kwargs('73', order_id, '2021-12-24T17:10:47+00:00')

    await stq_runner.eats_logistics_performer_payouts_link_orders.call(
        task_id='dummy_task', kwargs=kwargs_73,
    )

    assert shift_already_linked.times_called == 1
    assert order_not_linked.times_called == 0

    subjects_after_test = get_all_ids(pg_cursor)
    assert subjects_before_test == subjects_after_test

    linked_shift_id = get_linked_shift_id(pg_cursor, order_id)
    assert linked_shift_id == '1'


# Check, that an empty order is created if a proper one is not present on DB
@pytest.mark.pgsql(DB_NAME, files=DB_FILES)
@pytest.mark.config(
    EATS_LOGISTICS_PERFORMER_PAYOUTS_SHIFT_ORDER_LINKING_SETTINGS_V2=(  # noqa: E501
        CFG_LINKING_SETTINGS
    ),
    EATS_LOGISTICS_PERFORMER_PAYOUTS_FETCH_SETTINGS_V2=CFG_FETCH_SETTINGS,
)
@pytest.mark.parametrize(
    'current_time,pulse_time_pg,stq_order_kwargs,reschedule_count,'
    + 'linked_shift_id',
    [
        # Happy path
        pytest.param(
            '2021-12-24T17:06:47+00:00',
            '2021-12-24 20:06:00+03',
            order_kwargs('42', '42-26', '2021-12-24T17:05:47+00:00'),
            0,
            '1',
            id='in progress; order within the shift; point; linked',
        ),
    ],
)
async def test_shift_order_linking_create_empty(
        stq,
        stq_runner,
        pgsql,
        pulse_time_pg,
        testpoint,
        taxi_config,
        mocked_time,
        current_time,
        stq_order_kwargs,
        reschedule_count,
        linked_shift_id,
):
    mocked_time.set(dateutil.parser.isoparse(current_time))

    @testpoint('shift_already_linked')
    def shift_already_linked(data):
        pass

    @testpoint('order_not_linked')
    def order_not_linked(data):
        pass

    pg_cursor = pgsql['eats_logistics_performer_payouts'].dict_cursor()

    order_id = stq_order_kwargs['order_id']
    is_linked = 1 if linked_shift_id is not None else 0

    upsert_pulse(pg_cursor, PULSE_PERFORMER, pulse_time_pg)
    upsert_pulse(pg_cursor, PULSE_SHIFT, pulse_time_pg)

    subjects_before_test = get_all_ids(pg_cursor)
    await stq_runner.eats_logistics_performer_payouts_link_orders.call(
        task_id='dummy_task',
        kwargs=stq_order_kwargs,
        reschedule_counter=reschedule_count,
    )
    subjects_after_test = get_all_ids(pg_cursor)
    assert order_id not in subjects_before_test
    assert order_id in subjects_after_test

    assert linked_shift_id == get_linked_shift_id(pg_cursor, order_id)

    assert shift_already_linked.times_called == 0
    assert order_not_linked.times_called == (1 - is_linked)
