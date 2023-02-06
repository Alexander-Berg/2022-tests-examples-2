# pylint: disable=C0302
import typing

import pytest

from eats_catalog import adverts

# pylint: disable=C0302

ALWAYS = {'predicate': {'type': 'true'}, 'enabled': True}


def always_match(
        name: str, consumer: str, value: dict, is_config: bool = False,
):
    return pytest.mark.experiments3(
        is_config=is_config,
        match=ALWAYS,
        name=name,
        consumers=[consumer],
        clauses=[
            {
                'title': 'Always match',
                'value': value,
                'predicate': {'type': 'true'},
            },
        ],
        enable_debug=True,
    )


DISABLE_PREORDER = always_match(
    name='eats_catalog_preorder',
    consumer='eats-catalog-places-storage',
    value={
        'disable_for_restaurants': True,
        'disable_for_shops': True,
        'disable_for_bk': True,
        'disable_for_whitelabel': True,
    },
    is_config=True,
)

DISABLE_PREORDER_FOR_SHOPS_ONLY = always_match(
    name='eats_catalog_preorder',
    consumer='eats-catalog-places-storage',
    value={'disable_for_restaurants': False, 'disable_for_shops': True},
    is_config=True,
)

DISABLE_PREORDER_FOR_RESTAURANTS = always_match(
    name='eats_catalog_preorder',
    consumer='eats-catalog-places-storage',
    value={'disable_for_restaurants': True, 'disable_for_shops': False},
    is_config=True,
)

DISABLE_PREORDER_FOR_BK = always_match(
    name='eats_catalog_preorder',
    consumer='eats-catalog-places-storage',
    value={
        'disable_for_restaurants': False,
        'disable_for_shops': False,
        'disable_for_bk': True,
    },
    is_config=True,
)

DISABLE_TOP = always_match(
    name='eats_catalog_disable_top_rating_meta',
    consumer='eats-catalog-for-layout',
    value={'enabled': True},
)

INCLUDE_ASSEMBLY_COST = always_match(
    name='eda_slug_thresholds_with_assembly_cost',
    consumer='eats-catalog-slug',
    value={'enabled': True},
)

SHOW_PLACE_CATEGORIES = always_match(
    name='eats_catalog_show_place_categories',
    consumer='eats-catalog-for-layout',
    value={'enabled': True},
)

