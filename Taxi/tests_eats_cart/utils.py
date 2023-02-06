# pylint: disable=too-many-lines
import copy
import dataclasses
import datetime
import math
import numbers
import re
import typing

import pytest


@dataclasses.dataclass
class CartEta:
    place_id: int = 1
    total_time: int = 15
    cooking_time: int = 5
    delivery_time: int = 10
    boundaries_min: int = 5
    boundaries_max: int = 15


def setup_available_features(features: typing.List[str]):
    return pytest.mark.experiments3(
        name='eats_cart_features',
        consumers=['eats_cart/user_only'],
        is_config=False,
        default_value={x: {'enabled': True} for x in features},
    )


def setup_available_checkers(checkers: typing.List[str]):
    return pytest.mark.experiments3(
        name='eda_cart_checkers',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        is_config=False,
        default_value={checker: {'enabled': True} for checker in checkers},
    )


def not_show_row_discount():
    return pytest.mark.experiments3(
        name='exclude_discounts_in_promo_items',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        is_config=True,
        default_value={'enabled': True},
    )


def get_items_from_erms(value):
    return pytest.mark.experiments3(
        name='eats_client_menu_use_erms',
        consumers=['eats_cart/user_only'],
        is_config=False,
        default_value={'enabled': value},
    )


def config_cart_items_limits(
        total_items_limit=100,
        different_items_limit=100,
        one_item_quantity_limit=100,
):
    return pytest.mark.config(
        EATS_CART_ITEMS_LIMITS={
            'total_items_limit': total_items_limit,
            'different_items_limit': different_items_limit,
            'one_item_quantity_limit': one_item_quantity_limit,
        },
    )


def config_cart_total_limits(shop='9000', restaurant='5000'):
    return pytest.mark.config(
        EATS_CART_TOTAL_LIMIT={
            '__default__': {
                '__default__': '300000',
                'shop': shop,
                'restaurant': restaurant,
            },
            'RU': {
                '__default__': '300000',
                'shop': shop,
                'restaurant': restaurant,
            },
            'KZ': {
                '__default__': '300000',
                'shop': '3000',
                'restaurant': '6000',
            },
            'BY': {
                '__default__': '300000',
                'shop': '10000',
                'restaurant': '3584',
            },
        },
    )


def exclude_discounts(
        excluded_discounts: typing.List[str],
        excluded_promotypes: typing.List[str],
):
    return pytest.mark.experiments3(
        name='eats_discounts_applicator_exclude_discounts',
        consumers=['eats-discounts-applicator/user'],
        is_config=True,
        default_value={
            'excluded_discounts': excluded_discounts,
            'excluded_promotypes': excluded_promotypes,
        },
    )


def show_discounts():
    return pytest.mark.experiments3(
        name='delivery_threshold',
        consumers=['eats_cart/service_fee'],
        is_config=False,
        default_value={'enabled': True},
    )


def eats_discounts_promo_types_info(value):
    return pytest.mark.experiments3(
        name='eats_discounts_promo_types_info',
        consumers=['eats-discounts-applicator/user'],
        is_config=True,
        default_value=value,
    )


def get_auth_headers(
        eater_id='21', phone_id='phone123', email_id='email456', yandex_uid='',
):
    return {
        'X-YaTaxi-Session': 'eats:in',
        'X-Eats-User': (
            f'user_id={eater_id},'
            f'personal_phone_id={phone_id},'
            f'personal_email_id={email_id}'
        ),
        'X-YaTaxi-Bound-UserIds': '',
        'X-YaTaxi-Bound-Sessions': '',
        'X-Yandex-UID': yandex_uid,
    }


def pg_result_to_repr(result_set):
    return [list(map(str, row)) for row in result_set]


def pg_result_by_key(result_set, keys):
    return [
        [str(result_set[i][key]) for key in keys]
        for i in range(len(result_set))
    ]


class Point:
    def __init__(self, lat=55.75, lon=37.62):
        self.lat = lat
        self.lon = lon


