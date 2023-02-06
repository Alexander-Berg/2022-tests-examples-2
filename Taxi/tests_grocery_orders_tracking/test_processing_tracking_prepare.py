import pytest

from tests_grocery_orders_tracking import configs
from tests_grocery_orders_tracking import consts
from tests_grocery_orders_tracking import headers
from tests_grocery_orders_tracking import models


@configs.CRM_INFORMERS_ENABLED
@configs.FEEDBACK_DISABLED
@pytest.mark.parametrize(
    'crm_informer_id', ['7aa39782-c40c-49ea-9083-03edbb5e89a4', None],
)
async def test_check_informers_priority(
        taxi_grocery_orders_tracking,
        pgsql,
        grocery_depots,
        grocery_crm,
        crm_informer_id,
):
    grocery_depots.add_depot(legacy_depot_id=models.DEFAULT_DEPOT_ID)

    info = {'crm_informer_id': crm_informer_id} if crm_informer_id else None
    informer = models.Informer(
        pgsql=pgsql,
        order_id=consts.DEFAULT_ORDER_ID,
        informer_type='custom',
        raw_compensation_info=info,
        insert_in_pg=False,
    )

    if crm_informer_id:
        grocery_crm.set_user_informer(crm_informer_id, None)
        crm_request = {
            'depot_id': models.DEFAULT_DEPOT_ID,
            'idempotency_key': consts.DEFAULT_ORDER_ID,
        }
        grocery_crm.check_informer_check_request(
            crm_request, headers.AUTH_CONTEXT['headers'],
        )

    response = await taxi_grocery_orders_tracking.post(
        '/processing/v1/tracking-prepare',
        json={
            'order_id': consts.DEFAULT_ORDER_ID,
            'depot_id': models.DEFAULT_DEPOT_ID,
            'auth_context': headers.AUTH_CONTEXT,
        },
    )
    assert response.status_code == 200
    assert grocery_crm.times_check_informer_called() == 1

    if crm_informer_id:
        informer.compare_with_db()
    else:
        informer.check_empty_db()


async def test_400(taxi_grocery_orders_tracking, grocery_depots):
    grocery_depots.add_depot(legacy_depot_id=models.DEFAULT_DEPOT_ID)
    response = await taxi_grocery_orders_tracking.post(
        '/processing/v1/tracking-prepare',
        json={
            'order_id': consts.DEFAULT_ORDER_ID,
            'depot_id': models.DEFAULT_DEPOT_ID,
            'auth_context': {},
        },
    )
    assert response.status_code == 400


@configs.FEEDBACK_ENABLED
async def test_feedback(taxi_grocery_orders_tracking, pgsql, mockserver):
    products = {
        'available_products_for_feedback': [
            {
                'product_id': 'some_id',
                'product_name': 'mom\'s spaghetti',
                'product_img_url': 'url',
            },
        ],
    }

    @mockserver.json_handler(
        '/grocery-products-feedback/available/products/feedback',
    )
    def _mock_products_feedback():
        return mockserver.make_response(json=products, status=200)

    informer = models.Informer(
        pgsql=pgsql,
        order_id=consts.DEFAULT_ORDER_ID,
        informer_type='products_feedback',
        raw_compensation_info=products,
        insert_in_pg=False,
    )

    response = await taxi_grocery_orders_tracking.post(
        '/processing/v1/tracking-prepare',
        json={
            'order_id': consts.DEFAULT_ORDER_ID,
            'depot_id': models.DEFAULT_DEPOT_ID,
            'auth_context': headers.AUTH_CONTEXT,
        },
    )
    assert response.status_code == 200

    informer.compare_with_db()


@configs.CRM_INFORMERS_ENABLED
@configs.FEEDBACK_ENABLED
@pytest.mark.parametrize(
    'crm_informer_id', ['7aa39782-c40c-49ea-9083-03edbb5e89a4', None],
)
@pytest.mark.parametrize(
    'products, status_code',
    [
        (
            {
                'available_products_for_feedback': [
                    {
                        'product_id': 'some_id',
                        'product_name': 'moms spaghetti',
                        'product_img_url': 'url',
                    },
                ],
            },
            200,
        ),
        ({'available_products_for_feedback': []}, 200),
        (None, 500),
    ],
)
async def test_check_informers_priority_with_feedback(
        taxi_grocery_orders_tracking,
        pgsql,
        grocery_depots,
        grocery_crm,
        crm_informer_id,
        products,
        status_code,
        mockserver,
):
    grocery_depots.add_depot(legacy_depot_id=models.DEFAULT_DEPOT_ID)

    info = {'crm_informer_id': crm_informer_id} if crm_informer_id else None
    informer = models.Informer(
        pgsql=pgsql,
        order_id=consts.DEFAULT_ORDER_ID,
        informer_type='custom',
        raw_compensation_info=info,
        insert_in_pg=False,
    )

    if crm_informer_id:
        grocery_crm.set_user_informer(crm_informer_id, None)
        crm_request = {
            'depot_id': models.DEFAULT_DEPOT_ID,
            'idempotency_key': consts.DEFAULT_ORDER_ID,
        }
        grocery_crm.check_informer_check_request(
            crm_request, headers.AUTH_CONTEXT['headers'],
        )

    @mockserver.json_handler(
        '/grocery-products-feedback/available/products/feedback',
    )
    def _mock_products_feedback():
        return mockserver.make_response(json=products, status=status_code)

    response = await taxi_grocery_orders_tracking.post(
        '/processing/v1/tracking-prepare',
        json={
            'order_id': consts.DEFAULT_ORDER_ID,
            'depot_id': models.DEFAULT_DEPOT_ID,
            'auth_context': headers.AUTH_CONTEXT,
        },
    )
    assert response.status_code == 200
    assert grocery_crm.times_check_informer_called() == 1

    if crm_informer_id:
        informer.compare_with_db()
    else:
        informer.check_no_informers_in_db()
