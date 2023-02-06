import typing

import pytest


def eats_catalog_pickup(**kwargs):
    data = {
        'filter_name': 'Навынос',
        'filter_picture': '/images/pickup_filter',
        'filter_icon': '/icons/pickup_filter',
        'filter_name_v2': 'Навынос',
        'filter_icon_v2': '/icons/pickup_filter2',
    }
    data.update(kwargs)
    return pytest.mark.config(EATS_CATALOG_PICKUP=data)


def eats_catalog_plus_filter(**kwargs):
    data = {
        'name': 'Кэшбек',
        'icon_url': '/icons/plus',
        'name_v2': 'Кэшбек 2',
        'icon_url_v2': '/icons/plus2',
        'filter_picture': '/images/plus',
    }
    data.update(kwargs)
    return pytest.mark.config(EATS_CATALOG_PLUS_FILTER=data)


def eats_catalog_favorite(**kwargs):
    data = {
        'filter_name': 'Избранное',
        'filter_icon_url': 'asset://heart',
        'filter_name_v2': 'Избранное',
        'filter_icon_url_v2': 'asset://heart',
        'filter_filter_picture': 'asset://heart',
        'unauthorized_alert': {
            'title': 'Вы не авторизованы',
            'message': (
                'Пожалуйста, авторизуйтесь, для выбора фильтра "избранное"'
            ),
        },
        'no_favorites_alert': {
            'title': 'Избранные рестораны не найдены',
            'message': 'Избранные рестораны не найдены',
        },
        'never_liked_alert': {
            'title': 'Ничего не добавлено в избранное',
            'message': 'У вас нет ни одного избранного ресторана',
        },
    }
    data.update(kwargs)
    return pytest.mark.config(EATS_CATALOG_FAVORITE=data)


def eats_catalog_delivery_feature(**kwargs):
    data = {
        'surge_icon_url': 'asset://surg',
        'native_delivery_icon_url': 'asset://native_delivery',
        'taxi_delivery_icon_url': 'asset://native_delivery',
    }
    data.update(kwargs)
    return pytest.mark.config(EATS_CATALOG_DELIVERY_FEATURE=data)


def places_storage_settings(**kwargs):
    data = {
        'min_delivery_minutes': 5,
        'min_preparation_minutes': 5,
        'consider_new_for': 7,
        'schedule_end_offset': 0,
        'enable_place_schedule_filter': False,
        'place_schedule_filter_ignore_empty': True,
    }
    data.update(kwargs)
    return pytest.mark.config(EATS_CATALOG_PLACE_STORAGE_SETTINGS=data)


def wizard_settings(**kwargs):
    data = {
        'default_position': {'longitude': 37.619055, 'latitude': 55.75321},
        'eda_base_url': 'https://eda.yandex.ru/',
        'lavka_base_url': 'https://lavka.yandex.ru/',
    }

    data.update(kwargs)
    return pytest.mark.config(EATS_CATALOG_WIZARD=data)


def disable_brand_preorder(brand_ids: typing.List[str] = None):
    if brand_ids is None:
        brand_ids = []

    return pytest.mark.config(
        EATS_PARTNER_SLOTS_BRANDS_SETTINGS={'brand_ids': brand_ids},
    )


def extra_legal_info(
        place_id: str,
        date_of_registration: typing.Optional[str] = None,
        consumer_protection_contact: typing.Optional[str] = None,
        retailer_contacts: typing.Optional[str] = None,
        state_register_date: typing.Optional[str] = None,
        state_register_number: typing.Optional[str] = None,
        review_book_location: typing.Optional[str] = None,
        consumer_requests_contacts: typing.Optional[str] = None,
        check_additional_info: typing.Optional[str] = None,
):

    return pytest.mark.config(
        EATS_CATALOG_EXTRA_LEGAL_INFO={
            place_id: {
                'commericial_register_date_of_registration': (
                    date_of_registration
                ),
                'consumer_protection_contact': consumer_protection_contact,
                'retailer_contacts': retailer_contacts,
                'state_register_date': state_register_date,
                'state_register_number': state_register_number,
                'review_book_location': review_book_location,
                'consumer_requests_contacts': consumer_requests_contacts,
                'check_additional_info': check_additional_info,
            },
        },
    )


def max_order_weight(
        brand_weight: typing.Dict[str, int], default_weight: int = 30,
):
    config = brand_weight.copy()
    config['__default_threshold'] = default_weight
    return pytest.mark.config(EDA_CORE_CART_THRESHOLD={'weight': config})


def eda_delivery_price_promo(
        bad_retail_brands=(228,),
        bad_native_brands=(228, 322),
        use_stats_client=True,
):
    return pytest.mark.config(
        EDA_DELIVERY_PRICE_PROMO={
            'bad_retail_brands': bad_retail_brands,
            'bad_native_brands': bad_native_brands,
            'use_stats_client': use_stats_client,
            'use_eater_client': False,
        },
    )