MOSCOW_POINT = Point()


def get_params(
        shipping_type='delivery',
        delivery_time='2021-04-04T11:00:00+03:00',
        point=None,
        spend_cashback=False,
):
    if not point:
        point = MOSCOW_POINT
    res = {
        'latitude': point.lat,
        'longitude': point.lon,
        'shippingType': shipping_type,
        'spendCashback': spend_cashback,
    }
    if delivery_time:
        res['deliveryTime'] = delivery_time
    return res


def get_body_params(
        shipping_type='delivery',
        delivery_time='2021-04-04T11:00:00+03:00',
        point=None,
):
    if not point:
        point = MOSCOW_POINT
    return {
        'latitude': point.lat,
        'longitude': point.lon,
        'shipping_type': shipping_type,
        'delivery_time': delivery_time,
    }


def to_datetime(string):
    return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S%z')


def get_empty_cart(load_json, delivery_time, now, shipping_type, tz_offset):
    empy_cart = load_json('empty_cart.json')
    utc_time = to_datetime(delivery_time if delivery_time else now)
    local_time = utc_time.astimezone(datetime.timezone(tz_offset))
    empy_cart['delivery_date_time'] = local_time.strftime('%d-%m-%Y %H:%M')
    empy_cart['delivery_date_time_iso'] = local_time.isoformat()
    empy_cart['shipping_type'] = shipping_type
    now_datetime = to_datetime(now)
    empy_cart['updated_at'] = now_datetime.astimezone(
        datetime.timezone(tz_offset),
    ).strftime('%Y-%m-%dT%H:%M:%S%z')
    return empy_cart


def service_fee_enabled():
    return pytest.mark.experiments3(
        name='cart_service_fee',
        consumers=['eats_cart/service_fee'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'title': 'Add service fee experiment',
                    'description': 'Description of the experiment',
                    'holding_amount': '1.05',
                    'confirm_text': 'Some_text',
                    'announcement': 'Message for another service',
                },
            },
        ],
    )


def dynamic_prices(
        default_percent: typing.Optional[int] = None,
        items_percents: dict = None,
):
    items = dict()
    if default_percent:
        calculate_method = 'by_place_percent'
        items = {'__default__': default_percent}
        if items_percents:
            items.update(items_percents)
    else:
        calculate_method = 'by_items_cache'
    return pytest.mark.experiments3(
        name='eats_dynamic_price_by_user',
        consumers=['eats_smart_prices/user'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'enabled': True,
                    'calculate_method': calculate_method,
                    'modification_percent': items,
                },
            },
        ],
    )


def service_fee_from_pricing(enabled=False, dry_run=True):
    return pytest.mark.experiments3(
        name='eats_cart_get_service_fee_from_pricing',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled, 'dry_run': dry_run},
            },
        ],
    )


def disable_surge_checkout_check(threshold: int):
    return pytest.mark.experiments3(
        name='eats_cart_disable_surge_checkout_check',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'threshold': threshold},
            },
        ],
    )


def erase_place_business_enabled():
    return pytest.mark.experiments3(
        name='eats_cart_sync_erase_place_business',
        consumers=['eats_cart/user_only'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    )


def delivery_discount_enabled():
    return pytest.mark.experiments3(
        name='delivery_discount',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    )


def use_new_disc_for_rest_exp():
    return pytest.mark.experiments3(
        name='eats_cart_use_new_discounts_for_restaurants',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': True},
            },
        ],
    )


def get_pg_records_as_dicts(sql, db):
    db.execute(sql)
    columns = [desc[0] for desc in db.description]
    records = list(db)
    return [dict(zip(columns, rec)) for rec in records]


def discounts_applicator_enabled(enabled):
    return pytest.mark.experiments3(
        name='use_discounts_applicator_in_eats_cart',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
    )


def setup_auto_items(items):
    return pytest.mark.experiments3(
        name='eats_cart_automatic_items',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        is_config=True,
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {**items},
            },
        ],
    )


