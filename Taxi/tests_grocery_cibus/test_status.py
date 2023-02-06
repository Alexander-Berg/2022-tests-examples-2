# pylint: disable=import-error, invalid-name
import copy
import decimal

from grocery_mocks.models import cart
from grocery_mocks.utils import helpers as mock_helpers
import pytest

from . import consts
from . import headers
from . import models
from .plugins import configs

APPLICATION_ID = 'app-id'

Decimal = decimal.Decimal


@pytest.fixture(name='setup_cart_mock')
def _setup_cart_mock(grocery_cart):
    def _do(
            checked_order_id=consts.ORDER_ID,
            retrieve_raw_error_code=None,
            delivery_cost=None,
            tips=None,
    ):
        grocery_cart.set_cart_data(cart_id=consts.CART_ID)
        grocery_cart.set_items(
            [
                cart.GroceryCartItem(
                    'item_id_1', price='100', quantity='3', vat='0',
                ),
                cart.GroceryCartItem(
                    'item_id_2', price='50', quantity='3', vat='15',
                ),
            ],
        )
        grocery_cart.set_payment_method(
            {'type': 'cibus', 'id': 'test_payment_method_id'},
        )
        if delivery_cost is not None:
            grocery_cart.set_order_conditions(delivery_cost=delivery_cost)
        grocery_cart.set_tips(tips)

        if checked_order_id is not None:
            grocery_cart.check_request({'order_id': checked_order_id})
        if retrieve_raw_error_code is not None:
            grocery_cart.default_cart.set_error_code(
                handler='cart_retrieve_raw', code=retrieve_raw_error_code,
            )

    return _do


@pytest.fixture(name='status_call')
async def _status_call(taxi_grocery_cibus, cibus):
    async def _do(
            status_code=200, replace_headers=None, order_id=consts.ORDER_ID,
    ):
        if replace_headers is None:
            replace_headers = {}

        request_headers = copy.deepcopy(headers.DEFAULT_HEADERS)
        request_headers.update(replace_headers)

        response = await taxi_grocery_cibus.post(
            '/internal/cibus/v1/status',
            json={'order_id': order_id},
            headers=request_headers,
        )

        assert response.status_code == status_code
        return response.json()

    return _do


async def test_response(setup_cart_mock, status_call, grocery_cibus_configs):
    setup_cart_mock()
    grocery_cibus_configs.set_cibus_application_id(APPLICATION_ID)
    response = await status_call()

    assert response == _get_status_default_response(response['created'])


async def test_db(
        setup_cart_mock, status_call, grocery_cibus_db, grocery_cibus_configs,
):
    order_id = 'another_order_id'
    setup_cart_mock(checked_order_id=order_id)
    grocery_cibus_configs.set_cibus_application_id(APPLICATION_ID)

    for _ in range(2):
        await status_call(order_id=order_id)
        payment = grocery_cibus_db.load_payment(invoice_id=order_id)

        assert payment.order_id == order_id
        assert payment.invoice_id == order_id
        assert payment.token == consts.DEFAULT_TOKEN
        assert payment.redirect_url == consts.REDIRECT_URL
        assert payment.status == models.PaymentStatus.init
        assert payment.yandex_uid == headers.YANDEX_UID
        assert payment.application_id == APPLICATION_ID
        assert payment.deal_price == 450
        assert payment.error_code is None
        assert payment.deal_id is None


async def test_cibus_request(setup_cart_mock, status_call, cibus):
    setup_cart_mock()

    cibus.get_token.check(
        synonym=headers.YANDEX_UID,
        ext_info=dict(
            deal_price='450',
            vat_free_price='300',
            reference_id=consts.ORDER_ID,
        ),
        headers={
            'Authorization': consts.CIBUS_API_SECRET,
            'Application-Id': consts.APPLICATION_ID,
        },
    )
    await status_call()

    assert cibus.get_token.times_called == 1