def eats_catalog_offer(
        prolongation: typing.Optional[dict] = None,
        empty_delivery_time_interval=15,
):
    if prolongation is None:
        prolongation = {}
    return pytest.mark.config(
        EATS_CATALOG_OFFER={
            'prolongation': prolongation,
            'empty_delivery_time_interval': empty_delivery_time_interval,
        },
    )


def eats_catalog_rating_meta():
    return pytest.mark.config(
        EATS_CATALOG_RATING_META={
            'low': {
                'icon': {
                    'color': [
                        {'theme': 'light', 'value': '#NO0000'},
                        {'theme': 'dark', 'value': '#NO0000'},
                    ],
                    'url': 'asset://no_rating_star',
                },
                'text': {
                    'color': [
                        {'theme': 'light', 'value': '#NO0000'},
                        {'theme': 'dark', 'value': '#NO0000'},
                    ],
                    'text': 'Мало оценок',
                },
            },
            'new': {
                'icon': {'color': [], 'url': 'asset://rating_star_new'},
                'text': {
                    'color': [
                        {'theme': 'light', 'value': '#NEW000'},
                        {'theme': 'dark', 'value': '#NEW000'},
                    ],
                    'text': 'Новый',
                },
            },
            'regular': {
                'count_description': {'min_count': 201, 'text': '200+'},
                'icon_url': 'asset://rating_star',
                'thresholds': [
                    {
                        'icon_color': [
                            {'theme': 'light', 'value': '#ZERO00'},
                            {'theme': 'dark', 'value': '#ZERO00'},
                        ],
                        'min_rating': 0,
                        'text_color': [
                            {'theme': 'light', 'value': '#ZERO00'},
                            {'theme': 'dark', 'value': '#ZERO00'},
                        ],
                    },
                    {
                        'icon_color': [
                            {'theme': 'light', 'value': '#LOW000'},
                            {'theme': 'dark', 'value': '#LOW000'},
                        ],
                        'min_rating': 4.5,
                        'text_color': [
                            {'theme': 'light', 'value': '#LOW000'},
                            {'theme': 'dark', 'value': '#LOW000'},
                        ],
                    },
                    {
                        'additional_description': 'Хорошо',
                        'icon_color': [
                            {'theme': 'light', 'value': '#GOOD00'},
                            {'theme': 'dark', 'value': '#GOOD00'},
                        ],
                        'min_rating': 4.7,
                        'text_color': [
                            {'theme': 'light', 'value': '#GOOD00'},
                            {'theme': 'dark', 'value': '#GOOD00'},
                        ],
                    },
                    {
                        'additional_description': 'Отлично',
                        'icon_color': [
                            {'theme': 'light', 'value': '#GREAT0'},
                            {'theme': 'dark', 'value': '#GREAT0'},
                        ],
                        'min_rating': 4.9,
                        'text_color': [
                            {'theme': 'light', 'value': '#GREAT0'},
                            {'theme': 'dark', 'value': '#GREAT0'},
                        ],
                    },
                ],
            },
            'top': {
                'icon': {'color': [], 'url': 'asset://flame'},
                'tag': 'top_rating',
                'text': {
                    'color': [
                        {'theme': 'light', 'value': '#TOP000'},
                        {'theme': 'dark', 'value': '#TOP000'},
                    ],
                    'text': 'Рекомендуем',
                },
            },
        },
    )


def ultima_places(
        menu: typing.Optional[dict] = None,
        places: typing.Optional[dict] = None,
):
    if places is None:
        places = {}

    return pytest.mark.config(
        ULTIMA_PLACES={
            'colors': {
                'title': {'dark': '#TTITLE', 'light': '#TTITLE'},
                'delivery': {
                    'text': {'dark': '#DETEXT', 'light': '#DETEXT'},
                    'background': {'dark': '#DEBACK', 'light': '#DEBACK'},
                },
                'info': {
                    'title': {'dark': '#ITITLE', 'light': '#ITITLE'},
                    'description': {'dark': '#IDESCR', 'light': '#IDESCR'},
                },
                'review': {
                    'text': {'dark': '#RETEXT', 'light': '#RETEXT'},
                    'subtext': {'dark': '#RSUBTE', 'light': '#RSUBTE'},
                },
            },
            'header': {
                'image': {
                    'light': 'http://header/light',
                    'dark': 'http://header/dark',
                },
                'button': {
                    'deeplink': {
                        'app': 'eda.yandex://carousel/link',
                        'web': 'http://carousel/link',
                    },
                    'icon_image': {
                        'light': 'http://eda.yandex.ru/light',
                        'dark': 'http://eda.yandex.ru/dark',
                    },
                    'background_color': {
                        'dark': '#RETEXT',
                        'light': '#RETEXT',
                    },
                },
            },
            'places': places,
            'menu': menu,
        },
    )