def setup_auto_items_fee_type(fee_type):
    return pytest.mark.experiments3(
        name='eats_cart_auto_items_fee_type',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
        is_config=False,
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'type': fee_type},
            },
        ],
    )


def additional_payment_text(
        delivery_fee_subtitle: str = 'message.delivery_fee_subtitle',
        delivery_fee_main_text: str = 'message.delivery_fee_main_text',
):
    return pytest.mark.experiments3(
        name='additional_payments_msg',
        consumers=['eats_cart/service_fee'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {
                    'service_fee': {
                        'title': {
                            'text': 'message.service_fee_title',
                            'color': [
                                {'theme': 'light', 'value': '#000000'},
                                {'theme': 'dark', 'value': '#ffffff'},
                            ],
                        },
                        'amount': [
                            {'theme': 'light', 'value': '#000000'},
                            {'theme': 'dark', 'value': '#ffffff'},
                        ],
                        'action': {
                            'title': {
                                'text': 'message.service_fee_form_title',
                                'color': [
                                    {'theme': 'light', 'value': '#000000'},
                                    {'theme': 'dark', 'value': '#ffffff'},
                                ],
                            },
                            'buttons': [
                                {
                                    'id': 'close_button',
                                    'color': [
                                        {'theme': 'light', 'value': '#ffdd55'},
                                        {'theme': 'dark', 'value': '#333333'},
                                    ],
                                    'title': {
                                        'text': (
                                            'message.'
                                            'service_fee_button_close_text'
                                        ),
                                        'color': [
                                            {
                                                'theme': 'light',
                                                'value': '#000000',
                                            },
                                            {
                                                'theme': 'dark',
                                                'value': '#ffffff',
                                            },
                                        ],
                                    },
                                },
                                {
                                    'id': 'info_button',
                                    'color': [
                                        {'theme': 'light', 'value': '#ffdd55'},
                                        {'theme': 'dark', 'value': '#333333'},
                                    ],
                                    'title': {
                                        'text': (
                                            'message.'
                                            'service_fee_button_info_text'
                                        ),
                                        'color': [
                                            {
                                                'theme': 'light',
                                                'value': '#000000',
                                            },
                                            {
                                                'theme': 'dark',
                                                'value': '#ffffff',
                                            },
                                        ],
                                    },
                                    'deeplink': 'https://more_information/',
                                },
                            ],
                            'description': {
                                'text': 'message.service_fee_main_text',
                                'color': [
                                    {'theme': 'light', 'value': '#000000'},
                                    {'theme': 'dark', 'value': '#ffffff'},
                                ],
                            },
                            'block_buttons': True,
                        },
                        'subtitle': {
                            'text': 'message.service_fee_subtitle',
                            'color': [
                                {'theme': 'light', 'value': '#000000'},
                                {'theme': 'dark', 'value': '#ffffff'},
                            ],
                        },
                    },
                    'delivery_fee': {
                        'title': {
                            'text': 'message.delivery_fee_title',
                            'color': [
                                {'theme': 'light', 'value': '#000000'},
                                {'theme': 'dark', 'value': '#ffffff'},
                            ],
                        },
                        'amount': [
                            {'theme': 'light', 'value': '#a500cc'},
                            {'theme': 'dark', 'value': '#a500cc'},
                        ],
                        'action': {
                            'title': {
                                'text': 'message.delivery_fee_form_title',
                                'color': [
                                    {'theme': 'light', 'value': '#000000'},
                                    {'theme': 'dark', 'value': '#ffffff'},
                                ],
                            },
                            'buttons': [
                                {
                                    'id': 'close_button',
                                    'color': [
                                        {'theme': 'light', 'value': '#ffdd55'},
                                        {'theme': 'dark', 'value': '#333333'},
                                    ],
                                    'title': {
                                        'text': (
                                            'message.'
                                            'delivery_fee_button_close_text'
                                        ),
                                        'color': [
                                            {
                                                'theme': 'light',
                                                'value': '#000000',
                                            },
                                            {
                                                'theme': 'dark',
                                                'value': '#ffffff',
                                            },
                                        ],
                                    },
                                },
                            ],
                            'image_url': 'image/123delivery.png',
                            'description': {
                                'text': delivery_fee_main_text,
                                'color': [
                                    {'theme': 'light', 'value': '#000000'},
                                    {'theme': 'dark', 'value': '#ffffff'},
                                ],
                            },
                            'block_buttons': False,
                        },
                        'subtitle': {
                            'text': delivery_fee_subtitle,
                            'color': [
                                {'theme': 'light', 'value': '#000000'},
                                {'theme': 'dark', 'value': '#ffffff'},
                            ],
                        },
                        'image_url': 'https://lightning_picture/',
                    },
                },
            },
        ],
    )