@pytest.mark.parametrize(
    'kwargs',
    [
        dict(expected='450'),
        dict(delivery_cost='50', expected='500'),
        dict(
            tips=dict(
                amount='50', amount_type='absolute', payment_flow='separate',
            ),
            expected='450',
        ),
        dict(
            tips=dict(
                amount='50', amount_type='absolute', payment_flow='with_order',
            ),
            expected='500',
        ),
    ],
)
async def test_deal_price(setup_cart_mock, status_call, cibus, kwargs):
    setup_cart_mock(
        delivery_cost=kwargs.get('delivery_cost'), tips=kwargs.get('tips'),
    )

    cibus.get_token.check(
        ext_info=mock_helpers.sub_dict(deal_price=kwargs.get('expected')),
    )
    await status_call()

    assert cibus.get_token.times_called == 1


async def test_repeat_request(
        setup_cart_mock, status_call, cibus, grocery_cibus_configs,
):
    setup_cart_mock()
    grocery_cibus_configs.set_cibus_application_id(APPLICATION_ID)
    for _ in range(2):
        response = await status_call()
        assert response == _get_status_default_response(response['created'])

    assert cibus.get_token.times_called == 1


async def test_cart_not_found(setup_cart_mock, status_call, cibus):
    setup_cart_mock(checked_order_id=None, retrieve_raw_error_code=404)

    response = await status_call(status_code=404, order_id='some-other-id')

    assert response['code'] == 'unknown_order_id'
    assert cibus.get_token.times_called == 0


async def test_bad_request_cart(setup_cart_mock, status_call, cibus):
    setup_cart_mock(checked_order_id=None, retrieve_raw_error_code=400)

    await status_call(status_code=500, order_id='some-other-id')

    assert cibus.get_token.times_called == 0


async def test_cibus_error(
        setup_cart_mock, status_call, cibus, grocery_cibus_configs,
):
    setup_cart_mock()

    error_code = -1
    error_message = 'error_message'

    cibus.get_token.mock_response(
        token='', oauth_signin_url='', code=error_code, msg=error_message,
    )

    response = await status_call(status_code=200)

    assert response['status'] == 'fail'

    assert cibus.get_token.times_called == 1


@pytest.mark.parametrize(
    'err_code, db_error_code',
    [
        (-1, 'unknown_error'),
        (13, 'request_error'),
        (14, 'request_error'),
        (15, 'request_error'),
        (118, 'cibus_db_fail'),
        (171, 'wrong_secret'),
        (172, 'wrong_secret'),
        (177, 'wrong_user_token'),
        (307, 'wrong_app_token'),
        (315, 'request_error'),
        (501, 'no_credentials'),
        (10034, 'already_exists'),
        (10035, 'request_error'),
    ],
)
async def test_cibus_error_db(
        setup_cart_mock,
        status_call,
        cibus,
        grocery_cibus_db,
        err_code,
        db_error_code,
):
    error_message = 'error_message'
    order_id = 'another_order_id'

    setup_cart_mock(checked_order_id=order_id)

    cibus.get_token.mock_response(
        token='', oauth_signin_url='', code=err_code, msg=error_message,
    )

    await status_call(order_id=order_id)

    payment = grocery_cibus_db.load_payment(invoice_id=order_id)
    assert payment.error_code == db_error_code
    assert payment.error_desc == error_message
    assert payment.order_id == order_id

    assert cibus.get_token.times_called == 1


async def test_not_authorized(setup_cart_mock, status_call, cibus):
    setup_cart_mock()
    response = await status_call(
        replace_headers={headers.X_YANDEX_UID: None}, status_code=400,
    )

    assert response['code'] == 'no_yandex_uid'
    assert response['message'] == 'No yandex_uid in request'
    assert cibus.get_token.times_called == 0


def _get_status_default_response(created):
    return {
        'token': consts.DEFAULT_TOKEN,
        'redirect_url': consts.REDIRECT_URL,
        'finish_url': configs.CIBUS_FINISH_URL,
        'application_id': APPLICATION_ID,
        'status': 'init',
        'created': created,
    }
