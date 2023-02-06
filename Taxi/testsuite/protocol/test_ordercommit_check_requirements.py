import datetime

import pytest


@pytest.fixture
def surge(mockserver):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge(request):
        return {
            'zone_id': 'moscow',
            'classes': [
                {
                    'name': 'econom',
                    'value': 1.0,
                    'reason': 'pins_free',
                    'antisurge': False,
                    'value_raw': 1.0,
                    'value_smooth': 1.0,
                },
            ],
        }


@pytest.mark.parametrize(
    'tariff,due,ut,pr,agent,requirements,error',
    [
        ('econom', False, False, False, False, [], None),
        (
            'econom',
            False,
            False,
            False,
            False,
            ['req'],
            {'code': 'WRONG_REQUIREMENTS', 'wrong_requirements': ['req']},
        ),
        (
            'econom',
            False,
            False,
            False,
            False,
            ['creditcard'],
            {
                'code': 'PAYMENT_TYPE_CARD_UNSUPPORTED',
                'wrong_requirements': ['creditcard'],
            },
        ),
        (
            'econom',
            False,
            False,
            False,
            False,
            ['corp'],
            {
                'code': 'PAYMENT_TYPE_CORP_UNSUPPORTED',
                'wrong_requirements': ['corp'],
            },
        ),
        (
            'econom',
            False,
            True,
            False,
            False,
            [],
            {'code': 'TARIFF_IS_UNAVAILABLE'},
        ),
        (
            'econom',
            True,
            False,
            False,
            False,
            [],
            {'code': 'TARIFF_IS_UNAVAILABLE'},
        ),
        (
            'econom',
            False,
            False,
            True,
            False,
            [],
            {'code': 'PAYMENT_TYPE_UNACCEPTABLE'},
        ),
        (
            'econom',
            True,
            False,
            True,
            False,
            [],
            {'code': 'TARIFF_IS_RESTRICTED'},
        ),
        (
            'econom',
            True,
            False,
            True,
            True,
            [],
            {'code': 'PAYMENT_TYPE_UNACCEPTABLE'},
        ),
    ],
)
@pytest.mark.config(CRUTCH=True)
def test_check_requirements(
        taxi_protocol,
        db,
        tariff,
        due,
        ut,
        pr,
        agent,
        requirements,
        error,
        surge,
        mockserver,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    update_set = {
        'order.request.class': [tariff],
        'order.request.requirements': {x: True for x in requirements},
    }
    if due:
        update_set['order.request.due'] = datetime.datetime.utcnow()
    comment = ''
    if ut:
        comment += ',tariffunavailable-econom'
    if pr:
        comment += ',restrictpayment-yes'
    if agent:
        update_set['order.agent.agent_id'] = 'some_agent_id'
        update_set['order.agent.agent_user_type'] = 'individual'
    if comment:
        update_set['order.request.comment'] = comment
    db.order_proc.update({'_id': 'orderid'}, {'$set': update_set})
    request = {'id': 'user_id', 'orderid': 'orderid'}
    response = taxi_protocol.post('3.0/ordercommit', request)
    if error is None:
        assert response.status_code == 200, response.content
    else:
        assert response.status_code == 406, response.content
        assert response.json() == {'error': error}


@pytest.mark.config(HOURLY_RENTAL_ENABLED=True)
@pytest.mark.parametrize(
    'payment_type, requirements, config_values,'
    'expected_status_code, expected_code',
    [
        (
            'cash',
            {'hourly_rental': 1},
            {
                'hourly_rental': {
                    'allowed_by_default': True,
                    'non_default_payment_types': ['corp'],
                },
            },
            200,
            None,
        ),
        (
            'cash',
            {'hourly_rental': 1},
            {
                'hourly_rental': {
                    'allowed_by_default': True,
                    'non_default_payment_types': ['cash'],
                },
            },
            406,
            'PAYMENT_TYPE_CASH_UNSUPPORTED',
        ),
        (
            'corp',
            {'hourly_rental': 1},
            {
                'hourly_rental': {
                    'allowed_by_default': True,
                    'non_default_payment_types': ['corp'],
                },
            },
            406,
            'PAYMENT_TYPE_CORP_UNSUPPORTED',
        ),
    ],
)
def test_allowed_payment_types_for_requirements(
        taxi_protocol,
        db,
        payment_type,
        requirements,
        config_values,
        expected_status_code,
        expected_code,
        mockserver,
        config,
        surge,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    config.set_values(
        {'ALLOWED_PAYMENT_TYPES_FOR_REQUIREMENTS': config_values},
    )
    update_set = {
        'order.request.payment.type': payment_type,
        'order.request.requirements': requirements,
    }

    db.order_proc.update({'_id': 'orderid'}, {'$set': update_set})
    request = {'id': 'user_id', 'orderid': 'orderid'}
    response = taxi_protocol.post('3.0/ordercommit', request)
    assert response.status_code == expected_status_code
    if expected_status_code == 406:
        assert response.json()['error']['code'] == expected_code


@pytest.mark.parametrize(
    ('comment', 'door_to_door', 'expected_status_code'),
    [
        pytest.param('', True, 200),
        pytest.param(
            '',
            True,
            406,
            marks=pytest.mark.experiments3(
                filename='experiments3_door_to_door.json',
            ),
        ),
        pytest.param(
            '',
            False,
            200,
            marks=pytest.mark.experiments3(
                filename='experiments3_door_to_door.json',
            ),
        ),
        pytest.param(
            'comment',
            True,
            200,
            marks=pytest.mark.experiments3(
                filename='experiments3_door_to_door.json',
            ),
        ),
    ],
)
def test_door_to_door_comment(
        taxi_protocol,
        db,
        comment,
        door_to_door,
        expected_status_code,
        surge,
        pricing_data_preparer,
):
    pricing_data_preparer.set_locale('ru')

    update_set = {
        'order.request.comment': comment,
        'order.request.requirements': {'door_to_door': door_to_door},
    }
    db.order_proc.update({'_id': 'orderid'}, {'$set': update_set})

    request = {'id': 'user_id', 'orderid': 'orderid'}
    response = taxi_protocol.post('3.0/ordercommit', request)

    assert response.status_code == expected_status_code

    if expected_status_code == 406:
        expected_code = 'DOOR_TO_DOOR_COMMENT_NOT_FILLED'
        assert response.json()['error']['code'] == expected_code
