# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=redefined-outer-name
import datetime

import bson
import psycopg2.extras
import pytest

from manual_dispatch_plugins import *  # noqa: F403 F401

MINUS_INFINITE_DATE = datetime.datetime(
    1970, 1, 1, 0, 0, 0, 0, tzinfo=datetime.timezone.utc,
)


def _override_fields(original, override):
    for key, value in override.items():
        if key in original:
            original[key] = value
        else:
            raise ValueError(f'table has no field {key}')


def _filter_fields(dct, projection, excluded):
    assert (
        projection is None or excluded is None
    ), 'either choose a projection or exclude fields'
    excluded = excluded or []
    if projection is not None:
        projection = set(projection)
        dct = {k: v for k, v in dct.items() if k in projection}
    elif excluded is not None:
        for field in excluded:
            del dct[field]
    return dct


@pytest.fixture
def get_order(pgsql):
    cursor = pgsql['manual-dispatch'].conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    def wrapped(order_id, projection=None, excluded=None):
        cursor.execute(
            """SELECT *
            FROM manual_dispatch.order
            WHERE order_id='{}'""".format(
                order_id,
            ),
        )
        rows = cursor.fetchall()
        if not rows:
            return None
        return _filter_fields(dict(rows[0]), projection, excluded)

    return wrapped


@pytest.fixture
def get_rules(pgsql):
    cursor = pgsql['manual-dispatch'].conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    def wrapped(client_id, projection=None, excluded=None):
        cursor.execute(
            """
        SELECT
            rule.id,
            name,
            (array_agg(client_id))[1] AS client_id,
            lookup_ttl,
            switch_interval,
            is_enabled,
            new_list_hit_flow,
            array_agg(tariff) AS tariffs,
            main_contact,
            backup_contact
        FROM manual_dispatch.rule
        LEFT JOIN manual_dispatch.rule_coverage
        ON rule.id = rule_coverage.rule_id
        WHERE client_id ='{0}'
        GROUP BY rule.id;
        """.format(
                client_id,
            ),
        )
        rows = cursor.fetchall()
        if not rows:
            return None
        for row in rows:
            row['tariffs'] = sorted(row['tariffs'])
        return [
            _filter_fields(dict(row), projection, excluded) for row in rows
        ]

    return wrapped


@pytest.fixture
def get_client(pgsql):
    cursor = pgsql['manual-dispatch'].conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    def wrapped(client_id, projection=None, excluded=None):
        cursor.execute(
            """
        SELECT client_id, name, is_enabled FROM manual_dispatch.corp_client
        WHERE client_id = '{}';
        """.format(
                client_id,
            ),
        )
        rows = cursor.fetchall()
        if not rows:
            return None
        return _filter_fields(dict(rows[0]), projection, excluded)

    return wrapped