SELECT_CART_ITEMS = (
    'SELECT id, cart_id, place_menu_item_id, price, '
    'promo_price, quantity, deleted_at, is_auto '
    'FROM eats_cart.cart_items ORDER BY id;'
)

SELECT_CART_ITEM_FOR_CART = (
    'SELECT id, cart_id, place_menu_item_id, price, '
    'promo_price, quantity, deleted_at FROM eats_cart.cart_items '
    'WHERE cart_id = %s '
    'ORDER BY id;'
)

SELECT_CART = (
    'SELECT id, revision, eater_id, place_slug, place_id, promo_subtotal, '
    'total, delivery_fee, shipping_type, deleted_at, delivery_time '
    'FROM eats_cart.carts ORDER BY created_at'
)

SELECT_ACTIVE_CART = (
    'SELECT id, revision, eater_id, place_slug, place_id, promo_subtotal, '
    'total, delivery_fee, shipping_type, delivery_time '
    'FROM eats_cart.carts WHERE deleted_at IS NULL'
)

SELECT_EATER_CART = 'SELECT eater_id, cart_id FROM eats_cart.eater_cart'

SELECT_ACTIVE_EATER_CART = (
    'SELECT eater_id, cart_id FROM eats_cart.eater_cart '
    'WHERE cart_id IS NOT NULL'
)

SELECT_CART_ITEM_OPTIONS = (
    'SELECT cart_item_id, option_id, price, promo_price, quantity '
    'FROM eats_cart.cart_item_options ORDER BY cart_item_id, option_id'
)

SELECT_ACTIVE_NEW_ITEM_DISCOUNTS = (
    'SELECT cart_item_id, promo_id, amount '
    'FROM eats_cart.new_cart_item_discounts '
    'WHERE deleted_at IS NULL ORDER BY created_at;'
)

SELECT_NEW_ITEM_DISCOUNTS = (
    'SELECT promo_id, amount, deleted_at '
    'FROM eats_cart.new_cart_item_discounts '
    'ORDER BY created_at;'
)


def select_new_cart_discount(cart_id=None):
    return (
        'SELECT promo_id, amount, deleted_at '
        'FROM eats_cart.new_cart_discounts '
        '%s '
        'ORDER BY created_at;'
    ) % ('WHERE cart_id = \'' + cart_id + '\'' if cart_id else '')


SELECT_CART_DISCOUNTS = (
    'SELECT name, deleted_at FROM eats_cart.cart_discounts;'
)

ITEM_PROPERTIES = {
    'quantity': 2,
    'item_options': [
        {
            'group_id': 10372250,
            'group_options': [1679268432, 1679268437],
            'modifiers': [
                {'option_id': 1679268432, 'quantity': 1},
                {'option_id': 1679268437, 'quantity': 1},
            ],
        },
        {
            'group_id': 10372255,
            'group_options': [1679268442],
            'modifiers': [{'option_id': 1679268442, 'quantity': 2}],
        },
    ],
    'shipping_type': 'delivery',
}

