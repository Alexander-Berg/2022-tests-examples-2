import datetime

import pytest


APPLICATION_MAP_BRAND = {'__default__': 'yataxi', 'uber_iphone': 'yauber'}

DB_NAME = 'user-statistics'

FIRST_ORDER_CREATED = '2019-12-11T09:00:00Z'


def brand_from_application(application):
    if not application:
        return None
    return APPLICATION_MAP_BRAND.get(
        application, APPLICATION_MAP_BRAND['__default__'],
    )


def parse_datetime(source):
    source_str = source['$date'] if isinstance(source, dict) else source
    return datetime.datetime.strptime(source_str, '%Y-%m-%dT%H:%M:%S%z')


def get_order_data(
        order_id,
        order_created=FIRST_ORDER_CREATED,
        application='android',
        tariff_class='econom',
        payment_type='card',
):
    order_data = {
        'order_id': order_id,
        'order_created': {'$date': order_created},
        'phone_id': {'$oid': '000000000000000000000000'},
        'yandex_uid': '0123456789',
    }
    if application:
        order_data['application'] = application
    if tariff_class:
        order_data['tariff_class'] = tariff_class
    if payment_type:
        order_data['payment_type'] = payment_type

    return order_data


def get_db_order_data(order_data):
    """ Convert kwargs order data to database order data.

    {
        'phone_id': {'$oid': '123'},
        'yandex_uid': '789',
    }
    ->
    {
        'phone_id': '123',
        'yandex_uid': '789',
    }
    """
    result = {}
    for kwarg, value in order_data.items():
        if kwarg == 'phone_id':
            result['phone_id'] = value['$oid']
        else:
            result[kwarg] = value
    return result


class DbHelper:
    def __init__(self, db):
        self.db = db[DB_NAME]

    def _query_columns(self, cursor):
        return [desc[0] for desc in cursor.description]

    def _query_result(self, query):
        db_cursor = self.db.cursor()
        db_cursor.execute(query)

        columns = self._query_columns(db_cursor)
        rows = list(db_cursor)

        return [dict(zip(columns, row)) for row in rows]

    def get_counter(self, **kwargs):
        condition = ' AND '.join(
            [
                f'{column} = \'{value}\'' if value else f'{column} IS NULL'
                for column, value in kwargs.items()
            ],
        )
        query = f"""
            SELECT
                id::text,
                counter_value,
                counted_from,
                counted_to
            FROM userstats.orders_counters
            WHERE {condition}
        """
        rows = self._query_result(query)
        return rows[0] if rows else None

    def get_order_counter(self, identity_type, order):
        return self.get_counter(
            identity_type=identity_type,
            identity_value=order[identity_type],
            brand=brand_from_application(order.get('application')),
            tariff_class=order.get('tariff_class'),
            payment_type=order.get('payment_type'),
        )

    def get_recent_orders(self, counter_id):
        query = f"""
            SELECT
                id::text,
                order_counter_id,
                order_created_at
            FROM userstats.recent_orders
            WHERE
                order_counter_id = \'{counter_id}\'::uuid
        """
        return self._query_result(query)


def check_counters(db, order_data, expected_counter):
    for identity_type in ('phone_id', 'yandex_uid'):
        counter = db.get_order_counter(identity_type, order_data)
        counter.pop('id')
        assert counter == expected_counter


@pytest.mark.config(APPLICATION_MAP_BRAND=APPLICATION_MAP_BRAND)
@pytest.mark.parametrize('application', ['android', 'uber_iphone'])
@pytest.mark.parametrize('tariff_class', ['econom', 'business'])
@pytest.mark.parametrize('payment_type', ['card', 'cash'])
async def test_new_counter(
        stq_runner, pgsql, application, tariff_class, payment_type,
):
    order_data = get_order_data(
        'order1',
        application=application,
        tariff_class=tariff_class,
        payment_type=payment_type,
    )
    db_order_data = get_db_order_data(order_data)

    await stq_runner.userstats_order_complete.call(
        task_id='new_counter', kwargs=order_data,
    )

    order_created = parse_datetime(order_data['order_created'])
    expected_counter = {
        'counter_value': 1,
        'counted_from': order_created,
        'counted_to': order_created,
    }
    check_counters(DbHelper(pgsql), db_order_data, expected_counter)


