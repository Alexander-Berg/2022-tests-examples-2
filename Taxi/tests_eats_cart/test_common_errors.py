import copy

import pytest

from . import utils

EATER_ID = 'eater2'
MENU_ITEM_ID = 232323
PLACE_SLUG = 'place123'
PLACE_ID = '22'


@pytest.fixture(name='handle')
def set_up_handle(taxi_eats_cart, local_services, db_insert):
    class Context:
        def __init__(self) -> None:
            self.item_properties = utils.ITEM_PROPERTIES
            self.params = local_services.request_params

        def request(self, method):
            return getattr(self, method)()

        def post_item(self):
            body = dict(item_id=MENU_ITEM_ID, **self.item_properties)

            return taxi_eats_cart.post(
                'api/v1/cart',
                params=self.params,
                headers=utils.get_auth_headers(EATER_ID),
                json=body,
            )

        def put_item(self):
            cart_item_price = 59

            cart_id = db_insert.cart(
                EATER_ID,
                place_slug=PLACE_SLUG,
                place_id=PLACE_ID,
                promo_subtotal=cart_item_price,
                total=cart_item_price,
            )
            db_insert.eater_cart(EATER_ID, cart_id)
            cart_item_id = db_insert.cart_item(
                cart_id,
                MENU_ITEM_ID,
                price=cart_item_price,
                promo_price=None,
                quantity=1,
            )

            return taxi_eats_cart.put(
                f'/api/v1/cart/{cart_item_id}',
                params=self.params,
                headers=utils.get_auth_headers(EATER_ID),
                json=self.item_properties,
            )

        def sync_cart(self):
            old_item_id = 111

            old_cart_id = db_insert.cart(EATER_ID)
            db_insert.eater_cart(EATER_ID, old_cart_id)
            db_insert.cart_item(
                old_cart_id,
                old_item_id,
                price=1000,
                promo_price=None,
                quantity=10,
            )

            body = {
                'items': [dict(item_id=MENU_ITEM_ID, **self.item_properties)],
            }

            return taxi_eats_cart.post(
                '/api/v1/cart/sync',
                params=self.params,
                headers=utils.get_auth_headers(EATER_ID),
                json=body,
            )

        def add_bulk_cart(self):
            old_item_id = 111

            cart_id = db_insert.cart(EATER_ID)
            db_insert.eater_cart(EATER_ID, cart_id)
            db_insert.cart_item(
                cart_id,
                old_item_id,
                price=1000,
                promo_price=None,
                quantity=10,
            )

            body = {
                'items': [dict(item_id=MENU_ITEM_ID, **self.item_properties)],
            }

            return taxi_eats_cart.post(
                '/api/v1/cart/add_bulk',
                params=self.params,
                headers=utils.get_auth_headers(EATER_ID),
                json=body,
            )

        def bulk_update_cart(self):
            cart_item_price = 59
            cart_id = db_insert.cart(
                EATER_ID,
                place_slug=PLACE_SLUG,
                place_id=PLACE_ID,
                promo_subtotal=cart_item_price,
                total=cart_item_price,
            )
            db_insert.eater_cart(EATER_ID, cart_id)
            for_update = db_insert.cart_item(
                cart_id,
                MENU_ITEM_ID,
                price=cart_item_price,
                promo_price=None,
                quantity=1,
            )

            body = {
                'items': [dict(item_id=for_update, **self.item_properties)],
            }

            return taxi_eats_cart.post(
                '/api/v1/cart/update_bulk',
                params=self.params,
                headers=utils.get_auth_headers(EATER_ID),
                json=body,
            )

        def get_cart(self):
            return taxi_eats_cart.get(
                'api/v1/cart',
                params=self.params,
                headers=utils.get_auth_headers(EATER_ID),
            )

    return Context()


@pytest.mark.parametrize(
    'method', ['post_item', 'sync_cart', 'bulk_update_cart', 'add_bulk_cart'],
)
@pytest.mark.parametrize(
    'is_core_fine',
    [
        pytest.param(False, id='eats_core_fault'),
        pytest.param(True, id='eats_core_bad_request'),
    ],
)
async def test_post_non_exisiting_item(
        handle, local_services, load_json, is_core_fine, method,
):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    if is_core_fine:
        local_services.core_items_status = 400
        local_services.core_items_response = {
            'error': 'place_menu_items_not_found',
            'message': str(MENU_ITEM_ID),
        }
    else:
        resp = load_json('eats_core_menu_items.json')
        resp['place_menu_items'][0]['id'] = MENU_ITEM_ID + 1
        local_services.core_items_response = resp

    response = await handle.request(method)

    assert response.status_code == 400
    assert response.json() == {
        'code': 5,
        'domain': 'UserData',
        'err': 'Неверный формат',
        'errors': {'item_id': ['menu item 232323  не существует']},
    }
    assert local_services.mock_eats_core_menu.times_called == 1


@pytest.mark.parametrize(
    'method',
    [
        'post_item',
        'sync_cart',
        'put_item',
        'bulk_update_cart',
        'add_bulk_cart',
    ],
)
async def test_place_not_available(handle, local_services, load_json, method):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')

    local_services.catalog_place_status = 404
    local_services.catalog_place_response = {
        'code': '404',
        'message': 'Not Found',
    }

    response = await handle.request(method)

    assert response.status_code == 400
    assert response.json() == {
        'code': 55,
        'domain': 'UserData',
        'err': 'Недоступный ресторан',
    }

    assert local_services.mock_eats_core_menu.times_called == 1
    assert local_services.mock_eats_catalog.times_called == 1


