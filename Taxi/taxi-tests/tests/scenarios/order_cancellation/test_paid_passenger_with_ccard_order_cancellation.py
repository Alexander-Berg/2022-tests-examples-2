# pylint: disable=invalid-name

import pytest

from taxi_tests import utils

WAITING_TIME = 100
CANCELLATION_ERROR_MSG = 'Cancellation has not been paid in time'


def _add_paid_cancel_experiment(exp):
    exp.add_experiment(
        name='paid_cancel',
        consumers=[{'name': 'protocol/taxiontheway'}],
        clauses=[
            {
                'title': 'default',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    )


def _wait_when_cancellation_will_be_paid(passenger, timeout):
    for _ in utils.wait_for(timeout, CANCELLATION_ERROR_MSG):
        response = passenger.taxiontheway()
        if response.get('cancel_rules', {}).get('state', '') == 'paid':
            break


@pytest.mark.skip(reason='TAXIBACKEND-41364')
def test_paid_passenger_with_ccard_order_cancellation(
        exp, any_passenger_with_ccard_and_waited_driver,
):
    """
    Проверяем, что пользователь с картой, вызвавший и дождавшийся подъезда
    машины должен оплатить отмену заказа.
    """

    # 1. Получаем любого пользователя со способом оплаты карта и с заказом
    # в статусе платного ожидания.
    passenger = any_passenger_with_ccard_and_waited_driver
    _add_paid_cancel_experiment(exp)
    _wait_when_cancellation_will_be_paid(passenger, timeout=WAITING_TIME)

    # 2. Пользователь отменяет заказ.
    passenger.taxiontheway(cancel='user')

    # 3. Проверяем. что у пользователя списываются деньги со счета
    passenger.wait_for_basket_status('cleared')
    cost_of_cancel = passenger.get_card_payments('cleared')
    assert cost_of_cancel > 0
