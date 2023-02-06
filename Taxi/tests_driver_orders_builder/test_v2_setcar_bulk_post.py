# pylint: disable=too-many-lines

import copy

import pytest

V2_SETCAR_CREATE_URL = '/v2/setcar/bulk'
MOCK_UI = {
    'acceptance_button_params': {
        'bg_color': '#2f5bc7',
        'title': 'Принять',
        'progress_text_color': '#ffffff',
        'text_color': '#ffffff',
    },
    'acceptance_items': [
        {
            'background': {
                'color_day': '#FFFFFF',
                'corner_radius': 'mu_1',
                'type': 'rect',
            },
            'horizontal_divider_type': 'none',
            'items': [
                {
                    'accent': True,
                    'detail_primary_text_color': '#000000',
                    'detail_primary_text_color_night': '#000000',
                    'detail_secondary_text_color': '#000000',
                    'detail_secondary_text_color_night': '#000000',
                    'horizontal_divider_type': 'bottom_icon_gap',
                    'left_tip': {'background_color': '#46B275', 'text': 'А'},
                    'markdown': True,
                    'primary_max_lines': 3,
                    'primary_text_color': '#000000',
                    'primary_text_color_night': '#000000',
                    'secondary_text_color': '#000000',
                    'secondary_text_color_night': '#000000',
                    'title': (
                        '**4 мин** · '
                        '1-й Красногвардейский проезд, 21с1, подъезд 4'
                    ),
                    'type': 'tip_detail',
                },
                {
                    'accent': True,
                    'detail_primary_text_color': '#000000',
                    'detail_primary_text_color_night': '#000000',
                    'detail_secondary_text_color': '#000000',
                    'detail_secondary_text_color_night': '#000000',
                    'horizontal_divider_type': 'bottom_icon_gap',
                    'left_tip': {
                        'background_color': '#242B38',
                        'icon': {'icon_type': 'uber_global'},
                    },
                    'markdown': True,
                    'primary_max_lines': 3,
                    'primary_text_color': '#000000',
                    'primary_text_color_night': '#000000',
                    'secondary_text_color': '#000000',
                    'secondary_text_color_night': '#000000',
                    'title': 'Есенинский бульвар, 3, подъезд 1',
                    'type': 'tip_detail',
                },
                {
                    'accent': True,
                    'detail_primary_text_color': '#000000',
                    'detail_primary_text_color_night': '#000000',
                    'detail_secondary_text_color': '#000000',
                    'detail_secondary_text_color_night': '#000000',
                    'horizontal_divider_type': 'none',
                    'left_tip': {'background_color': '#F25139', 'text': 'Б'},
                    'markdown': True,
                    'padding_type': 'tiny_bottom',
                    'primary_max_lines': 3,
                    'primary_text_color': '#000000',
                    'primary_text_color_night': '#000000',
                    'secondary_text_color': '#000000',
                    'secondary_text_color_night': '#000000',
                    'title': '**12 мин** · ТРЦ Европейский, Выход №1',
                    'type': 'tip_detail',
                },
            ],
            'orientation': 'vertical',
            'padding_type': 'tiny_bottom',
            'type': 'multi_section',
            'use_item_divider_type': False,
        },
        {
            'background': {
                'color_day': '#242B38',
                'corner_radius': 'mu_1',
                'corners_type': 'top',
                'type': 'rect',
            },
            'hint': '2,1 км',
            'hint_color_day': '#FFFFFF',
            'hint_size': 'title_small',
            'horizontal_divider_type': 'none',
            'subtitle': '596 ₽',
            'subtitle_color_day': '#FFFFFF',
            'subtitle_size': 'big',
            'title': 'Безналичная оплата ★ 5',
            'title_color_day': '#A4A4AC',
            'title_icon': 'cashless',
            'title_icon_gravity': 'left',
            'type': 'header',
        },
        {
            'background': {'color_day': '#242B38', 'type': 'rect'},
            'horizontal_divider_type': 'none',
            'is_align_center': True,
            'tags': [],
            'type': 'tag_group',
            'wrap_before_indexes': [1],
        },
    ],
}

MOCK_UI_TAXIMETER = {
    'accept_toolbar_params': {
        'title': '2,1 км · 4 мин',
        'subtitle': 'Дальняя подача',
    },
    'acceptance_button_params': {
        'bg_color': '#f2e15c',
        'progress_text_color': '#ffffff',
        'subtitle': '',
        'text_color': '#21201f',
        'title': 'Принять',
    },
    'acceptance_items': [
        {
            'type': 'double_section',
            'horizontal_divider_type': 'full',
            'vertical_divider_type': 'full',
            'left': {
                'type': 'icon_detail',
                'reverse': True,
                'horizontal_divider_type': 'full',
                'accent_title': True,
                'title': 'Активность',
                'subtitle': '0',
                'left_icon': {
                    'icon_type': 'activity',
                    'icon_size': 'large',
                    'tint_color': '#d8d8d8',
                },
                'primary_text_color': '#9e9b98',
            },
            'right': {
                'type': 'icon_detail',
                'reverse': True,
                'horizontal_divider_type': 'full',
                'accent_title': True,
                'title': 'Цена',
                'subtitle': '× 1',
                'left_icon': {
                    'icon_type': 'surge',
                    'icon_size': 'large',
                    'tint_color': '#d8d8d8',
                },
                'primary_text_color': '#9e9b98',
            },
        },
        {
            'type': 'detail',
            'horizontal_divider_type': 'full',
            'markdown': True,
            'subtitle': 'Рейтинг пассажира',
            'subdetail': '**5**',
            'right_icon': 'star',
            'reverse': True,
        },
        {
            'type': 'default',
            'title': 'Откуда:',
            'subtitle': '1-й Красногвардейский проезд, 21с1, подъезд 4',
            'reverse': True,
            'horizontal_divider_type': 'full',
        },
        {
            'type': 'default',
            'title': 'Остановка:',
            'subtitle': 'Есенинский бульвар, 3, подъезд 1',
            'reverse': True,
            'horizontal_divider_type': 'full',
        },
        {
            'type': 'default',
            'title': 'Куда:',
            'subtitle': 'ТРЦ Европейский, Выход №1',
            'reverse': True,
            'horizontal_divider_type': 'full',
        },
    ],
}

