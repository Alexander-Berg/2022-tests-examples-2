# pylint: disable=import-error
from grocery_mocks.models import cart
# pylint: enable=import-error
import pytest

from . import experiments


ORDER_ID = 'order_id-grocery'
CART_ID = '28fe4a6e-c00d-45c1-a34e-6329c4a4e329'
ANOTHER_CART_ID = '28fe4a6e-c00d-45c1-a34e-6329c4a4e320'
COUNTRY_ISO3 = 'RUS'

RUS_TIPS_PROPOSALS = ['49', '99', '149']
RUS_TIPS_PROPOSALS_TEMPLATES = [
    '49 $SIGN$$CURRENCY$',
    '99 $SIGN$$CURRENCY$',
    '149 $SIGN$$CURRENCY$',
]
RUS_TIPS_CURRENCY_SIGN = '₽'

HEADERS_WITH_RUS_LOCALE = {
    'X-YaTaxi-Session': 'taxi:uuu',
    'X-Yandex-UID': '13579',
    'X-YaTaxi-User': f'eats_user_id={97531}',
    'X-Request-Language': 'ru',
}


def get_rus_response():
    return {
        'ask_for_tips': True,
        'proposals': [
            {
                'amount': '49',
                'amount_type': 'absolute',
                'amount_template': '49 $SIGN$$CURRENCY$',
            },
            {
                'amount': '99',
                'amount_type': 'absolute',
                'amount_template': '99 $SIGN$$CURRENCY$',
            },
            {
                'amount': '149',
                'amount_type': 'absolute',
                'amount_template': '149 $SIGN$$CURRENCY$',
            },
        ],
    }


@pytest.fixture(name='setup_mocks')
def _setup_mocks(grocery_orders_lib, grocery_cart):
    def _do(currency='RUB', country_iso3='RUS', checked_cart_id=CART_ID):
        mocked_order = grocery_orders_lib.add_order(
            order_id=ORDER_ID, cart_id=CART_ID,
        )
        mocked_order['country_iso3'] = country_iso3

        new_cart = grocery_cart.add_cart(cart_id=CART_ID)
        grocery_cart.check_request({'cart_id': checked_cart_id})
        new_cart.set_items(
            [cart.GroceryCartItem('item_id_1', currency=currency)],
        )
        new_cart.set_payment_method(
            {'type': 'card', 'id': 'test_payment_method_id'},
        )

    return _do


@experiments.TIPS_EXPERIMENT
@pytest.mark.parametrize(
    'request_json',
    [
        {'cart_id': CART_ID},
        {'order_id': ORDER_ID},
        {'country_iso3': COUNTRY_ISO3},
    ],
)
async def test_basic_requests(setup_mocks, taxi_grocery_api, request_json):
    setup_mocks()
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/tips',
        headers=HEADERS_WITH_RUS_LOCALE,
        json=request_json,
    )

    assert response.status_code == 200
    assert response.json() == get_rus_response()


async def test_unauthorized(setup_mocks, taxi_grocery_api):
    setup_mocks()
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/tips', json={'cart_id': CART_ID},
    )

    assert response.status_code == 401


async def test_orders_404_error(setup_mocks, taxi_grocery_api):
    setup_mocks()
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/tips',
        headers=HEADERS_WITH_RUS_LOCALE,
        json={'order_id': 'id'},
    )

    assert response.status_code == 404


@pytest.mark.parametrize('request_json', [{'cart_id': 'id'}, {'': ''}])
async def test_400_errors(setup_mocks, taxi_grocery_api, request_json):
    setup_mocks()
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/tips',
        headers=HEADERS_WITH_RUS_LOCALE,
        json=request_json,
    )

    assert response.status_code == 400


async def test_empty_experiments(setup_mocks, taxi_grocery_api):
    setup_mocks()
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/tips',
        headers=HEADERS_WITH_RUS_LOCALE,
        json={'cart_id': CART_ID},
    )

    assert response.status_code == 200
    body = response.json()

    assert body['ask_for_tips'] is False


@experiments.TIPS_EXPERIMENT
async def test_tristero_order_flow(setup_mocks, taxi_grocery_api):
    setup_mocks()
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/tips',
        headers=HEADERS_WITH_RUS_LOCALE,
        json={'cart_id': CART_ID, 'order_flow_version': 'tristero_flow_v1'},
    )

    assert response.status_code == 200
    body = response.json()

    assert body['ask_for_tips'] is False


@experiments.TIPS_EXPERIMENT
async def test_priority_of_country_iso_from_call(
        setup_mocks, taxi_grocery_api,
):
    setup_mocks(currency='RUB', country_iso3='RUS')
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/tips',
        headers=HEADERS_WITH_RUS_LOCALE,
        json={'cart_id': CART_ID, 'country_iso3': 'GBR'},
    )

    assert response.status_code == 200
    assert response.json()['ask_for_tips'] is False