DISABLE_ADVERTS = pytest.mark.experiments3(
    match=ALWAYS,
    name='eats_switching_off_advertising',
    consumers=['eats-catalog-advertiser'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
    is_config=True,
)

USE_DELIVERY_SLOTS = pytest.mark.experiments3(
    is_config=True,
    name='eats_catalog_slots_enabled',
    consumers=[
        'eats-catalog-for-layout',
        'eats-catalog-slug',
        'eats-catalog-place',
    ],
    match=ALWAYS,
    clauses=[
        {
            'title': 'Magnit',
            'value': {'enabled': False},
            'predicate': {
                'type': 'bool',
                'init': {'arg_name': 'is_magnit_app'},
            },
        },
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

TOP_RATING_TAG = always_match(
    name='eats_catalog_known_tags',
    consumer='eats-catalog-for-layout',
    value={'tags': ['top_rating']},
)

ENABLE_FAVORITES = pytest.mark.experiments3(
    match=ALWAYS,
    name='eda_favorite_brands',
    consumers=['eats-catalog-slug', 'eats-catalog-for-layout'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

EATS_DISCOUNTS_ENABLE = pytest.mark.experiments3(
    name='eats_discounts_enabled',
    # консьюмер внутри библиотеки eats-discounts-applicator
    consumers=['eats-discounts-applicator/enabled_discounts'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)

EATS_DISCOUNTS_PROMO_TYPES_INFO = pytest.mark.experiments3(
    name='eats_discounts_promo_types_info',
    is_config=True,
    consumers=['eats-discounts-applicator/user'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'true',
            'predicate': {'type': 'true'},
            'value': {
                'delivery_discount': {
                    'id': 1011,
                    'name': 'Скидка на доставку',
                    'description': 'Скидка на доставку',
                    'picture_uri': 'uri',
                },
            },
        },
    ],
)


EATS_DISCOUNTS_APPLICATOR_FOR_CATALOG = pytest.mark.experiments3(
    name='eats_discounts_applicator_in_eats_catalog',
    consumers=['eats-catalog-slug', 'eats-catalog-for-layout'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'true',
            'predicate': {'type': 'true'},
            'value': {'enabled': True},
        },
    ],
)


def eats_discounts_for_marketplaces(value):
    return always_match(
        name='eats_discounts_marketplace',
        consumer='eats-catalog-for-layout',
        value=value,
    )


DISABLE_AVAILABLE_SLUG = pytest.mark.experiments3(
    is_config=True,
    match=ALWAYS,
    name='eats_catalog_unavailable_slug',
    consumers=['eats-catalog-slug', 'eats-catalog-for-layout'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

USE_UMLAAS = pytest.mark.experiments3(
    is_config=True,
    match=ALWAYS,
    name='eats_catalog_umlaas',
    consumers=['eats-catalog-for-full-text-search'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

BRAND_COLOR_OVERRIDES = pytest.mark.experiments3(
    is_config=True,
    match=ALWAYS,
    name='eats_catalog_slug_brand_color_overrides',
    consumers=['eats-catalog-slug'],
    clauses=[
        {
            'title': 'Always match',
            'value': {
                'color': [
                    {'theme': 'light', 'value': '#000000'},
                    {'theme': 'dark', 'value': '#FFFFFF'},
                ],
                'logo_url': [
                    {'theme': 'light', 'size': 'small', 'url': 'light_url'},
                    {'theme': 'dark', 'size': 'small', 'url': 'dark_url'},
                ],
            },
            'predicate': {'type': 'true'},
        },
    ],
    enable_debug=True,
)


HIDE_RATING_COUNT = pytest.mark.experiments3(
    match=ALWAYS,
    name='eats_hide_rating_count',
    consumers=['eats-catalog-slug', 'eats-catalog-for-layout'],
    clauses=[
        {
            'title': 'Always match',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)

SHOP_FIRST = always_match(
    name='eats_catalog_sort_shop_to_top',
    consumer='eats-catalog-for-layout',
    value={'enabled': True},
    is_config=True,
)


SLUG_SHIPPING_ICONS = pytest.mark.experiments3(
    is_config=True,
    match=ALWAYS,
    name='eats_catalog_slug_shipping_icons',
    consumers=['eats-catalog-slug'],
    clauses=[
        {
            'title': 'Default icons',
            'value': {
                'courier': 'asset://icon_courier',
                'pickup': 'asset://icon_pickup',
                'rover': 'asset://icon_rover',
                'preorder': 'asset://icon_preorder',
                'high_price': 'asset://icon_high_price',
                'taxi': 'asset://icon_taxi',
                'marketplace_courier': 'asset://icon_marketplace_courier',
            },
            'predicate': {'type': 'true'},
        },
    ],
)

USE_SURGE_FINAL_PRICE = always_match(
    name='eats_catalog_use_surge_final_cost',
    consumer='eats-catalog-place',
    value={'enabled': True},
)

SLUG_SHIPPING_FEE_COLORS = always_match(
    name='eats_catalog_slug_shipping_fee_colors',
    consumer='eats-catalog-slug',
    value={
        'free_of_charge': [{'theme': 'light', 'value': '#00ff00'}],
        'surge': [{'theme': 'light', 'value': '#ff0000'}],
        'shipping_info_action_surge': [{'theme': 'light', 'value': '#0000ff'}],
    },
    is_config=True,
)

SEND_SURGE_ON_RADIUS = always_match(
    is_config=True,
    name='eats_catalog_send_surge_on_radius',
    consumer='eats-catalog-slug',
    value={'enabled': True},
)

USE_CUSTOMER_SLOTS_SHARED = pytest.mark.experiments3(
    is_config=True,
    match=ALWAYS,
    name='eats_catalog_use_eats_customer_slots_shared_for_timepicker',
    consumers=['eats-catalog-place', 'eats-catalog-slug'],
    clauses=[
        {
            'title': 'Default',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)


SHOW_SURGE_RADIUS_ON_CATALOG = always_match(
    name='eats_catalog_show_surge_radius_on_catalog',
    consumer='eats-catalog-for-layout',
    value={'enabled': True},
)


DISABLE_REVIEW_ACTION = always_match(
    name='eats_layout_constructor_disable_zen',
    consumer='eats-catalog-for-layout',
    value={'enabled': True},
)


DISABLE_CALC_SURGE_BULK = always_match(
    name='eats_catalog_disable_calc_surge_bulk',
    consumer='eats-catalog-for-layout',
    value={'enabled': True},
)

ENABLE_SHOP_RESOLVE = always_match(
    is_config=True,
    name='eats_catalog_enable_slot_resolve',
    consumer='eats-catalog-delivery-zone-resolve',
    value={'enabled': True},
)

DISABLE_PROMOS = always_match(
    is_config=True,
    name='eats_catalog_disable_promos',
    consumer='eats-catalog-slug',
    value={'enabled': True},
)

ENABLE_CONTINUOUS_THRESHOLDS_CALC = always_match(
    is_config=True,
    name='eats_catalog_slug_continuous_thresholds_calc',
    consumer='eats-catalog-slug',
    value={'enabled': True},
)

ENABLE_SHIPPING_FEE_WITH_PROMO_CALC = always_match(
    is_config=True,
    name='eats_catalog_slug_shipping_fee_with_promo_calc',
    consumer='eats-catalog-slug',
    value={'enabled': True},
)

SHOW_SERVICE_FEE = always_match(
    name='eats_catalog_slug_service_fee',
    consumer='eats-catalog-slug',
    value={'enabled': True},
)


def old_discounts_disable(enabled, promo):
    return pytest.mark.experiments3(
        name='eats_old_discounts_disable',
        consumers=['eats-catalog-for-layout'],
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled, 'discount_off': promo},
            },
        ],
    )


def pickup_availability(
        new_flow: bool = True,
        user_late: int = 5,
        check_preparation_after: int = 15,
):
    return always_match(
        name='eats_places_availability_pickup',
        consumer='eats-catalog-places-storage',
        value={
            'enable_new_pickup_flow': new_flow,
            'pickup_user_late_minutes': user_late,
            'check_preparation_after': check_preparation_after,
        },
    )


def top_rating_view(
        tag_name='top_rating',
        filter_name='Топ',
        filter_icon=None,
        filter_picture=None,
        filter_icon_v2=None,
):
    top_rating_config = {'tag_name': tag_name, 'filter_name': filter_name}

    if filter_icon:
        top_rating_config['filter_icon'] = filter_icon
    if filter_picture:
        top_rating_config['filter_picture'] = filter_picture

    if filter_icon_v2:
        top_rating_config['filter_icon_v2'] = filter_icon_v2

    return always_match(
        is_config=True,
        name='eats_catalog_tags_view',
        consumer='eats-catalog-for-layout',
        value={'top_rating': top_rating_config},
    )


def advertisements(source='experiment', brand_ids=None, place_ids=None):
    value = {'source': source}
    if brand_ids:
        value['brand_ids'] = brand_ids
    if place_ids:
        value['place_ids'] = place_ids

    return always_match(
        name='eats_catalog_advertisements',
        consumer='eats-catalog-advertiser',
        value=value,
        is_config=True,
    )


def eats_catalog_advertisement_meta(
        text_key: str = None, text_color: list = None, background: list = None,
):
    """
    Возвращает конфиг с настройками рекламной меты.
    """

    default_text: str = 'Реклама'
    default_text_color: list = [
        {'theme': 'light', 'value': '#999588'},
        {'theme': 'dark', 'value': '#999588'},
    ]
    default_background: list = [
        {'theme': 'light', 'value': '#EBE7DA'},
        {'theme': 'dark', 'value': '#56544D'},
    ]

    value: dict = {
        'text': {'text': default_text, 'color': default_text_color},
        'background': default_background,
    }

    if text_key:
        value['text']['text_key'] = text_key
    if text_color:
        value['text']['color'] = text_color
    if background:
        value['background'] = background

    return always_match(
        is_config=True,
        name='eats_catalog_advertisement_meta',
        consumer='eats-catalog-for-layout',
        value=value,
    )


def yabs_settings(settings: adverts.YabsSettings = adverts.YabsSettings()):
    return always_match(
        name='eats_catalog_yabs_settings',
        consumer='eats-catalog-advertiser',
        value=settings.asdict(),
        is_config=True,
    )


def advert_ctr_source(ctr_source: adverts.CTRSource):
    return always_match(
        name='eats_catalog_advert_ctr_source',
        consumer='eats-catalog-advertiser',
        value={'source': ctr_source},
        is_config=True,
    )


def couriers_pickup(brand_ids=None, place_ids=None):
    if not brand_ids:
        brand_ids = []

    if not place_ids:
        place_ids = []

    return always_match(
        is_config=True,
        name='eats_couriers_pickup',
        consumer='eats-catalog-places-storage',
        value={'brand_ids': brand_ids, 'place_ids': place_ids},
    )


def new_rating(thresholds=None):
    if not thresholds:
        thresholds = []

    return pytest.mark.experiments3(
        match=ALWAYS,
        name='eats_new_rating',
        consumers=['eats-catalog-slug', 'eats-catalog-for-layout'],
        clauses=[
            {
                'title': 'Always match',
                'value': {'thresholds': thresholds},
                'predicate': {'type': 'true'},
            },
        ],
    )


def qsr_pickup_user(personal_phone_id: typing.Optional[str] = None):
    if personal_phone_id is None:
        return pytest.mark.experiments3(
            name='open_qsr_pickup',
            consumers=['eats-catalog-places-storage'],
            clauses=[
                {
                    'title': 'Always match',
                    'value': {'enabled': True},
                    'predicate': {'type': 'true'},
                },
            ],
        )

    return pytest.mark.experiments3(
        name='open_qsr_pickup',
        consumers=['eats-catalog-places-storage'],
        clauses=[
            {
                'title': 'special user',
                'value': {'enabled': True},
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'personal_phone_id',
                        'arg_type': 'string',
                        'value': personal_phone_id,
                    },
                },
            },
            {
                'title': 'default',
                'value': {'enabled': False},
                'predicate': {'type': 'true', 'init': {}},
            },
        ],
    )


def currency_sign(sign):
    return pytest.mark.experiments3(
        name='eats_catalog_currency',
        consumers=[
            'eats-catalog-for-layout',
            'eats-catalog-slug',
            'eats-catalog-for-full-text-search',
        ],
        match=ALWAYS,
        clauses=[
            {
                'title': 'Always match',
                'predicate': {'type': 'true'},
                'value': {'currency_sign': sign},
            },
        ],
        is_config=True,
    )


def places_with_free_delivery_badge(
        text: str = 'Бейдж бесплатной доставки конкретного ресторана',
):
    return pytest.mark.experiments3(
        is_config=True,
        match=ALWAYS,
        name='eats_catalog_badge',
        consumers=['eats-catalog-layout-badge'],
        clauses=[
            {
                'title': 'All',
                'value': {'text': text},
                'predicate': {
                    'type': 'bool',
                    'init': {'arg_name': 'place_free_delivery'},
                },
            },
        ],
        default_value={},
    )


def eats_catalog_surge_radius(
        enabled: bool = True,
        enable_taxi_flowing: bool = True,
        enable_taxi_radius: bool = False,
        place_batch_size: int = 1000,
        use_lru_cache: bool = False,
):
    """
    FIXME сам по себе декоратор не работает,
    нужно еще задать время через
    @configs.eats_catalog_delivery_feature(disable_by_surge_for_minutes=240)
    """
    return always_match(
        is_config=True,
        name='eats_catalog_surge_radius',
        consumer='eats-catalog-places-storage',
        value={
            'enabled': enabled,
            'enable_taxi_flowing': enable_taxi_flowing,
            'enable_taxi_radius': enable_taxi_radius,
            'place_batch_size': place_batch_size,
            'use_lru_cache': use_lru_cache,
        },
    )


def surge_texts(
        title_key: str = '',
        message_key: str = '',
        description_key: str = '',
        delivery_unavailable_title_key: str = '',
        preorder_title_key: str = '',
        delivery_unavailable_message_key: str = '',
        preorder_message_key: str = '',
):
    values_all = {
        'title_key': title_key,
        'message_key': message_key,
        'description_key': description_key,
        'delivery_unavailable_title_key': delivery_unavailable_title_key,
        'preorder_title_key': preorder_title_key,
        'delivery_unavailable_message_key': delivery_unavailable_message_key,
        'preorder_message_key': preorder_message_key,
    }
    values_filtered = {k: v for k, v in values_all.items() if v}

    return always_match(
        is_config=True,
        name='eats_catalog_surge_texts',
        consumer='eats-catalog-slug',
        value=values_filtered,
    )


def filter_source_response(
        brand_ids: typing.Optional[typing.List[int]] = None,
        place_ids: typing.Optional[typing.List[int]] = None,
):
    return always_match(
        name='eats_catalog_places_filter',
        consumer='eats-catalog-places-storage',
        value={'brand_ids': brand_ids, 'place_ids': place_ids},
        is_config=True,
    )


def advert_auction_filter(
        place_ids: typing.List[int] = None,
        brand_ids: typing.List[int] = None,
        predicate: dict = None,
):
    """
    Возвращает эксперимент по фильтрации ресторанов из аукциона.
    """
    return always_match(
        name='advert_auction_filter',
        consumer='eats-catalog-advertiser',
        value={
            'brand_ids': brand_ids or [],
            'place_ids': place_ids or [],
            'predicate': predicate,
        },
        is_config=True,
    )


def eda_yandex_rover_courier(
        place_ids: typing.List[int],
        weekday: typing.Optional[int] = None,
        hour: typing.Optional[int] = None,
):
    predicates = [
        {
            'type': 'in_set',
            'init': {
                'arg_name': 'place_id',
                'set_elem_type': 'int',
                'set': place_ids,
            },
        },
    ]
    if weekday:
        predicates.append(
            {
                'type': 'eq',
                'init': {
                    'arg_name': 'weekday',
                    'arg_type': 'int',
                    'value': weekday,
                },
            },
        )
    if hour:
        predicates.append(
            {
                'type': 'eq',
                'init': {'arg_name': 'hour', 'arg_type': 'int', 'value': hour},
            },
        )

    return pytest.mark.experiments3(
        match=ALWAYS,
        name='eda_yandex_rover_courier',
        consumers=['eats-catalog-rover'],
        clauses=[
            {
                'title': 'Match',
                'value': {'enabled': True},
                'predicate': {
                    'type': 'all_of',
                    'init': {'predicates': predicates},
                },
            },
        ],
        default_value={'enabled': False},
    )


def known_tags(tags: typing.List[str]):
    return pytest.mark.experiments3(
        name='eats_catalog_known_tags',
        match=ALWAYS,
        consumers=['eats-catalog-for-layout', 'eats-catalog-slug'],
        clauses=[
            {
                'title': 'Always match',
                'predicate': {'type': 'true'},
                'value': {'tags': tags},
            },
        ],
    )


def michelin(
        project_tag: str,
        actions: typing.Optional[list] = None,
        banners: typing.Optional[list] = None,
):
    if actions is None:
        actions = []
    if banners is None:
        banners = []

    return pytest.mark.experiments3(
        match=ALWAYS,
        name='eats_catalog_michelin',
        consumers=['eats-catalog-for-layout', 'eats-catalog-slug'],
        is_config=True,
        default_value={
            'enabled': True,
            'project_tag': project_tag,
            'banners': banners,
            'actions': actions,
        },
    )


def free_delivery(enabled: bool):
    return always_match(
        name='eats_newbie_free_delivery_promo',
        consumer='eats-catalog-for-layout',
        value={'enabled': enabled, 'free_shop_delivery_text': 'free delivery'},
    )


def eta_text(
        default_tpl='%(min)s\u2009\u2013\u2009%(max)s мин',
        equal_tpl='~%(max)s мин',
        min_tpl='~%(min)s мин',
        max_tpl='~%(max)s мин',
        avg_tpl='~%(avg)s мин',
        default_hours_tpl='%(min)s\u2009\u2013\u2009%(max)s ч',
        equal_hours_tpl='~%(max)s ч',
        min_hours_tpl='~%(min)s ч',
        max_hours_tpl='~%(max)s ч',
        avg_hours_tpl='~%(avg)s ч',
):
    keyset = 'eats-catalog'
    default_key = 'delivary_feature.eta.default_tpl'
    equal_key = 'delivary_feature.eta.equal_tpl'
    min_key = 'delivary_feature.eta.min_tpl'
    max_key = 'delivary_feature.eta.max_tpl'
    avg_key = 'delivary_feature.eta.avg_tpl'

    default_hours_key = 'delivary_feature.hours.eta.default_tpl'
    equal_hours_key = 'delivary_feature.hours.eta.equal_tpl'
    min_hours_key = 'delivary_feature.hours.eta.min_tpl'
    max_hours_key = 'delivary_feature.hours.eta.max_tpl'
    avg_hours_key = 'delivary_feature.hours.eta.avg_tpl'

    def decorator(func):
        exp = always_match(
            name='eats_catalog_eta',
            consumer='eats-catalog-eta',
            is_config=True,
            value={
                'l10n': [
                    {
                        'default': '',
                        'key': 'default',
                        'tanker': {'key': default_key, 'keyset': keyset},
                    },
                    {
                        'default': '',
                        'key': 'equal',
                        'tanker': {'key': equal_key, 'keyset': keyset},
                    },
                    {
                        'default': '',
                        'key': 'min',
                        'tanker': {'key': min_key, 'keyset': keyset},
                    },
                    {
                        'default': '',
                        'key': 'max',
                        'tanker': {'key': max_key, 'keyset': keyset},
                    },
                    {
                        'default': '',
                        'key': 'avg',
                        'tanker': {'key': avg_key, 'keyset': keyset},
                    },
                    {
                        'default': '',
                        'key': 'default.hours',
                        'tanker': {'key': default_hours_key, 'keyset': keyset},
                    },
                    {
                        'default': '',
                        'key': 'equal.hours',
                        'tanker': {'key': equal_hours_key, 'keyset': keyset},
                    },
                    {
                        'default': '',
                        'key': 'min.hours',
                        'tanker': {'key': min_hours_key, 'keyset': keyset},
                    },
                    {
                        'default': '',
                        'key': 'max.hours',
                        'tanker': {'key': max_hours_key, 'keyset': keyset},
                    },
                    {
                        'default': '',
                        'key': 'avg.hours',
                        'tanker': {'key': avg_hours_key, 'keyset': keyset},
                    },
                ],
            },
        )

        loc = pytest.mark.translations(
            **{
                keyset: {
                    default_key: {'ru': [default_tpl]},
                    equal_key: {'ru': [equal_tpl]},
                    min_key: {'ru': [min_tpl]},
                    max_key: {'ru': [max_tpl]},
                    avg_key: {'ru': [avg_tpl]},
                    default_hours_key: {'ru': [default_hours_tpl]},
                    equal_hours_key: {'ru': [equal_hours_tpl]},
                    min_hours_key: {'ru': [min_hours_tpl]},
                    max_hours_key: {'ru': [max_hours_tpl]},
                    avg_hours_key: {'ru': [avg_hours_tpl]},
                },
            },
        )
        return loc(exp(func))

    return decorator


def brand_link(links: typing.List):
    return always_match(
        is_config=True,
        name='eats_catalog_place_link',
        consumer='eats-catalog-for-layout',
        value={'brand_link': links},
    )


def relaxed_ads_dedubliation():
    return always_match(
        is_config=True,
        name='eats_catalog_relaxed_ads_dedublication',
        consumer='eats-catalog-for-layout',
        value={'enabled': True},
    )


def surge_preorder(enabled: bool):
    return always_match(
        name='eats_catalog_surge_preorder',
        consumer='eats-catalog-surge',
        value={'enabled': enabled},
    )


def internal_places_deps_control(
        disable_surge: bool = False, disable_ranking: bool = False,
):
    return always_match(
        is_config=True,
        name='eats_catalog_internal_places_dependencies_control',
        consumer='eats-catalog-internal-places',
        value={
            'disable_surge': disable_surge,
            'disable_ranking': disable_ranking,
        },
    )


def emergency_disable_zone(
        interval: int = 120,
        disable_pedestrian: bool = False,
        disable_taxi: bool = False,
        disable_auto: bool = False,
):
    return always_match(
        name='eats_catalog_emergency_disable_zone',
        consumer='eats-catalog-emergency-disable-zone',
        value={
            'interval': interval,
            'disable_automobile_zones': disable_auto,
            'disable_pedestrian_zones': disable_pedestrian,
            'disable_taxi_zones': disable_taxi,
        },
    )


def matching_discounts_experiments(enabled, value):
    return pytest.mark.experiments3(
        clauses=[
            {
                'predicate': {'init': {}, 'type': 'true'},
                'title': 'any-title',
                'value': {'enabled': enabled, 'value': value},
            },
        ],
        consumers=['eats-discounts-applicator/users_experiments'],
        name=value,
    )


def hide_promos_slug(enabled, promo_type_ids):
    return always_match(
        name='eats_catalog_slug_hide_promo_actions',
        consumer='eats-catalog-slug',
        value={'enabled': enabled, 'promo_type_ids': promo_type_ids},
        is_config=True,
    )


def adverts_use_strong_indexing(enabled: bool):
    return always_match(
        name='eats_catalog_adverts_use_strong_indexing',
        consumer='eats-catalog-for-layout',
        value={'enabled': enabled},
    )


def eats_surge_planned(interval: int):
    return always_match(
        is_config=True,
        name='eats_surge_planned',
        consumer='eda-delivery-price/is-new-user',
        value={'time_interval_minutes': interval},
    )


def sort_promo_actions(consumer, limit, order):
    return always_match(
        name='eats_catalog_sort_promo_actions',
        consumer=consumer,
        value={'limit': limit, **order},
        is_config=True,
    )


def place_messages_pickup(
        title: str,
        description: typing.Optional[str] = None,
        footer: typing.Optional[str] = None,
):
    return always_match(
        is_config=True,
        name='eats_catalog_place_messages',
        consumer='eats-catalog-slug',
        value={
            'pickup': {
                'title': title,
                'description': description,
                'footer': footer,
            },
        },
    )


def surge_resolver_pipeline(pipeline_name: str):
    return always_match(
        is_config=True,
        name='eats_surge_resolver_pipeline',
        consumer='eats-surge-resolver/main',
        value={'pipeline_name': pipeline_name},
    )


def ignore_shipping_type_in_search(business_types: typing.List[str]):
    return always_match(
        is_config=True,
        name='eats_catalog_ignore_shipping_type_in_search',
        consumer='eats-catalog-for-full-text-search',
        value={'business_types': business_types},
    )


def tag_for_pickup_in_search(pickup_tag_key: typing.Optional[str]):
    return always_match(
        is_config=True,
        name='eats_catalog_special_tag_for_pickup_in_search',
        consumer='eats-catalog-for-full-text-search',
        value={'pickup_tag_key': pickup_tag_key} if pickup_tag_key else {},
    )


def eats_catalog_relevance_cache(
        source: adverts.RelevanceSource, default_value: float = 1.0,
):
    return always_match(
        is_config=False,
        name='eats_catalog_relevance_cache',
        consumer='eats-catalog-advertiser',
        value={'source': source.value, 'default_value': default_value},
    )


def enable_deduplication(consumer: typing.Optional[str] = None):
    if consumer is None:
        consumer = 'eats-catalog-layout'

    return always_match(
        name='eats_catalog_local_deduplication',
        value={'enabled': True},
        consumer=consumer,
    )


def deduplication(
        rules: typing.List[str],
        priority_tag: typing.Optional[str] = None,
        consumer: typing.Optional[str] = None,
):
    if consumer is None:
        consumer = 'eats-catalog-layout'

    return always_match(
        is_config=True,
        name='umlaas_eats_deduplication',
        value={
            'strategy': 'default',
            'rules': rules,
            'priority_tag': priority_tag,
        },
        consumer=consumer,
    )


def ranking_fallback(
        enable_fallback: bool = False, disable_umlaas: bool = False,
):
    return always_match(
        name='eats_catalog_use_ranking_fallback',
        value={'enabled': enable_fallback, 'disable_umlaas': disable_umlaas},
        consumer='eats-catalog-for-layout',
    )


def eats_catalog_show_plus(
        hide_plus: bool = False,
        hide_when_matched: bool = False,
        hide_when_matched_for_retail: bool = False,
        consumer='eats-catalog-for-layout',
):
    return always_match(
        name='eats_catalog_show_plus',
        value={
            'hide_plus': hide_plus,
            'hide_when_matched': hide_when_matched,
            'hide_when_matched_for_retail': hide_when_matched_for_retail,
        },
        consumer=consumer,
        is_config=True,
    )


def eats_catalog_sort_adverts(
        enabled, sort_types, consumer='eats-catalog-for-layout',
):
    return always_match(
        name='eats_catalog_sort_disable_adverts',
        value={'enabled': enabled, 'sort_types': sort_types},
        consumer=consumer,
    )


def eats_catalog_recommender_config(
        experiment: str = 'experiment', consumer='eats-catalog-advertiser',
):
    return always_match(
        name='eats_catalog_recommender_config',
        value={'experiment': experiment},
        consumer=consumer,
        is_config=True,
    )


def eats_catalog_yabs_coefficients(
        source: str = 'none',
        consumer='eats-catalog-advertiser',
        coefficients=adverts.Coefficients,
):
    return always_match(
        name='eats_catalog_yabs_coefficients',
        value={
            'relevance_source': source,
            'coefficients': coefficients.asdict(),
        },
        consumer=consumer,
        is_config=True,
    )