MOCK_UI_ENG = {
    'acceptance_items': [
        {
            'type': 'multi_section',
            'horizontal_divider_type': 'none',
            'padding_type': 'tiny_bottom',
            'background': {
                'type': 'rect',
                'color_day': '#FFFFFF',
                'corner_radius': 'mu_1',
            },
            'use_item_divider_type': False,
            'items': [
                {
                    'type': 'tip_detail',
                    'accent': True,
                    'horizontal_divider_type': 'bottom_icon_gap',
                    'markdown': True,
                    'title': (
                        '**4 min** · '
                        'Moscow, 1-й Krasnogvardeyski drive, 21/1, подъезд 4'
                    ),
                    'primary_text_color': '#000000',
                    'primary_text_color_night': '#000000',
                    'secondary_text_color': '#000000',
                    'secondary_text_color_night': '#000000',
                    'detail_primary_text_color': '#000000',
                    'detail_primary_text_color_night': '#000000',
                    'detail_secondary_text_color': '#000000',
                    'detail_secondary_text_color_night': '#000000',
                    'primary_max_lines': 3,
                    'left_tip': {'background_color': '#46B275', 'text': 'А'},
                },
                {
                    'type': 'tip_detail',
                    'accent': True,
                    'horizontal_divider_type': 'bottom_icon_gap',
                    'markdown': True,
                    'title': 'Moscow, Esenin blvd 3, porch 1',
                    'primary_text_color': '#000000',
                    'primary_text_color_night': '#000000',
                    'secondary_text_color': '#000000',
                    'secondary_text_color_night': '#000000',
                    'detail_primary_text_color': '#000000',
                    'detail_primary_text_color_night': '#000000',
                    'detail_secondary_text_color': '#000000',
                    'detail_secondary_text_color_night': '#000000',
                    'primary_max_lines': 3,
                    'left_tip': {
                        'icon': {'icon_type': 'uber_global'},
                        'background_color': '#242B38',
                    },
                },
                {
                    'type': 'tip_detail',
                    'accent': True,
                    'horizontal_divider_type': 'none',
                    'markdown': True,
                    'padding_type': 'tiny_bottom',
                    'title': '**12 min** · Moscow, Evropeyski mall, exit №1',
                    'primary_text_color': '#000000',
                    'primary_text_color_night': '#000000',
                    'secondary_text_color': '#000000',
                    'secondary_text_color_night': '#000000',
                    'detail_primary_text_color': '#000000',
                    'detail_primary_text_color_night': '#000000',
                    'detail_secondary_text_color': '#000000',
                    'detail_secondary_text_color_night': '#000000',
                    'primary_max_lines': 3,
                    'left_tip': {'background_color': '#F25139', 'text': 'Б'},
                },
            ],
            'orientation': 'vertical',
        },
        {
            'type': 'header',
            'horizontal_divider_type': 'none',
            'background': {
                'type': 'rect',
                'color_day': '#242B38',
                'corner_radius': 'mu_1',
                'corners_type': 'top',
            },
            'hint': '2.1 km',
            'hint_color_day': '#FFFFFF',
            'hint_size': 'title_small',
            'subtitle': '596 ₽',
            'subtitle_color_day': '#FFFFFF',
            'subtitle_size': 'big',
            'title': 'Безналичная оплата ★ 5',
            'title_color_day': '#A4A4AC',
            'title_icon': 'cashless',
            'title_icon_gravity': 'left',
        },
        {
            'type': 'tag_group',
            'horizontal_divider_type': 'none',
            'background': {'type': 'rect', 'color_day': '#242B38'},
            'wrap_before_indexes': [1],
            'tags': [],
            'is_align_center': True,
        },
    ],
    'acceptance_button_params': {
        'bg_color': '#2f5bc7',
        'title': 'Принять',
        'progress_text_color': '#ffffff',
        'text_color': '#ffffff',
    },
}

MOCK_UI_ENG_ISR = {
    'acceptance_items': [
        {
            'type': 'multi_section',
            'horizontal_divider_type': 'none',
            'padding_type': 'tiny_bottom',
            'background': {
                'type': 'rect',
                'color_day': '#FFFFFF',
                'corner_radius': 'mu_1',
            },
            'use_item_divider_type': False,
            'items': [
                {
                    'type': 'tip_detail',
                    'accent': True,
                    'horizontal_divider_type': 'bottom_icon_gap',
                    'markdown': True,
                    'title': (
                        '**4 min** · '
                        '1-й Krasnogvardeyski drive, 21/1, подъезд 4'
                    ),
                    'primary_text_color': '#000000',
                    'primary_text_color_night': '#000000',
                    'secondary_text_color': '#000000',
                    'secondary_text_color_night': '#000000',
                    'detail_primary_text_color': '#000000',
                    'detail_primary_text_color_night': '#000000',
                    'detail_secondary_text_color': '#000000',
                    'detail_secondary_text_color_night': '#000000',
                    'primary_max_lines': 3,
                    'left_tip': {'background_color': '#46B275', 'text': 'А'},
                },
                {
                    'type': 'tip_detail',
                    'accent': True,
                    'horizontal_divider_type': 'bottom_icon_gap',
                    'markdown': True,
                    'title': 'Esenin blvd 3, porch 1',
                    'primary_text_color': '#000000',
                    'primary_text_color_night': '#000000',
                    'secondary_text_color': '#000000',
                    'secondary_text_color_night': '#000000',
                    'detail_primary_text_color': '#000000',
                    'detail_primary_text_color_night': '#000000',
                    'detail_secondary_text_color': '#000000',
                    'detail_secondary_text_color_night': '#000000',
                    'primary_max_lines': 3,
                    'left_tip': {
                        'icon': {'icon_type': 'uber_global'},
                        'background_color': '#242B38',
                    },
                },
                {
                    'type': 'tip_detail',
                    'accent': True,
                    'horizontal_divider_type': 'none',
                    'markdown': True,
                    'padding_type': 'tiny_bottom',
                    'title': '**12 min** · Evropeyski mall, exit №1',
                    'primary_text_color': '#000000',
                    'primary_text_color_night': '#000000',
                    'secondary_text_color': '#000000',
                    'secondary_text_color_night': '#000000',
                    'detail_primary_text_color': '#000000',
                    'detail_primary_text_color_night': '#000000',
                    'detail_secondary_text_color': '#000000',
                    'detail_secondary_text_color_night': '#000000',
                    'primary_max_lines': 3,
                    'left_tip': {'background_color': '#F25139', 'text': 'Б'},
                },
            ],
            'orientation': 'vertical',
        },
        {
            'type': 'header',
            'horizontal_divider_type': 'none',
            'background': {
                'type': 'rect',
                'color_day': '#242B38',
                'corner_radius': 'mu_1',
                'corners_type': 'top',
            },
            'hint': '2.1 km',
            'hint_color_day': '#FFFFFF',
            'hint_size': 'title_small',
            'subtitle': '596 ',
            'subtitle_color_day': '#FFFFFF',
            'subtitle_size': 'big',
            'title': 'Безналичная оплата ★ 5',
            'title_color_day': '#A4A4AC',
            'title_icon': 'cashless',
            'title_icon_gravity': 'left',
        },
        {
            'type': 'tag_group',
            'horizontal_divider_type': 'none',
            'background': {'type': 'rect', 'color_day': '#242B38'},
            'wrap_before_indexes': [1],
            'tags': [],
            'is_align_center': True,
        },
    ],
    'acceptance_button_params': {
        'bg_color': '#2f5bc7',
        'title': 'Принять',
        'progress_text_color': '#ffffff',
        'text_color': '#ffffff',
    },
}