@pytest.mark.config(APPLICATION_MAP_BRAND=APPLICATION_MAP_BRAND)
@pytest.mark.pgsql(DB_NAME, files=['fill_data.sql'])
@pytest.mark.parametrize(
    'order, order_created, increment_expected',
    [
        ('order1', FIRST_ORDER_CREATED, False),
        ('order2', '2019-12-11T14:00:00+0300', True),
    ],
)
async def test_existing_counter(
        stq_runner, pgsql, order, order_created, increment_expected,
):
    order_data = get_order_data(order, order_created=order_created)
    db_order_data = get_db_order_data(order_data)

    expected_counter = {
        'counter_value': 1,
        'counted_from': parse_datetime(FIRST_ORDER_CREATED),
        'counted_to': parse_datetime(FIRST_ORDER_CREATED),
    }
    check_counters(DbHelper(pgsql), db_order_data, expected_counter)

    await stq_runner.userstats_order_complete.call(
        task_id='new_counter', kwargs=order_data,
    )

    expected_updated_counter = {
        'counter_value': 2 if increment_expected else 1,
        'counted_from': parse_datetime(FIRST_ORDER_CREATED),
        'counted_to': parse_datetime(order_created),
    }
    check_counters(DbHelper(pgsql), db_order_data, expected_updated_counter)


@pytest.mark.parametrize(
    'processing_expected',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                USER_STATISTICS_MIGRATION={'migration_mode_enabled': False},
            ),
            id='migration mode off',
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                USER_STATISTICS_MIGRATION={'migration_mode_enabled': True},
            ),
            id='missing migrate till',
        ),
        pytest.param(
            True,
            marks=pytest.mark.config(
                USER_STATISTICS_MIGRATION={
                    'migration_mode_enabled': True,
                    'migrate_till': '2020-06-01T11:00:00+0300',
                },
            ),
            id='after migrate till',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                USER_STATISTICS_MIGRATION={
                    'migration_mode_enabled': True,
                    'migrate_till': '2020-06-01T13:00:00+0300',
                },
            ),
            id='before migrate till',
        ),
    ],
)
async def test_migration_mode(stq_runner, testpoint, processing_expected):
    @testpoint('event_processing')
    def event_processed(data):
        pass

    order_data = get_order_data('order1', order_created='2020-06-01T09:00:00Z')
    await stq_runner.userstats_order_complete.call(
        task_id='new_counter', kwargs=order_data,
    )

    assert event_processed.times_called == (1 if processing_expected else 0)


@pytest.mark.config(
    APPLICATION_MAP_BRAND=APPLICATION_MAP_BRAND,
    USER_STATISTICS_RECENT_ORDERS={
        'save_settings': {'identity_types': ['yandex_uid'], 'keep_days': 30},
        'cleanup_settings': {'period_sec': 60},
    },
)
@pytest.mark.parametrize(
    'init_db',
    [
        pytest.param(False, id='new_counter'),
        pytest.param(
            True,
            marks=pytest.mark.pgsql(DB_NAME, files=['fill_data.sql']),
            id='existing_counter',
        ),
    ],
)
async def test_save_recent_orders(stq_runner, pgsql, init_db):
    order_id = 'order1'

    order_data = get_order_data(order_id)
    db_order_data = get_db_order_data(order_data)

    await stq_runner.userstats_order_complete.call(
        task_id='recent_order', kwargs=order_data,
    )

    db = DbHelper(pgsql)
    for identity_type in ('phone_id', 'yandex_uid'):
        counter = db.get_order_counter(identity_type, db_order_data)
        recent_orders = db.get_recent_orders(counter['id'])

        if identity_type == 'yandex_uid':
            assert recent_orders
            assert recent_orders[0]['order_created_at'] == parse_datetime(
                FIRST_ORDER_CREATED,
            )
        else:
            assert not recent_orders