LOCK_CART_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS = [
    pytest.param(
        marks=pytest.mark.config(
            EATS_CART_LOCK_CART_USER_FROM_MIDDLEWARES=False,
        ),
        id='disabled-EATS_CART_LOCK_CART_USER_FROM_MIDDLEWARES',
    ),
    pytest.param(
        marks=pytest.mark.config(
            EATS_CART_LOCK_CART_USER_FROM_MIDDLEWARES=True,
        ),
        id='enabled-EATS_CART_LOCK_CART_USER_FROM_MIDDLEWARES',
    ),
]

RELATED_DATA_USER_FROM_MIDDLEWARES_CONFIG_PYTEST_PARAMS = [
    pytest.param(
        False,
        marks=pytest.mark.config(
            EATS_CART_RELATED_DATA_USER_FROM_MIDDLEWARES=False,
        ),
        id='disabled-EATS_CART_RELATED_DATA_USER_FROM_MIDDLEWARES',
    ),
    pytest.param(
        True,
        marks=pytest.mark.config(
            EATS_CART_RELATED_DATA_USER_FROM_MIDDLEWARES=True,
        ),
        id='enabled-EATS_CART_RELATED_DATA_USER_FROM_MIDDLEWARES',
    ),
]


class PlaceOption:
    def __init__(
            self,
            option_id: int,
            price: float,
            promo_price: typing.Optional[float],
            multiplier: int = 2,
    ) -> None:
        self.option_id = option_id
        self.price = price
        self.promo_price = promo_price
        self.multiplier = multiplier
        if self.price == self.promo_price:
            print('error: option has same price and promo_price')
            self.promo_price = None

    def serialize(self) -> dict:
        return {
            'id': self.option_id,
            'decimalPrice': str(self.price),
            'decimalPromoPrice': (
                str(self.promo_price) if self.promo_price else None
            ),
            'multiplier': self.multiplier,
            'name': 'Сметана - 30 гр',
            'price': math.ceil(self.price),
            'promoPrice': (
                math.ceil(self.promo_price) if self.promo_price else None
            ),
        }


class PlaceOptionGroup:
    def __init__(
            self,
            group_id: int,
            max_selected: int = 5,
            min_selected: int = 0,
            required: bool = False,
            options: typing.Optional[typing.List[PlaceOption]] = None,
    ) -> None:
        self.group_id: int = group_id
        self.max_selected: int = max_selected
        self.min_selected: int = min_selected
        self.required: bool = required
        self.options: typing.List[
            PlaceOption
        ] = [] if not options else copy.deepcopy(options)

    def add_option(self, option: PlaceOption) -> None:
        self.options.append(option)

    def serialize(self) -> dict:
        options = []
        for option in self.options:
            options.append(option.serialize())
        return {
            'id': self.group_id,
            'maxSelected': self.max_selected,
            'minSelected': self.min_selected,
            'name': 'Соус на выбор',
            'required': self.required,
            'options': options,
        }

    def get_max_options_price(self) -> float:
        res = 0.0
        for option in self.options:
            res += option.price * option.multiplier
        return res

    def get_max_options_promo_price(self) -> typing.Optional[float]:
        res = 0.0
        for option in self.options:
            if option.promo_price:
                res += option.promo_price * option.multiplier
            else:
                res += option.price * option.multiplier
        if res == self.get_max_options_price():
            return None

        return res