MOCK_UI_TAXIMETER_ANTISURGE_SECTION = {
    'type': 'icon_detail',
    'reverse': True,
    'horizontal_divider_type': 'full',
    'accent_title': True,
    'subtitle': 'Цена снижена',
    'left_icon': {
        'icon_size': 'large',
        'icon_type': 'anti_surge',
        'tint_color': '#5c5a57',
    },
    'primary_text_color': '#5c5a57',
}

MOCK_UI_TAXIMETER_LONG_ORDER = {
    'type': 'default',
    'reverse': True,
    'title': '12 мин, 1.3 км',
    'subtitle': 'Долгая поездка',
}


ADDRESS_TO_ENG = {
    'Street': 'Moscow, Evropeyski mall, exit №1',
    'Lat': 55.74553754198694,
    'Lon': 37.56530594673405,
    'Region': '',
    'Order': 2,
    'ArrivalDistance': 20,
}

ADDRESS_TO_ENG_ISR = {
    'Street': 'Evropeyski mall, exit №1',
    'Lat': 55.74553754198694,
    'Lon': 37.56530594673405,
    'Region': '',
    'Order': 2,
    'ArrivalDistance': 20,
}

ADDRESS_TO = {
    'Order': 2,
    'ArrivalDistance': 20.0,
    'Street': 'ТРЦ Европейский, Выход №1',
    'Region': '',
    'Lat': 55.74553754198694,
    'Lon': 37.56530594673405,
}

ADDRESS_FROM_ENG = {
    'Street': 'Moscow, 1-й Krasnogvardeyski drive, 21/1, подъезд 4',
    'Lat': 55.75000699999999,
    'Lon': 37.5334785,
    'ApartmentInfo': '4 подъезд, 5 этаж, 33 квартира. Код от домофона: 67.',
    'Comment': 'Код от подъезда/домофона: 67.\nКлиент: Герман',
    'Region': '',
    'Porch': '4',
}

ADDRESS_FROM_ENG_ISR = {
    'Street': '1-й Krasnogvardeyski drive, 21/1, подъезд 4',
    'Lat': 55.75000699999999,
    'Lon': 37.5334785,
    'ApartmentInfo': '4 подъезд, 5 этаж, 33 квартира. Код от домофона: 67.',
    'Comment': 'Код от подъезда/домофона: 67.\nКлиент: Герман',
    'Region': '',
    'Porch': '4',
}

ADDRESS_FROM = {
    'Street': '1-й Красногвардейский проезд, 21с1, подъезд 4',
    'Porch': '4',
    'Region': '',
    'Lat': 55.75000699999999,
    'Lon': 37.5334785,
    'ApartmentInfo': '4 подъезд, 5 этаж, 33 квартира. Код от домофона: 67.',
    'Comment': 'Код от подъезда/домофона: 67.\nКлиент: Герман',
}

ROUTE_POINT_ENG = {
    'Street': 'Moscow, Esenin blvd 3, porch 1',
    'Lat': 55.745537,
    'Lon': 37.565306,
    'Region': '',
    'Order': 1,
    'ArrivalDistance': 20,
}

ROUTE_POINT_ENG_ISR = {
    'Street': 'Esenin blvd 3, porch 1',
    'Lat': 55.745537,
    'Lon': 37.565306,
    'Region': '',
    'Order': 1,
    'ArrivalDistance': 20,
}

ROUTE_POINT = {
    'Order': 1,
    'ArrivalDistance': 20,
    'Street': 'Есенинский бульвар, 3, подъезд 1',
    'Region': '',
    'Lat': 55.745537,
    'Lon': 37.565306,
}

MOCK_TAXIMETER_SETTINGS = {
    'showing_payment_type_for': [2, 3, 5, 7],
    'showing_surge_for': [1, 2, 3],
    'status_change_delays': {'1': 0, '3': 0, '7': 3, '2': 0, '5': 3},
    'driver_mode_type': 'orders',
    'hide_cost_widget': True,
    'show_user_cost': False,
    # 'taximeter_pricing_version_config': {
    #     'primary_pricing_version': 'v2',
    #     'secondary_pricing_enabled': False,
    # },
}

BASE_PRICE = {
    'user': {
        'boarding': 199.0,
        'destination_waiting': 0.0,
        'distance': 85.34953829383852,
        'requirements': 0.0,
        'time': 115.59768651429248,
        'transit_waiting': 0.0,
        'waiting': 0.0,
    },
    'driver': {
        'boarding': 199.0,
        'destination_waiting': 0.0,
        'distance': 85.34953829383852,
        'requirements': 0.0,
        'time': 115.59768651429248,
        'transit_waiting': 0.0,
        'waiting': 0.0,
    },
}

PAID_SUPPLY_FIXED_PRICE = {'max_distance': 501, 'price': 398.0, 'show': False}

PAID_SUPPLY_DRIVER_FIXED_PRICE = {
    'max_distance': 501,
    'price': 696.0,
    'show': False,
}

PAID_SUPPLY_TOOLBAR_PARAMS = {
    'subtitle': '696 ₽ · 2.6 км',
    'title': 'Безналичная оплата',
}

