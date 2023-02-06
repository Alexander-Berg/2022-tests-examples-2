from hashlib import md5
import json

import pytest


TESTPARAMS = [
    (
        {'db': '1488', 'session': 'test_session'},
        {'order': '111', 'rating': '4', 'msg': 'Passenger smoked'},
        200,
    ),
    (
        {'db': '1488', 'session': 'test_session'},
        {'order': '111', 'rating': '10', 'msg': 'PERFECTO'},
        400,
    ),
    (
        {'db': '1488', 'session': 'test_session'},
        {'order': '111', 'rating': '4a', 'msg': 'Trympyrym'},
        400,
    ),
    (
        {'db': '1488', 'session': 'test_session'},
        {'order': '111', 'rating': 'abc', 'msg': 'Lorem ipsum'},
        400,
    ),
    (
        {'db': '1488', 'session': 'wrong_session'},
        {'order': '111', 'rating': '3', 'msg': 'Passenger cried'},
        401,
    ),
    (
        {'db': '1488', 'session': 'test_session'},
        {'rating': '2', 'msg': 'Passenger singed'},
        400,
    ),
    (
        {'db': '1488', 'session': 'test_session'},
        {'order': '', 'rating': '2', 'msg': 'Passenger smiled'},
        400,
    ),
    (
        {'db': '1488', 'session': 'test_session'},
        {'order': '7447', 'rating': '1', 'msg': 'Passenger died'},
        404,
    ),
]

IDS = [
    'normal',
    'too high rating',
    'sligtly wrong rating',
    'very wrong rating',
    'auth fail',
    'no order_id',
    'empty order_id',
    'wrong order_id',
]


@pytest.mark.sql(
    'taximeter',
    'INSERT INTO orders_0 (park_id, id, number, driver_id, '
    'date_create, date_booking) '
    'VALUES (\'{db}\', \'{order}\', {num}, \'{driver}\', now(), now())'.format(
        db='1488', order='111', num=1, driver='driverSS',
    ),
)
@pytest.mark.parametrize('auth,formdata,expected', TESTPARAMS, ids=IDS)
def test_driver_feeds_add(
        taxi_driver_protocol,
        auth,
        formdata,
        expected,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'test_session', 'driverSS')

    response = taxi_driver_protocol.post(
        'driver/feeds/add', params=auth, data=formdata,
    )
    assert response.status_code == expected


