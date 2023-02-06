import copy
import uuid

import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys


IDEMPOTENCY_TOKEN = 'idempotency-token'

BASIC_HEADERS = common.TAXI_HEADERS.copy()
BASIC_HEADERS['X-Idempotency-Token'] = IDEMPOTENCY_TOKEN


async def test_unauthorized_access(taxi_grocery_cart, cart):
    basic_headers = BASIC_HEADERS.copy()
    basic_headers['X-YaTaxi-Session'] = ''

    await cart.init(['test_item'])

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'delivery_type': 'eats_dispatch',
        },
        headers=basic_headers,
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'random_cart_id, checked_out', [(True, False), (False, True)],
)
async def test_not_found(taxi_grocery_cart, cart, random_cart_id, checked_out):
    await cart.init(['test_item'])
    if checked_out:
        await cart.checkout()

    if not random_cart_id:
        cart_id = cart.cart_id
    else:
        cart_id = str(uuid.uuid4())

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'delivery_type': 'eats_dispatch',
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 404


async def test_conflict(taxi_grocery_cart, cart):
    await cart.init(['test_item_1'])
    await cart.modify(['test_item_2'])

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'delivery_type': 'eats_dispatch',
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 409


async def test_retry(taxi_grocery_cart, cart):
    await cart.init(['test_item'])

    for _ in range(2):
        response = await taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/set-delivery-type',
            json={
                'cart_id': cart.cart_id,
                'cart_version': 1,
                'position': keys.DEFAULT_POSITION,
                'delivery_type': 'eats_dispatch',
            },
            headers=BASIC_HEADERS,
        )
        assert response.status_code == 200


@pytest.mark.parametrize('delivery_type', ['eats_dispatch', 'pickup'])
async def test_db(taxi_grocery_cart, cart, delivery_type):
    await cart.init(['test_item'])

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'delivery_type': delivery_type,
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200

    cart_doc = cart.fetch_db()
    assert cart_doc.delivery_type == delivery_type
    assert cart_doc.cart_version == 2
    assert cart_doc.idempotency_token == IDEMPOTENCY_TOKEN


@pytest.mark.experiments3(
    name='lavka_default_delivery_type',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Always enabled',
            'predicate': {'type': 'true'},
            'value': {'delivery_type': 'eats_dispatch'},
        },
    ],
    is_config=True,
)
@pytest.mark.experiments3(filename='exp_del_type.json')
@pytest.mark.parametrize('delivery_type', ['eats_dispatch', 'rover', 'pickup'])
async def test_response_delivery_type(taxi_grocery_cart, cart, delivery_type):
    await cart.init(['test_item'])

    location = keys.DEFAULT_DEPOT_LOCATION

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': {'location': location},
            'delivery_type': delivery_type,
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    if delivery_type == 'pickup':
        assert (
            response.json()['checkout_unavailable_reason']
            == 'delivery-type-not-allowed'
        )
        assert response.json()['delivery_type'] == 'eats_dispatch'
    else:
        assert response.json()['delivery_type'] == delivery_type


@pytest.mark.experiments3(filename='exp_del_type.json')
@pytest.mark.parametrize(
    'location',
    [
        pytest.param([12, 22], id='no rover'),
        pytest.param([123.456, 45], id='forced rover, in response'),
        pytest.param([10, 20], id='rover'),
    ],
)
@pytest.mark.parametrize(
    'zones_enabled',
    [
        pytest.param(False, id='from experiment'),
        pytest.param(True, id='From depot zone'),
    ],
)
async def test_non_rover_delivery_type(
        taxi_grocery_cart, cart, location, zones_enabled,
):
    """
    Rover enabled, but force_rover overrides it and uses eats_dispatch
    """

    experiments.get_rover_zones_exp(zones_enabled)

    await taxi_grocery_cart.invalidate_caches()

    await cart.init(['test_item'])

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': {'location': location},
            'delivery_type': 'rover',
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    if location != [12, 22]:
        assert response.json()['delivery_type'] == 'rover'
    else:
        assert response.json()['delivery_type'] == 'eats_dispatch'


@pytest.mark.experiments3(filename='exp_del_type.json')
@pytest.mark.parametrize('location', [pytest.param([10, 20], id='rover')])
@pytest.mark.parametrize(
    'zones_enabled',
    [
        pytest.param(False, id='from experiment'),
        pytest.param(True, id='From depot zone'),
    ],
)
async def test_no_rover_18_plus(
        taxi_grocery_cart, cart, location, zones_enabled,
):
    """
    Rover disabled
    """

    experiments.get_rover_zones_exp(zones_enabled)

    await taxi_grocery_cart.invalidate_caches()

    await cart.init(['test_item'], legal_restrictions=['RU_18+'])

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': {'location': location},
            'delivery_type': 'rover',
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['delivery_type'] == 'eats_dispatch'