PAID_SUPPLY_TOOLBAR_PARAMS_TAXIMETER = {
    'title': '2,1 км · 4 мин',
    'subtitle': 'Платная подача',
}

PAID_SUPPLY_ACCEPTANCE_BUTTON_PARAMS = {
    'bg_color': '#0062c6',
    'progress_text_color': '#ffffff',
    'subtitle': '',
    'text_color': '#ffffff',
    'title': 'Принять',
}

PAID_SUPPLY_SURGE_SECTION = {
    'accent_title': True,
    'horizontal_divider_type': 'full',
    'left_icon': {
        'icon_size': 'large',
        'icon_type': 'surge',
        'tint_color': '#0596fa',
    },
    'primary_text_color': '#0062c6',
    'reverse': True,
    'subtitle': '+100 ₽',
    'title': 'Цена',
    'type': 'icon_detail',
}

PAID_SUPPLY_TAGS = [
    {
        'color': '#5CD691',
        'icon': 'cash',
        'text': 'Платная подача 100 ₽',
        'text_size': 'text',
    },
]

PAID_SUPPLY_TAGS_ISR = [
    {
        'color': '#5CD691',
        'icon': 'cash',
        'text': 'Платная подача 100 ',
        'text_size': 'text',
    },
]

ANTISURGE_ACCEPTANCE_BUTTON_PARAMS = {
    'bg_color': '#5c5a57',
    'progress_text_color': '#ffffff',
    'subtitle': '596 ₽',
    'text_color': '#ffffff',
    'title': 'Принять',
}

MOCK_TARIFFSV2 = {
    'is_fallback_pricing': False,
    'driver': {
        'category_prices_id': 'c/168c3ba42916455ca95cbbdd96ea6678',
        'geoareas': ['g/2bab7eff1aa848b681370b2bd83cfbf9'],
    },
    'user': {
        'category_prices_id': 'c/168c3ba42916455ca95cbbdd96ea6678',
        'geoareas': ['g/2bab7eff1aa848b681370b2bd83cfbf9'],
    },
}

MOCK_MULTIOFFER = {
    'id': '01234567-89ab-cdef-0123-456789abcdef',
    'is_accepted': False,
    'start_date': '2020-12-01T20:12:36.000000Z',
    'timeout': 15,
    'play_timeout': 20,
}

MOCK_LEGACY_EXPERIMENTS = [
    'direct_assignment',
    'taximeter_complete',
    'open_near_point_a',
    'use_lbs_for_waiting_status',
]