@pytest.mark.sql(
    'taximeter',
    'INSERT INTO orders_0 (park_id, id, number, driver_id, '
    'date_create, date_booking) '
    'VALUES (\'{db}\', \'{order}\', {num}, \'{driver}\', now(), now())'.format(
        db='1488', order='111', num=1, driver='driverBadCar',
    ),
)
def test_driver_feeds_add_alien_order(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session(
        '1488', 'test_session', 'driverSS',
    )  # not your order

    response = taxi_driver_protocol.post(
        'driver/feeds/add', params=TESTPARAMS[0][0], data=TESTPARAMS[0][1],
    )
    assert response.status_code == 401


@pytest.mark.sql(
    'taximeter',
    'INSERT INTO orders_0 (park_id, id, number, driver_id, '
    'date_create, date_booking) '
    'VALUES (\'{db}\', \'{order}\', {num}, \'{driver}\', now(), now())'.format(
        db='1488', order='111', num=1, driver='unknown_driver_pewpewpew',
    ),
)
def test_driver_feeds_no_driver(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session(
        '1488', 'test_session', 'unknown_driver_pewpewpew',
    )

    response = taxi_driver_protocol.post(
        'driver/feeds/add', params=TESTPARAMS[0][0], data=TESTPARAMS[0][1],
    )
    assert response.status_code == 500


@pytest.mark.sql(
    'taximeter',
    'INSERT INTO orders_0 (park_id, id, number, driver_id, '
    'date_create, date_booking) '
    'VALUES (\'{db}\', \'{order}\', {num}, \'{driver}\', now(), now())'.format(
        db='1488', order='111', num=1, driver='driver',
    ),
)
def test_driver_feeds_no_car(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session(
        '1488', 'test_session', 'driver',
    )  # 'driver' has no cars

    response = taxi_driver_protocol.post(
        'driver/feeds/add', params=TESTPARAMS[0][0], data=TESTPARAMS[0][1],
    )
    assert response.status_code == 500


@pytest.mark.sql(
    'taximeter',
    'INSERT INTO orders_0 (park_id, id, number, '
    'driver_id, date_create, date_booking) '
    'VALUES (\'{db}\', \'{order}\', {num}, \'{driver}\', now(), now())'.format(
        db='1488', order='111', num=1, driver='driverBadCar',
    ),
)
def test_driver_feeds_bad_callsign(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session(
        '1488', 'test_session', 'driverBadCar',
    )  # bad callsign

    response = taxi_driver_protocol.post(
        'driver/feeds/add', params=TESTPARAMS[0][0], data=TESTPARAMS[0][1],
    )
    assert response.status_code == 200


@pytest.mark.sql(
    'taximeter',
    'INSERT INTO orders_0 (park_id, id, number, driver_id, '
    'date_create, date_booking) '
    'VALUES (\'{db}\', \'{order}\', {num}, \'{driver}\', now(), now())'.format(
        db='1488', order='111', num=1, driver='driverSS',
    ),
)
def test_driver_feeds_add_database(
        taxi_driver_protocol,
        sql_databases,
        driver_authorizer_service,
        mock_stq_agent,
):
    driver_authorizer_service.set_session('1488', 'test_session', 'driverSS')

    response = taxi_driver_protocol.post(
        'driver/feeds/add',
        params={'db': '1488', 'session': 'test_session'},
        data={'order': '111', 'rating': '4', 'msg': 'Passenger laughed'},
    )

    assert response.status_code == 200

    cursor = sql_databases.taximeter.conn.cursor()
    # structure in e.g. backend-cpp/testsuite/configs/postgresql/taximeter.sql
    query = 'SELECT * FROM feedbacks_0'
    cursor.execute(query)
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert len(rows[0]) == 14
    assert rows[0][0] == '1488'
    assert rows[0][6] == 'Passenger laughed'
    assert rows[0][6] != 'Passenger danced'
    assert rows[0][7] == 4
    assert rows[0][11] == '111'
    assert rows[0][12] == 1

    assert not len(mock_stq_agent.get_tasks('driver_feedback_repeat'))


@pytest.mark.now('2020-03-23T01:02:03+0000')
@pytest.mark.sql(
    'taximeter',
    """INSERT INTO orders_0 (
    park_id, id, number, driver_id, date_create, date_booking)
    VALUES ('{db}', '{order}', {num}, '{driver}', now(), now())""".format(
        db='1488', order='111', num=794, driver='driverSS',
    ),
)
@pytest.mark.parametrize('is_stq', [True, False])
def test_stq_repeater(
        taxi_driver_protocol,
        config,
        sql_databases,
        redis_store,
        driver_authorizer_service,
        mock_stq_agent,
        is_stq,
):
    driver_authorizer_service.set_session('1488', 'test_session', 'driverSS')
    feedback_id = md5(('111' + 'driverSS' + '1').encode('utf-8')).hexdigest()

    # insert this to get duplicate error in the handler
    cursor = sql_databases.taximeter.conn.cursor()
    query = (
        """INSERT INTO feedbacks_0
    (park_id, driver_id, order_id, id, date, feed_type, status) VALUES
    ('1488', 'driverSS', '111', '{id}', now(), 1, 0);""".format(
            id=feedback_id,
        )
    )
    cursor.execute(query)

    config.set_values(dict(DRIVER_FEEDBACK_REPEAT_VIA_STQ=is_stq))
    response = taxi_driver_protocol.post(
        'driver/feeds/add',
        params={'db': '1488', 'session': 'test_session'},
        data={'order': '111', 'rating': '4', 'msg': 'He did a barrel roll'},
    )

    assert response.status_code == 200

    if is_stq:
        stq_tasks = mock_stq_agent.get_tasks('driver_feedback_repeat')

        assert len(stq_tasks) == 1
        stq_task = stq_tasks[0]
        assert stq_task.args == [
            '1488',
            'driverSS',
            '111',
            feedback_id,
            {'$date': '2020-03-23T04:02:03.000+0300'},
            4,
            0,
            1,
        ]

        stq_kwargs = stq_task.kwargs
        stq_kwargs.pop('log_extra', None)

        assert stq_kwargs == {
            'description': 'He did a barrel roll',
            'order_number': 794,
            'driver_name': 'Мироненко Андрей Алексеевич',
            'driver_signal': 'Ёжик',
        }
    else:
        serialized = redis_store.hget('Feedback:Errors', feedback_id)
        obj = json.loads(serialized)
        obj.pop('exception', None)
        assert obj == {
            'command': '1',
            'date': '2020-03-23T01:02:03+0000',
            'db': '1488',
            'feed': {
                'date': '2020-03-23T01:02:03+0000',
                'driver_id': 'driverSS',
                'driver_name': 'Мироненко Андрей Алексеевич',
                'driver_signal': 'Ёжик',
                'description': 'He did a barrel roll',
                'id': feedback_id,
                'order_id': '111',
                'order_number': 794,
                'score': 4,
                'status': '0',
                'type': '1',
            },
        }