@pytest.mark.parametrize(
    'with_markdown, allowed_pickup, available_delivery_types',
    [
        pytest.param(
            True, False, [], id='markdown_item_in_cart_and_not_allowed_pickup',
        ),
        pytest.param(
            False,
            False,
            ['eats_dispatch'],
            id='no_markdown_item_in_cart_and_not_allowed_pickup',
        ),
        pytest.param(
            True,
            True,
            ['pickup'],
            id='markdown_item_in_cart_and_allowed_pickup',
        ),
        pytest.param(
            False,
            True,
            ['eats_dispatch', 'pickup'],
            id='no_markdown_item_in_cart_and_allowed_pickup',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp_del_type.json')
async def test_available_delivery_types(
        taxi_grocery_cart,
        cart,
        with_markdown,
        allowed_pickup,
        available_delivery_types,
):
    cart_items = ['test_item_1']
    if with_markdown:
        cart_items.append('test_item_2:st-md')
    await cart.init(
        cart_items,
        # TODO: LAVKABACKEND-1959 - remove from here
        delivery_type='pickup',
        headers={**BASIC_HEADERS, 'X-Yandex-Uid': '8484'},
        # TODO: LAVKABACKEND-1959 - remove to here
    )

    basic_headers = BASIC_HEADERS.copy()
    if allowed_pickup:
        basic_headers['X-Yandex-Uid'] = '8484'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'delivery_type': 'eats_dispatch',
        },
        headers=basic_headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    assert (
        response_json['available_delivery_types'].sort()
        == available_delivery_types.sort()
    )


@pytest.mark.parametrize(
    'delivery_type',
    [
        pytest.param(
            'eats_dispatch', id='eats_dispatch_as_selected_delivery_type',
        ),
        pytest.param('pickup', id='pickup_as_selected_delivery_type'),
    ],
)
@pytest.mark.parametrize(
    'with_markdown, allowed_pickup',
    [
        pytest.param(
            False, False, id='no_markdown_item_in_cart_and_not_allowed_pickup',
        ),
        pytest.param(
            True, True, id='markdown_item_in_cart_and_allowed_pickup',
        ),
        pytest.param(
            False, True, id='no_markdown_item_in_cart_and_allowed_pickup',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp_del_type.json')
async def test_checkout_unavailable_reason(
        taxi_grocery_cart, cart, delivery_type, with_markdown, allowed_pickup,
):
    cart_items = ['test_item_1']
    if with_markdown:
        cart_items.append('test_item_2:st-md')
    await cart.init(
        cart_items,
        # TODO: LAVKABACKEND-1959 - remove from here
        delivery_type='pickup',
        headers={**BASIC_HEADERS, 'X-Yandex-Uid': '8484'},
        # TODO: LAVKABACKEND-1959 - remove to here
    )

    basic_headers = BASIC_HEADERS.copy()
    if allowed_pickup:
        basic_headers['X-Yandex-Uid'] = '8484'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'delivery_type': delivery_type,
        },
        headers=basic_headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    if delivery_type not in response_json['available_delivery_types']:
        assert (
            response_json['checkout_unavailable_reason']
            == 'delivery-type-not-allowed'
        )
    else:
        assert (
            response_json.get('checkout_unavailable_reason', '')
            != 'delivery-type-not-allowed'
        )


# TODO: LAVKABACKEND-1959 - remove from here
@pytest.mark.experiments3(filename='exp_del_type.json')
# TODO: LAVKABACKEND-1959 - remove to here
async def test_correct_markdown_items_limits(taxi_grocery_cart, cart):
    markdown_item = 'test_item_2:st-md'

    await cart.init(
        ['test_item_1', markdown_item],
        # TODO: LAVKABACKEND-1959 - remove from here
        delivery_type='pickup',
        headers={**BASIC_HEADERS, 'X-Yandex-Uid': '8484'},
        # TODO: LAVKABACKEND-1959 - remove to here
    )

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'delivery_type': 'eats_dispatch',
        },
        headers=BASIC_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()

    assert (
        response_json['checkout_unavailable_reason'] == 'quantity-over-limit'
    )
    assert len(response_json['diff_data']['products']) == 1
    diff_product = response_json['diff_data']['products'][0]
    assert diff_product['product_id'] == markdown_item
    assert diff_product['quantity']['actual_limit'] == '0'


@pytest.mark.parametrize('locale', ['en', 'ru', 'he'])
@pytest.mark.pgsql('grocery_cart', files=['localized_product.sql'])
async def test_localized_product_response(
        taxi_grocery_cart, locale, load_json, overlord_catalog,
):
    localized = load_json('expected_product_localization.json')

    overlord_catalog.add_product(product_id='localized_product', price='345')

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': '11111111-2222-aaaa-bbbb-cccdddeee005',
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'delivery_type': 'eats_dispatch',
        },
        headers={
            **BASIC_HEADERS,
            'X-Request-Language': locale,
            'X-YaTaxi-User': 'eats_user_id=12345',
        },
    )
    assert response.status_code == 200

    item = response.json()['items'][0]
    assert item['title'] == localized[locale]['title']
    assert item['subtitle'] == localized[locale]['subtitle']


async def test_coupons_additional_data(
        taxi_grocery_cart, cart, grocery_coupons, grocery_p13n,
):
    await cart.init(['test_item'])

    assert grocery_p13n.discount_modifiers_times_called == 1
    grocery_coupons.check_check_request(**keys.CHECK_REQUEST_ADDITIONAL_DATA)
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'delivery_type': 'eats_dispatch',
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers={**BASIC_HEADERS, 'User-Agent': keys.DEFAULT_USER_AGENT},
    )
    assert response.status_code == 200

    assert grocery_p13n.discount_modifiers_times_called == 2


@pytest.mark.parametrize('has_personal_phone_id', [True, False])
async def test_no_phone_id(
        taxi_grocery_cart,
        cart,
        grocery_coupons,
        grocery_p13n,
        user_api,
        has_personal_phone_id,
):
    await cart.init(['test_item'])

    headers = copy.deepcopy(BASIC_HEADERS)
    if has_personal_phone_id:
        headers['X-YaTaxi-User'] = 'personal_phone_id=personal-phone-id'

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/set-delivery-type',
        json={
            'cart_id': cart.cart_id,
            'cart_version': 1,
            'position': keys.DEFAULT_POSITION,
            'delivery_type': 'eats_dispatch',
            'additional_data': keys.DEFAULT_ADDITIONAL_DATA,
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert user_api.times_called == (1 if has_personal_phone_id else 0)