@pytest.mark.parametrize(
    'body, result',
    [
        (
            {
                'order_id': '123',
                'drivers': [
                    {
                        'driver_profile_id': 'driver1',
                        'park_id': 'park1',
                        'alias_id': 'alias_id_1',
                    },
                    {
                        'driver_profile_id': 'driver2',
                        'park_id': 'park2',
                        'alias_id': 'alias_id_2',
                    },
                    {
                        'driver_profile_id': 'driver3',
                        'park_id': 'park3',
                        'alias_id': 'alias_id_3',
                    },
                    {
                        'driver_profile_id': 'driver4',
                        'park_id': 'park4',
                        'alias_id': 'alias_id_4',
                    },
                ],
            },
            {
                'setcars': [
                    {
                        'driver': {
                            'alias_id': 'alias_id_1',
                            'driver_profile_id': 'driver1',
                            'park_id': 'park1',
                        },
                        'setcar': {
                            'internal': {
                                'order_id': 'fe8250a5c1324bceb162b71f64e40ad7',
                                'payment_type': 'card',
                            },
                            'id': 'alias_id_1',
                            'agg': 'aggregator1_guid',
                            'provider': 2,
                            'clid': 'aggregator1_clid',
                            'source': 'service',
                            'route_distance': 2523,
                            'pickup_distance_type': 'long',
                            'notification': {'sound': 'new_order.wav'},
                            'number': 1,
                            'show_address': True,
                            'experiments': MOCK_LEGACY_EXPERIMENTS,
                            'address_from': ADDRESS_FROM,
                            'address_to': ADDRESS_TO,
                            'route_points': [ROUTE_POINT],
                            'pay_type': 1,
                            'autocancel': MOCK_MULTIOFFER['timeout'],
                            'date_create': '2020-12-01T20:12:36.000000Z',
                            'date_drive': '2020-12-01T20:17:36.000000Z',
                            'date_last_change': '2020-12-01T20:12:36.000000Z',
                            'requirement_list': [],
                            'route_time': '2020-12-01T20:17:36.000000Z',
                            'driver_fixed_price': {
                                'max_distance': 501,
                                'price': 596.0,
                                'show': False,
                            },
                            'fixed_price': {
                                'max_distance': 501,
                                'price': 298.0,
                                'show': False,
                            },
                            'chain': {
                                'dist': 2023,
                                'prev_lat': 51.662082,
                                'prev_lon': 39.207141,
                                'time': 201,
                            },
                            'driver_mode_info': {
                                'display_mode': 'orders',
                                'display_profile': 'orders',
                            },
                            'has_online_cashbox': True,
                            'ui': MOCK_UI,
                            'base_price': BASE_PRICE,
                            'taximeter_settings': MOCK_TAXIMETER_SETTINGS,
                            'tariffs_v2': MOCK_TARIFFSV2,
                            'multioffer': MOCK_MULTIOFFER,
                            'driver_tags': ['tag1', 'tag2'],
                            'kind': 1,
                            'client_geo_sharing': {
                                'track_id': '40d4167a527340caac75e55040bfd49e',
                            },
                            'car_name': 'Pagani Zonda R',
                            'car_number': 'X666XXX666',
                            'driver_signal': 'rogue_one',
                            'car_franchise': True,
                            'car_id': '13e21f1abac24eb78f8ffaf8db872a28',
                            'driver_id': 'driver1',
                            'driver_name': 'Иванов Иван Иванович',
                            'type_name': 'Яндекс.Безналичный',
                            'passager_count': 1,
                            'waiting_mode': 'regular',
                        },
                    },
                    {
                        'driver': {
                            'alias_id': 'alias_id_2',
                            'driver_profile_id': 'driver2',
                            'park_id': 'park2',
                        },
                        'setcar': {
                            'internal': {
                                'order_id': 'fe8250a5c1324bceb162b71f64e40ad7',
                                'payment_type': 'card',
                            },
                            'id': 'alias_id_2',
                            'agg': 'aggregator2_guid',
                            'provider': 2,
                            'clid': 'aggregator2_clid',
                            'source': 'service',
                            'requirement_list': [],
                            'route_distance': 2523,
                            'pickup_distance_type': 'long',
                            'notification': {'sound': 'new_order.wav'},
                            'number': 1,
                            'show_address': False,
                            'experiments': MOCK_LEGACY_EXPERIMENTS,
                            'address_from': ADDRESS_FROM,
                            'address_to': ADDRESS_TO,
                            'route_points': [ROUTE_POINT],
                            'pay_type': 1,
                            'autocancel': MOCK_MULTIOFFER['timeout'],
                            'date_create': '2020-12-01T20:12:36.000000Z',
                            'date_drive': '2020-12-01T20:17:36.000000Z',
                            'date_last_change': '2020-12-01T20:12:36.000000Z',
                            'route_time': '2020-12-01T20:17:36.000000Z',
                            'driver_fixed_price': {
                                'max_distance': 501,
                                'price': 596.0,
                                'show': False,
                            },
                            'fixed_price': {
                                'max_distance': 501,
                                'price': 298.0,
                                'show': False,
                            },
                            'chain': {
                                'dist': 2023,
                                'prev_lat': 51.662082,
                                'prev_lon': 39.207141,
                                'time': 201,
                            },
                            'driver_mode_info': {
                                'display_mode': 'orders',
                                'display_profile': 'orders',
                            },
                            'driver_points_info': {
                                'long_wait_cancel': 0.0,
                                'long_wait_cancel_title': (
                                    'Укажите причину отмены'
                                ),
                            },
                            'has_online_cashbox': False,
                            'ui': MOCK_UI_TAXIMETER,
                            'base_price': BASE_PRICE,
                            'multioffer': MOCK_MULTIOFFER,
                            'taximeter_settings': MOCK_TAXIMETER_SETTINGS,
                            'tariffs_v2': MOCK_TARIFFSV2,
                            'driver_tags': ['tag1', 'tag3'],
                            'kind': 1,
                            'Reposition': True,
                            'client_geo_sharing': {
                                'track_id': '40d4167a527340caac75e55040bfd49e',
                            },
                            'car_name': 'Pagani Zonda R',
                            'car_number': 'X666XXX666',
                            'driver_signal': 'rogue_one',
                            'car_franchise': True,
                            'car_id': '13e21f1abac24eb78f8ffaf8db872a28',
                            'driver_id': 'driver2',
                            'driver_name': 'Иванов Иван Иванович',
                            'type_name': 'Яндекс.Безналичный',
                            'passager_count': 1,
                            'waiting_mode': 'regular',
                        },
                    },
                    {
                        'driver': {
                            'alias_id': 'alias_id_3',
                            'driver_profile_id': 'driver3',
                            'park_id': 'park3',
                        },
                        'setcar': {
                            'internal': {
                                'order_id': 'fe8250a5c1324bceb162b71f64e40ad7',
                                'payment_type': 'card',
                            },
                            'id': 'alias_id_3',
                            'agg': 'aggregator2_guid',
                            'provider': 2,
                            'clid': 'aggregator2_clid',
                            'source': 'service',
                            'requirement_list': [],
                            'route_distance': 2523,
                            'pickup_distance_type': 'long',
                            'notification': {'sound': 'new_order.wav'},
                            'number': 1,
                            'show_address': True,
                            'experiments': MOCK_LEGACY_EXPERIMENTS,
                            'address_from': ADDRESS_FROM_ENG,
                            'address_to': ADDRESS_TO_ENG,
                            'route_points': [ROUTE_POINT_ENG],
                            'pay_type': 1,
                            'autocancel': MOCK_MULTIOFFER['timeout'],
                            'date_create': '2020-12-01T20:12:36.000000Z',
                            'date_drive': '2020-12-01T20:17:36.000000Z',
                            'date_last_change': '2020-12-01T20:12:36.000000Z',
                            'route_time': '2020-12-01T20:17:36.000000Z',
                            'driver_fixed_price': {
                                'max_distance': 501,
                                'price': 596.0,
                                'show': False,
                            },
                            'fixed_price': {
                                'max_distance': 501,
                                'price': 298.0,
                                'show': False,
                            },
                            'chain': {
                                'dist': 2023,
                                'prev_lat': 51.662082,
                                'prev_lon': 39.207141,
                                'time': 201,
                            },
                            'driver_mode_info': {
                                'display_mode': 'orders',
                                'display_profile': 'orders',
                            },
                            'has_online_cashbox': False,
                            'ui': MOCK_UI_ENG,
                            'base_price': BASE_PRICE,
                            'multioffer': MOCK_MULTIOFFER,
                            'taximeter_settings': MOCK_TAXIMETER_SETTINGS,
                            'tariffs_v2': MOCK_TARIFFSV2,
                            'driver_tags': ['tag1', 'tag3'],
                            'kind': 1,
                            'client_geo_sharing': {
                                'track_id': '40d4167a527340caac75e55040bfd49e',
                            },
                            'car_name': 'Pagani Zonda R',
                            'car_number': 'X666XXX666',
                            'driver_signal': 'rogue_one',
                            'car_franchise': True,
                            'car_id': '13e21f1abac24eb78f8ffaf8db872a28',
                            'driver_id': 'driver3',
                            'driver_name': 'Иванов Иван Иванович',
                            'type_name': 'Яндекс.Безналичный',
                            'passager_count': 1,
                            'waiting_mode': 'regular',
                        },
                    },
                    {
                        'driver': {
                            'alias_id': 'alias_id_4',
                            'driver_profile_id': 'driver4',
                            'park_id': 'park4',
                        },
                        'setcar': {
                            'internal': {
                                'order_id': 'fe8250a5c1324bceb162b71f64e40ad7',
                                'payment_type': 'card',
                            },
                            'id': 'alias_id_4',
                            'agg': 'aggregator2_guid',
                            'provider': 2,
                            'clid': 'aggregator2_clid',
                            'source': 'service',
                            'requirement_list': [],
                            'route_distance': 2523,
                            'pickup_distance_type': 'long',
                            'notification': {'sound': 'new_order.wav'},
                            'number': 1,
                            'show_address': True,
                            'experiments': MOCK_LEGACY_EXPERIMENTS,
                            'address_from': ADDRESS_FROM_ENG_ISR,
                            'address_to': ADDRESS_TO_ENG_ISR,
                            'route_points': [ROUTE_POINT_ENG_ISR],
                            'pay_type': 1,
                            'autocancel': MOCK_MULTIOFFER['timeout'],
                            'date_create': '2020-12-01T20:12:36.000000Z',
                            'date_drive': '2020-12-01T20:17:36.000000Z',
                            'date_last_change': '2020-12-01T20:12:36.000000Z',
                            'route_time': '2020-12-01T20:17:36.000000Z',
                            'driver_fixed_price': {
                                'max_distance': 501,
                                'price': 596.0,
                                'show': False,
                            },
                            'fixed_price': {
                                'max_distance': 501,
                                'price': 298.0,
                                'show': False,
                            },
                            'chain': {
                                'dist': 2023,
                                'prev_lat': 51.662082,
                                'prev_lon': 39.207141,
                                'time': 201,
                            },
                            'driver_mode_info': {
                                'display_mode': 'orders',
                                'display_profile': 'orders',
                            },
                            'has_online_cashbox': False,
                            'ui': MOCK_UI_ENG_ISR,
                            'base_price': BASE_PRICE,
                            'multioffer': MOCK_MULTIOFFER,
                            'taximeter_settings': MOCK_TAXIMETER_SETTINGS,
                            'tariffs_v2': MOCK_TARIFFSV2,
                            'driver_tags': ['tag1', 'tag3'],
                            'kind': 1,
                            'client_geo_sharing': {
                                'track_id': '40d4167a527340caac75e55040bfd49e',
                            },
                            'car_name': 'Pagani Zonda R',
                            'car_number': 'X666XXX666',
                            'driver_signal': 'rogue_one',
                            'car_franchise': True,
                            'car_id': '13e21f1abac24eb78f8ffaf8db872a28',
                            'driver_id': 'driver4',
                            'driver_name': 'Иванов Иван Иванович',
                            'type_name': 'Яндекс.Безналичный',
                            'passager_count': 1,
                            'waiting_mode': 'regular',
                        },
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'test_tags',
    [
        '',
        'paid_supply',
        'is_explicit_antisurge',
        'show_destination_by_loyalty',
        'show_destination_by_loyalty_fallback',
        'show_destination_by_activity_and_tags',
        'show_destination_by_experiment3',
        'show_destination_by_adverse',
        'show_destination_by_activity_and_old_experiment',
        'show_destination_by_long_order',
        'show_destination_by_tariff',
    ],
)
@pytest.mark.driver_tags_match(
    dbid='park1', uuid='driver1', tags=['tag1', 'tag2'],
)
@pytest.mark.driver_tags_match(
    dbid='park3', uuid='driver3', tags=['tag1', 'tag3'],
)
@pytest.mark.driver_tags_match(
    dbid='park4', uuid='driver4', tags=['tag1', 'tag3'],
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='driver_orders_builder_settings',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={
        'enable_replace_driver_points_info': True,
        'enable_driver_tags_request': True,
        'enable_driver_profiles_request': True,
        'enable_multioffer_request': True,
        'enable_candidate_meta_request': True,
        'enable_cashbox_integration_request': True,
        'enable_driver_mode_request': True,
        'enable_park_aggregator_redis_source': True,
    },
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='setcar_uberdriver_destination',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='setcar_uberdriver_price',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='setcar_uberdriver_payment_type',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=False,
    name='passenger_ratings_for_drivers',
    consumers=['driver-orders-builder/setcar'],
    clauses=[],
    default_value={'enabled': True},
)
@pytest.mark.experiments3()
@pytest.mark.now('2020-12-01T23:12:36+03:00')
async def test_create_v2_setcar_bulk(
        mockserver,
        taxi_driver_orders_builder,
        taxi_driver_orders_builder_monitor,
        taxi_config,
        experiments3,
        tariff_settings,
        parks,
        redis_store,
        load_json,
        test_tags,
        body,
        result,
        order_proc,
):
    exp3_value = (
        'tag1'
        if 'show_destination_by_experiment3' in test_tags
        else 'NOT_A_TAG'
    )
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='driver_orders_builder_show_destination_by_activity_and_tags',
        consumers=['driver-orders-builder/setcar'],
        default_value={'show': False},
        clauses=[
            {
                'title': 'Show destination by tags',
                'value': {'show': True},
                'enabled': True,
                'extension_method': 'replace',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {'arg_name': 'driver_tags'},
                                'type': 'not_null',
                            },
                            {
                                'init': {
                                    'predicates': [
                                        {
                                            'init': {
                                                'arg_name': 'driver_tags',
                                                'set_elem_type': 'string',
                                                'value': exp3_value,
                                            },
                                            'type': 'contains',
                                        },
                                    ],
                                },
                                'type': 'any_of',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
            },
        ],
    )
    taxi_config.set_values(
        {
            'TAXIMETER_VERSION_SETTINGS_BY_BUILD': {
                '__default__': {'feature_support': {'detail_tip': '9.00'}},
            },
            'EXPLICIT_ANTISURGE_SETTINGS': {
                '__default__': {
                    'HIDE_DEST': False,
                    'MIN_ABS_GAIN': 20,
                    'MIN_REL_GAIN': 0.1,
                    'MIN_SURGE_B': 10,
                    'OFFER_TIMEOUT': 25,
                    'SHOW_FIXED_PRICE': True,
                    'SKIP_FIELDS': 'rnop',
                },
            },
            'LOYALTY_CHECK_POINT_B': True,
            'LOYALTY_FALLBACK_POINT_B': (
                'show_destination_by_loyalty_fallback' in test_tags
            ),
            'DRIVER_REVEAL_CHECK_POINT_B_BY_TAGS': True,
            'DRIVER_REVEAL_POINT_B_BY_ACTIVITY_AND_TAGS': {
                '__default__': {
                    'activity': (
                        70
                        if 'show_destination_by_activity_and_tags' in test_tags
                        else 100
                    ),
                    'allowing_tags': ['tag1'],
                    'blocking_tags': [],
                },
            },
            'ADVERSE_ZONES': {
                'moscow': {
                    'pushkino': {'show_destination': True, 'skip_fields': ''},
                },
            },
            'REVEAL_DESTINATION_TO_DRIVER': {
                'moscow': {
                    'min_driver_points': (
                        70
                        if 'show_destination_by_activity_and_old_experiment'
                        in test_tags
                        else 100
                    ),
                },
            },
            'LONG_TRIP_SHOW_DESTINATION': {
                '__default__': {
                    '__default__': (
                        'show_destination_by_long_order' in test_tags
                    ),
                },
            },
            'LONG_TRIP_CRITERIA': {
                '__default__': {
                    '__default__': {
                        'apply': 'either',
                        'distance': (
                            100
                            if 'show_destination_by_long_order' in test_tags
                            else 5000
                        ),
                        'duration': 2400,
                    },
                },
            },
            'TAXIMETER_SHOW_SURGE_DRIVER_BY_STATUS': {
                '__default__': {
                    'show_for_statuses': ['assigned', 'driving', 'waiting'],
                },
            },
            'TAXIMETER_SHOW_TIME_DELAY': {
                '__default__': {
                    '__default__': {
                        'assigned': 0,
                        'complete': 3,
                        'driving': 0,
                        'transporting': 3,
                        'waiting': 0,
                    },
                },
            },
            'TAXIMETER_DRIVERCOST_HIDE': {
                '__default__': {
                    'enable': True,
                    'fixed_price': False,
                    'hide_plate': False,
                    'hide_widget': True,
                    'payment_types': [],
                },
            },
            'TAXIMETER_ADDRESS_SHORTTEXT_FORMAT': {
                '__default__': '{locality}, {short_text}',
                'arm': '{locality}, {short_text}',
                'isr': '{locality}, {short_text}',
            },
        },
    )
    parks.set_aggregators_id(
        {
            'park1': 'aggregator1',
            'park2': 'aggregator2',
            'park3': 'aggregator2',
            'park4': 'aggregator2',
        },
    )
    parks.set_countries({'park4': 'isr'})
    redis_store.hmset(
        'Aggregator:YandexClid', {'aggregator2_clid': 'aggregator2_guid'},
    )

    if 'show_destination_by_tariff' in test_tags:
        tariff_settings.data[0]['hide_dest_for_driver_by_class'][
            'econom'
        ] = False

    @mockserver.json_handler(
        '/contractor-orders-multioffer/internal/v2/multioffer/state',
    )
    def _state(request):
        result = {
            'multioffer_id': '01234567-89ab-cdef-0123-456789abcdef',
            'state': 'chosen_candidate',
            'updated_at': '2020-02-07T19:45:00.922+00:00',
            'timeout': 15,
            'play_timeout': 20,
            'candidate': {
                'id': 'blabla',
                'dbid': 'blablabla',
                'unique_driver_id': 'driver_unique_id',
                'alias_id': 'bla',
                'in_extended_radius': 'paid_supply' in test_tags,
                'tariff_info': {'currency': 'RUB', 'category_name': 'econom'},
                'route_info': {
                    'approximate': False,
                    'distance': 2523,
                    'time': 300,
                },
                'chain_info': {
                    'destination': [39.207141, 51.662082],
                    'left_time': 99,
                    'left_dist': 500,
                    'order_id': 'f3ae2a04966035119c3ea83c8d0197ae',
                },
                'position': [37.5653059, 55.745537],
                'classes': ['econom'],
                'driver_metrics': {
                    'id': '611413e4257851004e1d0780',
                    'type': 'dm_service',
                    'activity': 80,
                    'dispatch': 'long',
                    'properties': [
                        'lookup_mode_multioffer',
                        'dispatch_medium',
                    ],
                    'activity_blocking': {
                        'duration_sec': 3600,
                        'activity_threshold': 11,
                    },
                    'activity_prediction': {},
                },
                'taximeter_version': '8.8',
                'car': {'dbcar_id': '13e21f1abac24eb78f8ffaf8db872a28'},
            },
        }

        if request.json['driver_profile_id'] == 'driver2':
            result['candidate']['metadata'] = {
                'reposition': {'mode': 'highway to hell'},
            }
            result['candidate']['tags'] = ['tag1', 'tag3']

        return result

    @mockserver.json_handler('/candidate-meta/v1/candidate/meta/get')
    def _mock_candidate_meta(request):
        return {'metadata': {}}

    @mockserver.json_handler('/loyalty/service/loyalty/v1/rewards')
    def _mock_loyaly(request):
        if 'show_destination_by_loyalty_fallback' in test_tags:
            return mockserver.make_response(status=500)
        return {
            'matched_driver_rewards': {
                'point_b': {
                    'show_point_b': 'show_destination_by_loyalty' in test_tags,
                    'lock_reasons': {},
                },
            },
        }

    order_proc.set_file(load_json, 'order_core_response1.json')
    order_proc.order_proc['fields']['order']['pricing_data']['user']['meta'][
        'price_before_coupon'
    ] = 555
    if 'is_explicit_antisurge' in test_tags:
        order_proc.order_proc['fields']['order'].setdefault('calc', {})[
            'alternative_type'
        ] = 'explicit_antisurge'
    if 'show_destination_by_adverse' in test_tags:
        order_proc.order_proc['fields']['adverse_destination'] = 'pushkino'

    @mockserver.json_handler(
        '/driver-profiles/v1/driver/app/profiles/retrieve',
    )
    def _mock_get_driver_app(request):
        assert request.json['id_in_set'] == [
            'park1_driver1',
            'park2_driver2',
            'park3_driver3',
            'park4_driver4',
        ]
        return {
            'profiles': [
                {
                    'park_driver_profile_id': 'park1_driver1',
                    'data': {
                        'locale': 'ru',
                        'taximeter_version': '9.50',
                        'taximeter_version_type': 'uber',
                        'taximeter_platform': 'android',
                        'fleet_type': 'uberdriver',
                    },
                },
                {
                    'park_driver_profile_id': 'park2_driver2',
                    'data': {
                        'locale': 'ru',
                        'taximeter_version': '9.50',
                        'taximeter_version_type': '',
                        'taximeter_platform': 'android',
                        'fleet_type': 'taximeter',
                    },
                },
                {
                    'park_driver_profile_id': 'park3_driver3',
                    'data': {
                        'locale': 'en',
                        'taximeter_version': '9.50',
                        'taximeter_version_type': 'uber',
                        'taximeter_platform': 'android',
                        'fleet_type': 'uberdriver',
                    },
                },
                {
                    'park_driver_profile_id': 'park4_driver4',
                    'data': {
                        'locale': 'en',
                        'taximeter_version': '9.50',
                        'taximeter_version_type': 'uber',
                        'taximeter_platform': 'android',
                        'fleet_type': 'uberdriver',
                    },
                },
            ],
        }

    @mockserver.json_handler('/passenger-profile/passenger-profile/v1/profile')
    def _mock_passenger_profile(request):
        return {'first_name': 'Victoria', 'rating': '5'}

    @mockserver.json_handler(
        '/cashbox-integration/v1/parks/cashboxes/current/retrieve',
    )
    def _mock_cashbox_integration(request):
        if request.json.get('park_id') == 'park1':
            return {'cashbox_id': '2222', 'park_id': 'park1'}
        return {'park_id': 'park2'}

    await taxi_driver_orders_builder.tests_control(
        reset_metrics=True, invalidate_caches=True,
    )
    response = await taxi_driver_orders_builder.post(
        V2_SETCAR_CREATE_URL, json=body,
    )
    assert response.status_code == 200, response.text
    result = copy.deepcopy(result)

    patch_if = ['paid_supply']
    if any(x in test_tags for x in patch_if):
        for setcar in result['setcars']:
            setcar['setcar']['fixed_price'] = PAID_SUPPLY_FIXED_PRICE
            setcar['setcar'][
                'driver_fixed_price'
            ] = PAID_SUPPLY_DRIVER_FIXED_PRICE
            setcar['setcar']['paid_supply'] = {'cost': 100}
            setcar['setcar']['fixed_price']['price'] = 298 + 100
            if setcar['driver']['driver_profile_id'] == 'driver2':
                setcar['setcar']['ui'][
                    'accept_toolbar_params'
                ] = PAID_SUPPLY_TOOLBAR_PARAMS_TAXIMETER
                setcar['setcar']['ui']['acceptance_items'][0][
                    'right'
                ] = PAID_SUPPLY_SURGE_SECTION
                setcar['setcar']['ui'][
                    'acceptance_button_params'
                ] = PAID_SUPPLY_ACCEPTANCE_BUTTON_PARAMS
            elif setcar['driver']['driver_profile_id'] == 'driver4':
                setcar['setcar']['ui']['acceptance_items'][1][
                    'subtitle'
                ] = '696 '
                setcar['setcar']['ui']['acceptance_items'][2][
                    'tags'
                ] = PAID_SUPPLY_TAGS_ISR
            else:
                setcar['setcar']['ui']['acceptance_items'][1][
                    'subtitle'
                ] = '696 ₽'
                setcar['setcar']['ui']['acceptance_items'][2][
                    'tags'
                ] = PAID_SUPPLY_TAGS
    else:
        for setcar in result['setcars']:
            setcar['setcar']['fixed_price']['price'] = 298

    patch_if = ['is_explicit_antisurge']
    if any(x in test_tags for x in patch_if):
        for setcar in result['setcars']:
            setcar['setcar']['driver_fixed_price']['show'] = True
            setcar['setcar']['fixed_price']['show'] = True
            if setcar['driver']['driver_profile_id'] == 'driver2':
                setcar['setcar']['ui']['accept_toolbar_params'][
                    'title'
                ] = '2,1 км · 4 мин'
                setcar['setcar']['ui']['accept_toolbar_params'][
                    'subtitle'
                ] = 'Заказ туда, где спрос выше'
                setcar['setcar']['ui'][
                    'acceptance_button_params'
                ] = ANTISURGE_ACCEPTANCE_BUTTON_PARAMS

    # Uber is not affected
    patch_if = ['is_explicit_antisurge', 'show_destination_']
    if any(x in test_tags for x in patch_if):
        for setcar in result['setcars']:
            if setcar['driver']['driver_profile_id'] == 'driver2':
                setcar['setcar']['show_address'] = True
    else:
        for setcar in result['setcars']:
            if setcar['driver']['driver_profile_id'] == 'driver2':
                setcar['setcar']['show_address'] = False
                del setcar['setcar']['ui']['acceptance_items'][4]
                del setcar['setcar']['ui']['acceptance_items'][3]

    # Uber is not affected
    patch_if = ['is_explicit_antisurge']
    if any(x in test_tags for x in patch_if):
        for setcar in result['setcars']:
            if setcar['driver']['driver_profile_id'] == 'driver2':
                setcar['setcar']['ui']['acceptance_items'][0][
                    'right'
                ] = MOCK_UI_TAXIMETER_ANTISURGE_SECTION

    patch_if = ['show_destination_by_long_order']
    if any(x in test_tags for x in patch_if):
        for setcar in result['setcars']:
            setcar['setcar']['order_details'] = [
                {
                    'subtitle': '12 мин, 1,3 км',
                    'title': '',
                    'type': 'long_route',
                },
            ]
            setcar['setcar']['is_long_order'] = True
            if setcar['driver']['driver_profile_id'] == 'driver2':
                setcar['setcar']['ui']['acceptance_items'].append(
                    MOCK_UI_TAXIMETER_LONG_ORDER,
                )
            elif setcar['driver']['driver_profile_id'] in (
                'driver3',
                'driver4',
            ):
                setcar['setcar']['order_details'] = [
                    {
                        'subtitle': '12 min, 1.3 km',
                        'title': '',
                        'type': 'long_route',
                    },
                ]

    for setcar in result['setcars']:
        setcar['setcar_push'] = copy.deepcopy(setcar['setcar'])

        del setcar['setcar_push']['base_price']
        del setcar['setcar_push']['client_geo_sharing']
        del setcar['setcar_push']['driver_fixed_price']
        del setcar['setcar_push']['driver_tags']
        del setcar['setcar_push']['fixed_price']
        del setcar['setcar_push']['waiting_mode']

    assert len(response.json()) == len(result)
    for expected in result['setcars']:
        for real in response.json()['setcars']:
            if real['driver']['alias_id'] == expected['driver']['alias_id']:
                # Crutch: service use unordered_set, it's not relevant for
                # tests, but broke them, so sort them here
                real['setcar']['driver_tags'].sort()

                assert expected['driver'] == real['driver']
                assert expected['setcar'] == real['setcar']

    metrics = await taxi_driver_orders_builder_monitor.get_metric(
        'compare_setcar_per_field_mismatches',
    )
    assert metrics == {}