class PlaceItem:
    def __init__(
            self,
            item_id: int,
            price: float,
            promo_price: typing.Optional[float],
            available: bool = True,
            in_stock: typing.Optional[int] = None,
            options_groups: typing.Optional[
                typing.List[PlaceOptionGroup]
            ] = None,
            shipping_type: str = 'all',
            promo_types: typing.Optional[typing.List[typing.Dict]] = None,
    ) -> None:
        self.item_id: int = item_id
        self.price: float = price
        self.promo_price: typing.Optional[float] = promo_price
        self.available: bool = available
        self.in_stock: typing.Optional[int] = in_stock
        self.options_groups: typing.List[
            PlaceOptionGroup
        ] = [] if not options_groups else copy.deepcopy(options_groups)
        self.shipping_type: str = shipping_type
        self.promo_types: typing.List[
            typing.Dict
        ] = [] if not promo_types else copy.deepcopy(promo_types)
        if self.price == self.promo_price:
            print('error: item has same price and promo_price')
            self.promo_price = None

    def add_option_group(self, group: PlaceOptionGroup) -> None:
        self.options_groups.append(group)

    def serialize(self) -> dict:
        options_groups = []
        for group in self.options_groups:
            options_groups.append(group.serialize())
        return {
            'adult': False,
            'available': self.available,
            'decimalPrice': str(self.price),
            'decimalPromoPrice': (
                str(self.promo_price) if self.promo_price else None
            ),
            'description': 'Плов и соус к нему на выбор, долма',
            'id': self.item_id,
            'inStock': self.in_stock,
            'name': 'Сет Плов и долма',
            'optionsGroups': options_groups,
            'picture': {
                'ratio': 1,
                'scale': 'aspect_fill',
                'uri': '/images/3534679/3b74946183f0ef-{w}x{h}.jpeg',
            },
            'price': math.ceil(self.price),
            'promoPrice': (
                math.ceil(self.promo_price) if self.promo_price else None
            ),
            'promoTypes': self.promo_types,
            'shippingType': self.shipping_type,
            'shortName': None,
            'weight': '1\u00a0kg',
        }

    def get_options_for_request(self, one_as_bool: bool) -> list:
        res = []
        for group in self.options_groups:
            group_options = []
            modifiers = []
            for option in group.options:
                group_options.append(option.option_id)
                modifiers.append(
                    {
                        'option_id': option.option_id,
                        'quantity': (
                            option.multiplier
                            if not one_as_bool or option.multiplier > 1
                            else True
                        ),
                    },
                )
            res.append(
                {
                    'group_id': group.group_id,
                    'group_options': group_options,
                    'modifiers': modifiers,
                },
            )
        return res

    def get_price(self) -> float:
        res = self.price
        for group in self.options_groups:
            res += group.get_max_options_price()
        return res

    def get_promo_price(self) -> typing.Optional[float]:
        res = self.promo_price if self.promo_price else self.price
        for group in self.options_groups:
            options_promo_price = group.get_max_options_promo_price()
            if options_promo_price:
                res += options_promo_price
            else:
                res += group.get_max_options_price()

        if res == self.get_price():
            return None
        return res


class CoreItemsResponse:
    def __init__(
            self,
            place_id: str,
            items: typing.Optional[typing.List[PlaceItem]] = None,
            place_slug: typing.Optional[str] = None,
            place_brand_business_type: str = 'restaurant',
    ) -> None:
        self.place_id: str = place_id
        self.place_slug: str = place_slug if place_slug else f'place{place_id}'
        self.place_brand_business_type: str = place_brand_business_type
        self.items: typing.List[
            PlaceItem
        ] = [] if not items else copy.deepcopy(items)

    def add_item(self, item: PlaceItem) -> None:
        self.items.append(item)

    def serialize(self) -> dict:
        place_menu_items = []
        for item in self.items:
            place_menu_items.append(item.serialize())
        res = {
            'place_brand_business_type': self.place_brand_business_type,
            'place_id': self.place_id,
            'place_menu_items': place_menu_items,
            'place_slug': self.place_slug,
        }
        return res


async def add_item(
        taxi_eats_cart,
        local_services,
        item: PlaceItem,
        eater_id: str,
        quantity: int = 1,
        options: typing.Optional[list] = None,
        shipping_type: str = 'delivery',
        one_as_bool: bool = False,
        expected_code: int = 200,
):
    if not options:
        options = item.get_options_for_request(one_as_bool)
    elif one_as_bool:
        for opt in options:
            if 'modifiers' not in opt:
                continue
            for mod in opt['modifiers']:
                if mod['quantity'] == 1:
                    mod['quantity'] = True
    body = {
        'item_id': item.item_id,
        'quantity': quantity if not one_as_bool or quantity > 1 else True,
        'shipping_type': shipping_type,
        'item_options': options,
    }

    response = await taxi_eats_cart.post(
        'api/v1/cart',
        params=local_services.request_params,
        headers=get_auth_headers(eater_id),
        json=body,
    )
    assert response.status_code == expected_code
    return response.json()