@pytest.fixture
def create_order(pgsql):
    cursor = pgsql['manual-dispatch'].dict_cursor()

    def create_audits(order_id, order_status):
        if order_status == 'pending':
            statuses = ['pending']
        elif order_status == 'finished':
            statuses = ['pending', 'assigned', 'finished']
        else:
            statuses = ['pending', order_status]
        for status in statuses:
            cursor.execute(
                """
                INSERT INTO manual_dispatch.order_audit
                    (order_id, status, reason)
                VALUES (%s, %s, 'testsuite')
                """,
                (order_id, status),
            )

    def wrapped(**override):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        order = {
            'order_id': 'order_id_1',
            'claim_id': 'claim_id_1',
            'corp_id': 'client_id_1',
            'tariff': 'courier',
            'status': 'pending',
            'search_params': None,
            'performer_id': 'performer_id_1',
            'created_ts': now,
            'manual_switch_interval': datetime.timedelta(seconds=10),
            'due_ts': now,
            'search_ts': now,
            'lookup_ttl': datetime.timedelta(seconds=10),
            'new_list_hit_flow': False,
            'lookup_version': 0,
            'lock_expiration_ts': MINUS_INFINITE_DATE,
            'owner_operator_id': None,
            'order_type': 'b2b',
            'tag': None,
            'address_shortname': None,
            'mirror_only_value': True,
            'country': None,
            'zone_id': None,
        }
        if override.get('search_params') is not None:
            override['search_params'] = psycopg2.extras.Json(
                override['search_params'],
            )
        _override_fields(order, override)
        cursor.execute(
            """INSERT INTO manual_dispatch.order
                   (order_id, claim_id, corp_id, tariff, status, search_params,
                   performer_id, created_ts, manual_switch_interval, due_ts,
                   search_ts, lookup_ttl, new_list_hit_flow,
                   lookup_version, lock_expiration_ts,
                   owner_operator_id, order_type, tag, address_shortname,
                   country, zone_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
                       %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                order['order_id'],
                order['claim_id'],
                order['corp_id'],
                order['tariff'],
                order['status'],
                order['search_params'],
                order['performer_id'],
                order['created_ts'],
                order['manual_switch_interval'],
                order['due_ts'],
                order['search_ts'],
                order['lookup_ttl'],
                order['new_list_hit_flow'],
                order['lookup_version'],
                order['lock_expiration_ts'],
                order['owner_operator_id'],
                order['order_type'],
                order['tag'],
                order['address_shortname'],
                order['country'],
                order['zone_id'],
            ),
        )
        create_audits(order['order_id'], order['status'])
        return order

    return wrapped


@pytest.fixture
def get_order_audit(pgsql):
    cursor = pgsql['manual-dispatch'].conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    def wrapped(order_id, projection=None, excluded=None):
        cursor.execute(
            """SELECT * FROM manual_dispatch.order_audit
            WHERE order_id='{}'""".format(
                order_id,
            ),
        )
        rows = cursor.fetchall()
        return [_filter_fields(dict(x), projection, excluded) for x in rows]

    return wrapped


@pytest.fixture
def assert_orders_eq():
    def convert_time_point(time_point):
        if time_point.date() == datetime.date(1970, 1, 1):
            # psycopg2 doesn't handle infinite dates (userver does)
            return MINUS_INFINITE_DATE
        return time_point.astimezone(datetime.timezone.utc).replace(
            microsecond=0,
        )

    def wrapped(order1, order2):
        for order in (order1, order2):
            for date_field in (
                    'created_ts',
                    'search_ts',
                    'due_ts',
                    'updated_ts',
                    'lock_expiration_ts',
            ):
                if date_field in order:
                    order[date_field] = convert_time_point(order[date_field])
        assert order1 == order2

    return wrapped


@pytest.fixture
def create_dispatch_attempt(pgsql):
    cursor = pgsql['manual-dispatch'].conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    def wrapped(**override):
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        dispatch_attempt = {
            'order_id': 'order_id_1',
            'operator_id': 'operator_id_1',
            'performer_id': 'dbid1_uuid1',
            'status': 'pending',
            'expiration_ts': now + datetime.timedelta(minutes=2),
            'created_ts': now,
            'updated_ts': now,
            'message': None,
        }
        _override_fields(dispatch_attempt, override)
        cursor.execute(
            'INSERT INTO manual_dispatch.dispatch_attempt '
            '(order_id, operator_id, performer_id, status, expiration_ts, '
            'message, created_ts, updated_ts) '
            'VALUES (%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id',
            (
                dispatch_attempt['order_id'],
                dispatch_attempt['operator_id'],
                dispatch_attempt['performer_id'],
                dispatch_attempt['status'],
                dispatch_attempt['expiration_ts'],
                dispatch_attempt['message'],
                dispatch_attempt['created_ts'],
                dispatch_attempt['updated_ts'],
            ),
        )
        dispatch_attempt['id'] = cursor.fetchone()['id']
        return dispatch_attempt

    return wrapped


@pytest.fixture
def get_dispatch_attempt(pgsql):
    cursor = pgsql['manual-dispatch'].conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    def wrapped(
            order_id=None, attempt_id=None, projection=None, excluded=None,
    ):
        assert (order_id is None) != (attempt_id is None)
        cursor.execute(
            """SELECT * FROM manual_dispatch.dispatch_attempt
            WHERE {field}=%s""".format(
                field='order_id' if order_id is not None else 'id',
            ),
            (order_id if order_id is not None else attempt_id,),
        )
        rows = cursor.fetchall()
        rows = [_filter_fields(dict(x), projection, excluded) for x in rows]
        if attempt_id is not None:
            return rows[0] if rows else None
        # order_id makes no guarantees about uniqueness without the status
        return rows

    return wrapped


@pytest.fixture
def headers():
    return {
        'X-Yandex-UID': 'yandex_uid_1',
        'Accept-Language': 'ru-RU, ru;q=0.9',
    }


@pytest.fixture
def create_corp_client(pgsql):
    cursor = pgsql['manual-dispatch'].conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    def wrapped(client_id, name, is_enabled):
        cursor.execute(
            """
        INSERT INTO manual_dispatch.corp_client (
            client_id,
            name,
            is_enabled
        ) VALUES (%s, %s, %s)
        """,
            (client_id, name, is_enabled),
        )

    return wrapped


@pytest.fixture(autouse=True)
def mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _mock_bulk_retrieve(request):
        return {
            'items': [
                {'id': x['id'], 'value': x['id'][:-3]}
                for x in request.json['items']
            ],
        }

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _mock_bulk_store(request):
        return {
            'items': [
                {'id': x['value'] + '_id', 'value': x['value']}
                for x in request.json['items']
            ],
        }


@pytest.fixture
def create_rule(pgsql):
    cursor = pgsql['manual-dispatch'].conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    def wrapped(
            rule_id,
            name,
            is_enabled,
            lookup_ttl,
            manual_switch_interval,
            main_contact,
            backup_contact,
    ):
        if main_contact is not None:
            main_contact = main_contact['name'], main_contact['phone_id']
        if backup_contact is not None:
            backup_contact = backup_contact['name'], backup_contact['phone_id']
        cursor.execute(
            """
            INSERT INTO manual_dispatch.rule (
                id,
                name,
                is_enabled,
                lookup_ttl,
                switch_interval,
                main_contact,
                backup_contact
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """,
            (
                rule_id,
                name,
                is_enabled,
                lookup_ttl,
                manual_switch_interval,
                main_contact,
                backup_contact,
            ),
        )

    return wrapped


@pytest.fixture
def create_rule_coverage(pgsql):
    cursor = pgsql['manual-dispatch'].conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    def wrapped(rule_id, client_id, tariff):
        cursor.execute(
            """
            INSERT INTO manual_dispatch.rule_coverage (
                rule_id, client_id, tariff
            )
            VALUES (%s, %s, %s)
            """,
            (rule_id, client_id, tariff),
        )

    return wrapped


@pytest.fixture(autouse=True)
def rule_rule_coverage(create_corp_client, create_rule, create_rule_coverage):
    create_corp_client('client_id_1', 'name_1', True)
    create_corp_client('client_id_2', 'name_2', False)
    create_corp_client('client_id_3', 'name_3', True)

    create_rule(
        rule_id='rule_id_1',
        name='name_1',
        is_enabled=True,
        lookup_ttl='1800s',
        manual_switch_interval='1800s',
        main_contact={'name': 'Foo Bar', 'phone_id': '+700012345678_id'},
        backup_contact=None,
    )
    create_rule(
        rule_id='rule_id_2',
        name='name_2',
        is_enabled=True,
        lookup_ttl='1800s',
        manual_switch_interval='1800s',
        main_contact={'name': 'Baz Buzz', 'phone_id': '+7123456789012_id'},
        backup_contact={'name': 'Spam Eggs', 'phone_id': '+7123456789012_id'},
    )
    create_rule(
        rule_id='rule_id_3',
        name='name_3',
        is_enabled=True,
        lookup_ttl='10s',
        manual_switch_interval='20s',
        main_contact=None,
        backup_contact=None,
    )
    create_rule(
        rule_id='rule_id_4',
        name='name_4',
        is_enabled=True,
        lookup_ttl='1800s',
        manual_switch_interval='1800s',
        main_contact=None,
        backup_contact=None,
    )
    create_rule(
        rule_id='rule_id_5',
        name='name_5',
        is_enabled=False,
        lookup_ttl='1800s',
        manual_switch_interval='1800s',
        main_contact=None,
        backup_contact=None,
    )

    create_rule_coverage('rule_id_1', 'client_id_1', 'comfort')
    create_rule_coverage('rule_id_1', 'client_id_1', 'econom')
    create_rule_coverage('rule_id_2', 'client_id_1', 'courier')
    create_rule_coverage('rule_id_3', 'client_id_2', 'comfort')
    create_rule_coverage('rule_id_4', 'client_id_3', 'comfort')
    create_rule_coverage('rule_id_5', 'client_id_3', 'courier')


@pytest.fixture
def mock_set_order_fields(mockserver, load_json):
    context = {
        'expected_value': {'$set': {'manual_dispatch': {'mirror_only': True}}},
        'get_response': None,
    }

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/get-fields',
    )
    def get_order_fields(request):
        if context['get_response'] is None:
            return mockserver.make_response(
                status=200,
                content_type='application/bson',
                response=bson.BSON.encode(
                    load_json('order_fields_response.json'),
                ),
            )
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(context['get_response']),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/order-proc/set-fields',
    )
    def set_order_fields(request):
        request_body = bson.BSON.decode(request.get_data())
        assert request_body['update'] == context['expected_value']
        return mockserver.make_response(
            status=200,
            content_type='application/bson',
            response=bson.BSON.encode(load_json('order_fields_response.json')),
        )

    @mockserver.json_handler(
        '/order-core/internal/processing/v1/event/start-lookup',
    )
    def start_lookup(request):
        assert bson.BSON.decode(request.get_data()) == {
            'filters': {'status': 'pending'},
        }
        return mockserver.make_response('', status=200)

    context['handler'] = set_order_fields
    context['get_handler'] = get_order_fields
    context['lookup'] = start_lookup
    return context


@pytest.fixture
def get_delayed_updates(pgsql):

    cursor = pgsql['manual-dispatch'].conn.cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )

    def wrapped(projection=None, excluded=None):
        cursor.execute('SELECT * FROM manual_dispatch.delayed_status_updates')
        rows = cursor.fetchall()
        for row in rows:
            row['created_ts'] = row['created_ts'].astimezone(
                datetime.timezone.utc,
            )
        return [_filter_fields(dict(x), projection, excluded) for x in rows]

    return wrapped