@pytest.mark.parametrize(
    'method',
    [
        'post_item',
        'sync_cart',
        'put_item',
        'bulk_update_cart',
        'add_bulk_cart',
    ],
)
async def test_ambiguous_place(handle, local_services, load_json, method):
    local_services.set_place_slug(PLACE_SLUG)
    local_services.core_items_status = 400
    local_services.core_items_response = {
        'error': 'different_places_forbidden',
        'message': '',
    }

    response = await handle.request(method)

    assert response.status_code == 400
    assert response.json() == {
        'code': 5,
        'domain': 'UserData',
        'err': 'Неверный формат',
        'errors': {'item_id': ['Элементы должны принадлежать к одному месту']},
    }

    assert local_services.mock_eats_core_menu.times_called == 1


FAULTY_ID = (1 << 31) - 1
OVERFLOWED = 3


def corrupt_item_options_group(properties, group_index=0):
    properties['item_options'][group_index]['group_id'] = FAULTY_ID


def corrupt_group_options(properties, group_index=0, option_index=0):
    properties['item_options'][group_index]['group_options'][
        option_index
    ] = FAULTY_ID
    properties['item_options'][group_index]['modifiers'][option_index][
        'option_id'
    ] = FAULTY_ID


def corrupt_modifier_id(properties, group_index=0, mod_index=0):
    properties['item_options'][group_index]['modifiers'][mod_index][
        'option_id'
    ] = FAULTY_ID


def violate_min_max_selected(properties, group_index=0):
    options = properties['item_options'][group_index]['group_options']
    start = options[-1]
    options.extend(start - i for i in range(1, OVERFLOWED - len(options) + 1))
    properties['item_options'][group_index]['modifiers'] = [
        {'option_id': id, 'quantity': 1} for id in options
    ]


def violate_multiplier(properties, group_index=0, mod_index=0):
    properties['item_options'][group_index]['modifiers'][mod_index][
        'quantity'
    ] = OVERFLOWED


def duplicate_modifier(properties, group_index=0):
    modifiers = properties['item_options'][group_index]['modifiers']
    modifiers[1:] = [copy.deepcopy(modifiers[0])]


@pytest.mark.parametrize(
    'method',
    [
        'post_item',
        'sync_cart',
        'put_item',
        'bulk_update_cart',
        'add_bulk_cart',
    ],
)
@pytest.mark.parametrize(
    'corrupt_fn,errors',
    [
        (
            corrupt_item_options_group,
            {
                'group_id': [
                    'Группа опций 2147483647 не найдена '
                    'в списке групп элемента 232323',
                ],
            },
        ),
        (
            corrupt_group_options,
            {
                'item_options': [
                    'Опция 2147483647 не найдена в группе 10372250',
                ],
            },
        ),
        (
            corrupt_modifier_id,
            {
                'item_options': [
                    'В модификаторе количества указана '
                    'несуществующая опция 2147483647',
                ],
            },
        ),
        (
            violate_min_max_selected,
            {
                'group_id': [
                    'Выбранное количество опций группы 10372250 '
                    'должно быть в диапазоне от 1 до 2',
                ],
                'item_options': [
                    'Опция 1679268436 не найдена в группе 10372250',
                ],
            },
        ),
        (
            violate_multiplier,
            {
                'item_options': [
                    'Модификатор количества для опции 1679268432 '
                    'должен быть больше нуля и меньше либо равен 2',
                ],
                'group_id': [
                    'Выбранное количество опций группы 10372250 '
                    'должно быть в диапазоне от 1 до 2',
                ],
            },
        ),
        (
            duplicate_modifier,
            {
                'item_options': [
                    'Неуникальный модификатор количества для опции 1679268432',
                ],
            },
        ),
    ],
)
async def test_faulty_options(
        handle, local_services, load_json, method, corrupt_fn, errors,
):
    local_services.set_place_slug('place123')
    local_services.core_items_request = [str(MENU_ITEM_ID)]
    local_services.core_items_response = load_json('eats_core_menu_items.json')
    local_services.catalog_place_response = load_json(
        'eats_catalog_internal_place.json',
    )

    properties = copy.deepcopy(utils.ITEM_PROPERTIES)
    corrupt_fn(properties)
    handle.item_properties = properties

    expected_json = {'code': 5, 'domain': 'UserData', 'err': 'Неверный формат'}
    expected_json['errors'] = errors

    response = await handle.request(method)

    assert response.status_code == 400
    assert response.json() == expected_json

    assert local_services.mock_eats_core_menu.times_called == 1


@pytest.mark.parametrize(
    'method',
    [
        'post_item',
        'sync_cart',
        'put_item',
        'bulk_update_cart',
        'add_bulk_cart',
    ],
)
@pytest.mark.parametrize('coordinate', ['latitude', 'longitude'])
async def test_inconsistent_coordinates(handle, method, coordinate):
    del handle.params[coordinate]

    response = await handle.request(method)

    expected_json = {'code': 5, 'domain': 'UserData', 'err': 'Неверный формат'}
    expected_json['errors'] = {coordinate: []}

    assert response.status_code == 400
    assert response.json() == expected_json
