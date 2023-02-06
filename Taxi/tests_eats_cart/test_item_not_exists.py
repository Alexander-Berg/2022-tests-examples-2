import pytest

from tests_eats_cart import utils

MENU_ITEM_ID = 232323
NOT_EXISTS_ITEM = '111'


@pytest.mark.parametrize(
    'method,path,read_only',
    [
        pytest.param(
            'delete',
            '/api/v1/cart/disabled-items',
            False,
            id='del_v1_disabled_items',
        ),
        pytest.param('delete', '/api/v1/cart/1', False, id='del_v1_cart'),
        pytest.param(
            'delete',
            '/api/v1/cart/unavailable-items-by-time',
            False,
            id='del_v1_unavailable-items-by-time',
        ),
        pytest.param('put', '/api/v1/cart/2', False, id='put_v1_cart'),
        pytest.param('post', '/api/v1/cart', False, id='post_v1_cart'),
        pytest.param('get', '/api/v1/cart', True, id='get_v1_cart'),
    ],
)
async def test_not_all_items_exists(
        local_services,
        eats_cart_cursor,
        taxi_eats_cart,
        method,
        path,
        read_only,
):
    request_body = dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)
    if method == 'delete':
        request_body = {}
    elif method == 'get':
        request_body = None

    local_services.core_items_request = ['111', '232323', '2']
    status_code = (
        await getattr(taxi_eats_cart, method)(
            path,
            params=local_services.request_params,
            headers=utils.get_auth_headers(),
            json=request_body,
        )
    ).status_code

    assert status_code == 200

    eats_cart_cursor.execute(utils.SELECT_CART_ITEMS)
    items = eats_cart_cursor.fetchall()

    for item in items:
        if item['place_menu_item_id'] == NOT_EXISTS_ITEM:
            assert (
                item['deleted_at'] is None
            ) == read_only, f'item {item} expected deleted is {not read_only}'
        else:
            assert item['deleted_at'] is None, f'item {item} is deleted'


@pytest.mark.parametrize(
    'method,path,read_only',
    [
        pytest.param(
            'delete',
            '/api/v1/cart/disabled-items',
            False,
            id='del_v1_disabled_items',
        ),
        pytest.param('delete', '/api/v1/cart/1', False, id='del_v1_cart'),
        pytest.param(
            'delete',
            '/api/v1/cart/unavailable-items-by-time',
            False,
            id='del_v1_unavailable-items-by-time',
        ),
        pytest.param('put', '/api/v1/cart/2', False, id='put_v1_cart'),
        pytest.param('get', '/api/v1/cart', True, id='get_v1_cart'),
    ],
)
async def test_all_items_not_exists(
        local_services,
        mockserver,
        eats_cart_cursor,
        taxi_eats_cart,
        method,
        path,
        read_only,
):
    request_body = dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)
    if method == 'delete':
        request_body = {}
    elif method == 'get':
        request_body = None

    local_services.core_items_request = ['111', '232323', '2']

    @mockserver.json_handler(
        '/eats-core-place-menu/internal-api/v1/place/menu/get-items',
    )
    def _mock_eats_core_menu(request):
        return mockserver.make_response(
            json={
                'error': 'place_menu_items_not_found',
                'message': 'not found',
            },
            status=400,
        )

    status_code = (
        await getattr(taxi_eats_cart, method)(
            path,
            params=local_services.request_params,
            headers=utils.get_auth_headers(),
            json=request_body,
        )
    ).status_code

    assert status_code == 200 if read_only else 400

    eats_cart_cursor.execute(utils.SELECT_CART)
    carts = eats_cart_cursor.fetchall()

    cart = carts[0]

    assert (cart['deleted_at'] is None) == read_only


async def test_add_only_new_item_exists(
        local_services,
        mockserver,
        load_json,
        eats_cart_cursor,
        taxi_eats_cart,
):
    request_body = dict(item_id=MENU_ITEM_ID, **utils.ITEM_PROPERTIES)

    local_services.core_items_request = ['111', '232323', '2']
    core_items_response = load_json('eats_core_menu_items.json')

    core_items_response['place_menu_items'] = core_items_response[
        'place_menu_items'
    ][:1]

    @mockserver.json_handler(
        '/eats-core-place-menu/internal-api/v1/place/menu/get-items',
    )
    def _mock_eats_core_menu(request):
        if request.json['items'] == [str(MENU_ITEM_ID)]:
            return core_items_response
        return mockserver.make_response(
            json={
                'error': 'place_menu_items_not_found',
                'message': 'not found',
            },
            status=400,
        )

    resp = await taxi_eats_cart.post(
        '/api/v1/cart',
        params=local_services.request_params,
        headers=utils.get_auth_headers(),
        json=request_body,
    )

    assert resp.status_code == 200

    assert 'item_id' in resp.json()

    assert len(resp.json()['cart']['items']) == 2

    for item in resp.json()['cart']['items']:
        assert item['item_id'] == MENU_ITEM_ID

    eats_cart_cursor.execute(utils.SELECT_CART)
    carts = eats_cart_cursor.fetchall()

    cart = carts[0]

    assert cart['deleted_at'] is None
