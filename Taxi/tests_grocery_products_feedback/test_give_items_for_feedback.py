import pytest

from tests_grocery_products_feedback import models

YANDEX_UID = 'some_uid'
PRODUCT_ID = 'some_product_id'
ORDER_ID = '7881317eb10d4ecda902fe21587f0df3-grocery'
CREATED_AT = '2021-11-22T15:33:00+03:00'


def _get_order_raw(calculation, status):
    return {
        'order_id': ORDER_ID,
        'created_at': CREATED_AT,
        'status': status,
        'calculation': calculation,
        'contact': {},
        'destinations': [],
    }


@pytest.mark.parametrize('decision, product_count', [(0, 1), (1, 2), (1, 0)])
async def test_basic(
        taxi_grocery_products_feedback,
        testpoint,
        grocery_order_log,
        pgsql,
        decision,
        product_count,
):
    feedback = models.ProductFeedback(
        pgsql=pgsql, yandex_uid=YANDEX_UID, product_id='some_id_1', score=5,
    )
    feedback.update_db()

    feedback2 = models.ProductFeedback(
        pgsql=pgsql, yandex_uid=YANDEX_UID, product_id='some_id_2', score=5,
    )
    if product_count == 0:
        feedback2.update_db()

    feedback3 = models.ProductFeedback(
        pgsql=pgsql, yandex_uid=YANDEX_UID, product_id='some_id_3', score=5,
    )
    if product_count == 0:
        feedback3.update_db()

    calculations = {
        'items': [
            {'name': 'milk', 'product_id': 'some_id_1', 'cost': '100'},
            {'name': 'chocolate', 'product_id': 'some_id_2', 'cost': '200'},
            {'name': 'chocolate_2', 'product_id': 'some_id_3', 'cost': '300'},
        ],
        'final_cost': '600',
        'currency_code': 'RUB',
    }

    orders_raw = {'orders': []}
    orders_raw['orders'].append(_get_order_raw(calculations, 'closed'))

    grocery_order_log.set_order_raw(orders_raw)

    @testpoint('inject_decision')
    def _inject_decision(data):
        return {'decision': decision}

    response = await taxi_grocery_products_feedback.post(
        '/available/products/feedback',
        json={'yandex_uid': YANDEX_UID, 'bound_yandex_uids': []},
    )

    assert response.status_code == 200

    response = response.json()

    assert len(response['available_products_for_feedback']) == product_count


@pytest.mark.parametrize('error_code', [404, 500])
async def test_order_log_error(
        taxi_grocery_products_feedback, grocery_order_log, error_code,
):
    grocery_order_log.set_retrieve_raw_error(error_code)

    response = await taxi_grocery_products_feedback.post(
        '/available/products/feedback',
        json={'yandex_uid': YANDEX_UID, 'bound_yandex_uids': []},
    )

    if error_code == 404:
        assert response.status_code == 200
        assert len(response.json()['available_products_for_feedback']) == 0
    else:
        assert response.status_code == error_code


@pytest.mark.parametrize(
    'first_order_status, second_order_status',
    [
        ('closed', 'closed'),
        ('closed', 'assembling'),
        ('canceled', 'closed'),
        ('canceled', 'delivering'),
    ],
)
async def test_closed_orders(
        taxi_grocery_products_feedback,
        grocery_order_log,
        first_order_status,
        second_order_status,
):
    product_name_first = 'milk'
    calculations_first = {
        'items': [
            {
                'name': product_name_first,
                'product_id': 'some_id_1',
                'cost': '100',
            },
        ],
        'final_cost': '100',
        'currency_code': 'RUB',
    }

    product_name_second = 'chocolate'
    calculations_second = {
        'items': [
            {
                'name': product_name_second,
                'product_id': 'some_id_2',
                'cost': '200',
            },
        ],
        'final_cost': '200',
        'currency_code': 'RUB',
    }

    orders_raw = {'orders': []}
    orders_raw['orders'].append(
        _get_order_raw(calculations_first, first_order_status),
    )
    orders_raw['orders'].append(
        _get_order_raw(calculations_second, second_order_status),
    )

    grocery_order_log.set_order_raw(orders_raw)

    response = await taxi_grocery_products_feedback.post(
        '/available/products/feedback',
        json={'yandex_uid': YANDEX_UID, 'bound_yandex_uids': []},
    )

    assert response.status_code == 200

    response = response.json()

    if first_order_status == 'closed':
        assert (
            response['available_products_for_feedback'][0]['product_name']
            == product_name_first
        )
    elif second_order_status == 'closed':
        assert (
            response['available_products_for_feedback'][0]['product_name']
            == product_name_second
        )
    else:
        assert len(response['available_products_for_feedback']) == 0