def convert_item_ids(item: dict, converter) -> dict:
    if 'item_id' in item:
        item['item_id'] = converter(item['item_id'])
    for group in item['item_options']:
        group['group_id'] = converter(group['group_id'])
        converted_option_ids = []
        for option_id in group['group_options']:
            converted_option_ids.append(converter(option_id))
        group['group_options'] = converted_option_ids
        for option in group['modifiers']:
            option['option_id'] = converter(option['option_id'])
    return item


def make_lock_cart_body(eater_id, for_pickup):
    default = get_params()
    body = {
        'eater_id': eater_id,
        'latitude': default['latitude'],
        'longitude': default['longitude'],
        'delivery_time': default['deliveryTime'],
        'shipping_type': 'pickup' if for_pickup else 'delivery',
    }
    if for_pickup:
        del body['latitude']
        del body['longitude']
    return body


async def call_lock_cart(
        taxi_eats_cart, eater_id, headers, for_pickup=False, data=None,
):
    path = (
        '/internal/eats-cart/v1/lock_cart_pickup'
        if for_pickup
        else '/internal/eats-cart/v1/lock_cart'
    )
    return await taxi_eats_cart.post(
        path,
        headers=headers,
        json=data
        if data is not None
        else make_lock_cart_body(eater_id, for_pickup),
    )


def add_to_number(number, delta):
    if isinstance(number, numbers.Number):
        return number + delta
    if isinstance(number, str):
        return str(float(number) + delta)
    return None


def update_matching_keys(object_, pattern, callable_):
    for key, value in object_.items():
        if re.match(pattern, key):
            object_[key] = callable_(value)


def make_cashback_data(plus_response: dict) -> dict:
    result = copy.deepcopy(plus_response)

    result['cashback_income'] = {
        'title': result['title'],
        'subtitle': result['description'],
        'cashback': result['decimal_cashback'],
        'deeplink': result['deeplink'],
    }

    result['cashback_outcome'] = {
        'title': result['outcome_title'],
        'subtitle': result['outcome_description'],
        'cashback': '0',
        'deeplink': result['deeplink'],
    }

    del result['decimal_cashback_outcome']

    del result['outcome_description']
    del result['outcome_title']

    return result


def do_nothing(*args, **kwargs):
    pass


EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT = [
    {
        'id': 123,
        'slug': 'place123',
        'revision_id': 1,
        'updated_at': '2020-11-26T00:00:00.000000Z',
        'region': {
            'id': 123,
            'geobase_ids': [1, 2, 3, 4, 5],
            'time_zone': 'UTC+3',
        },
        'brand': {
            'id': 122333,
            'slug': 'slug',
            'name': 'name',
            'picture_scale_type': 'aspect_fit',
        },
        'business': 'restaurant',
        'allowed_couriers_types': ['pedestrian'],
        'country': {
            'name': 'Russia',
            'code': 'RU',
            'currency': {'code': 'RUB', 'sign': '₽'},
            'id': 35,
        },
    },
]


def weight_fee_experiment(enabled=True):
    return pytest.mark.experiments3(
        name='eats_cart_weight_fee',
        consumers=['eats_cart/default_eats_cart_kwargs'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
    )


def matching_discounts_experiments(enabled, exp_name):
    return pytest.mark.experiments3(
        clauses=[
            {
                'predicate': {'init': {}, 'type': 'true'},
                'title': 'any-title',
                'value': {'enabled': enabled, 'value': exp_name},
            },
        ],
        consumers=['eats-discounts-applicator/users_experiments'],
        name=exp_name,
    )


def compare_and_remove_time(response, expected, field):
    expected_time = to_datetime(expected[field])
    del expected[field]
    response_time = to_datetime(response[field])
    del response[field]
    assert expected_time == response_time
