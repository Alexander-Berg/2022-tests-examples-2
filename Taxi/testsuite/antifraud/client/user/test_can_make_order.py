import pytest


def _check(
        taxi_antifraud,
        can_make_order,
        json=None,
        status_code=200,
        user_phone_id=None,
        user_source_id=None,
        order_id=None,
        initial_payment_type='card',
        application='android',
):
    if user_phone_id is None:
        user_phone_id = '5714f45e98956f06baaae3d4'
    if order_id is None:
        order_id = '100500'

    if json is None:
        json = {
            'order_id': order_id,
            'user_id': '100',
            'user_phone_id': user_phone_id,
            'user_source_id': user_source_id,
            'initial_payment_type': initial_payment_type,
            'application': application,
        }
    response = taxi_antifraud.post('client/user/can_make_order', json=json)
    assert status_code == response.status_code
    if status_code == 200:
        data = response.json()
        assert data == {'can_make_order': can_make_order}


@pytest.mark.config(
    AFS_ANTIGAMBLING_CONFIG={
        'default': {'orders': 4, 'time': 60},
        'corp': {'orders': 0, 'time': 80},
        'corpweb': {'orders': 0, 'time': 60},
    },
)
@pytest.mark.now('2018-10-01T09:00:00+0000')
def test_check_can_make_order_order_proc_no_fraud(taxi_antifraud):
    _check(
        taxi_antifraud,
        True,
        user_phone_id='571ad47bb10260a10841535f',
        order_id='d7072aed6f234fbe817d84354630ab95',
    )


@pytest.mark.config(
    AFS_ANTIGAMBLING_CONFIG={
        'default': {'orders': 0, 'time': 60},
        'corp': {'orders': 4, 'time': 60},
        'corpweb': {'orders': 0, 'time': 60},
    },
)
@pytest.mark.now('2018-10-01T09:00:00+0000')
def test_check_can_make_order_order_proc_no_fraud_corp(taxi_antifraud):
    _check(
        taxi_antifraud,
        True,
        user_phone_id='571ad47bb10260a10841535f',
        order_id='d7072aed6f234fbe817d84354630ab95',
        initial_payment_type='corp',
    )


@pytest.mark.config(
    AFS_ANTIGAMBLING_CONFIG={
        'default': {'orders': 0, 'time': 60},
        'corp': {'orders': 0, 'time': 60},
        'corpweb': {'orders': 4, 'time': 60},
    },
)
@pytest.mark.now('2018-10-01T09:00:00+0000')
def test_check_can_make_order_order_proc_no_fraud_webcorp(taxi_antifraud):
    _check(
        taxi_antifraud,
        True,
        user_phone_id='571ad47bb10260a10841535f',
        order_id='d7072aed6f234fbe817d84354630ab95',
        initial_payment_type='corp',
        application='corpweb',
    )


@pytest.mark.config(
    AFS_ANTIGAMBLING_CONFIG={
        'default': {'orders': 3, 'time': 60},
        'corp': {'orders': 800, 'time': 80},
        'corpweb': {'orders': 900, 'time': 60},
    },
)
@pytest.mark.now('2018-10-01T09:00:00+0000')
def test_check_can_make_order_order_proc_fraud(taxi_antifraud):
    _check(
        taxi_antifraud,
        False,
        user_phone_id='571ad47bb10260a10841535f',
        order_id='d7072aed6f234fbe817d84354630ab95',
    )


@pytest.mark.config(
    AFS_ANTIGAMBLING_CONFIG={
        'default': {'orders': 3, 'time': 60},
        'corp': {'orders': 800, 'time': 80},
        'corpweb': {'orders': 900, 'time': 60},
    },
    AFS_USER_SOURCES_WHITE_LIST=['cargo'],
)
@pytest.mark.now('2018-10-01T09:00:00+0000')
def test_check_can_make_order_user_sources_white_list(taxi_antifraud):
    _check(
        taxi_antifraud,
        True,
        user_phone_id='571ad47bb10260a10841535f',
        order_id='d7072aed6f234fbe817d84354630ab95',
        user_source_id='cargo',
    )


@pytest.mark.config(
    AFS_ANTIGAMBLING_CONFIG={
        'default': {'orders': 800, 'time': 60},
        'corp': {'orders': 3, 'time': 80},
        'corpweb': {'orders': 900, 'time': 60},
    },
)
@pytest.mark.now('2018-10-01T09:00:00+0000')
def test_check_can_make_order_order_proc_fraud_corp(taxi_antifraud):
    _check(
        taxi_antifraud,
        False,
        user_phone_id='571ad47bb10260a10841535f',
        order_id='d7072aed6f234fbe817d84354630ab95',
        initial_payment_type='corp',
    )


@pytest.mark.config(
    AFS_ANTIGAMBLING_CONFIG={
        'default': {'orders': 800, 'time': 60},
        'corp': {'orders': 800, 'time': 80},
        'corpweb': {'orders': 3, 'time': 60},
    },
)
@pytest.mark.now('2018-10-01T09:00:00+0000')
def test_check_can_make_order_order_proc_fraud_corpweb(taxi_antifraud):
    _check(
        taxi_antifraud,
        False,
        user_phone_id='571ad47bb10260a10841535f',
        order_id='d7072aed6f234fbe817d84354630ab95',
        initial_payment_type='corp',
        application='corpweb',
    )
