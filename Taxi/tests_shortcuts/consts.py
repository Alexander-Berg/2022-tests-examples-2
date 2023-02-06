import copy

URL = 'v1/blender-shortcuts'
MEDIUM_WIDGET_URL = 'v1/medium-widget'
CITY_MODE_URL = 'v1/screen/city-mode'
SCREEN_SUPERMARKET_URL = 'v1/screen/supermarket'
SCREEN_SHOPS_URL = 'v1/screen/shops'
SCREEN_SCOOTERS_URL = 'v1/screen/scooters'

DEEPLINK_TYPE = 'deeplink'
ACTION_DRIVEN_TYPE = 'action-driven'
TAXI_EXPECTED_DEST_TYPE = 'taxi:expected-destination'
MEDIA_STORIES_TYPE = 'media-stories'
INVITES_TYPE = 'invites'
DRIVE_FIXPOINT_OFFERS_TYPE = 'drive:fixpoint-offers'

EATS_PLACES_DELIVERY_TIME = [{'id': 1, 'deliveryTime': {'min': 0, 'max': 10}}]

SUBTITLE_KEY = 'shortcuts_subtitle_template'
SUBTITLE_TEMPLATES = {'ru': '{eta}', 'en': '{eta}'}

DELIVERY_TIME_KEY = 'shortcuts_eats_delivery_time_template'
DELIVERY_TIME_TEMPLATES = {
    'ru': '%(delivery_time)s мин',
    'en': '%(delivery_time)s min',
}

CONTENT_SETTINGS_EXPERIMENT = 'superapp_shortcuts_content_settings'
PREFETCH_EXPERIMENT = 'superapp_shortcuts_prefetch_strategy'
BLOCKS_EXPERIMENT = 'shortcuts_blocks_appearance'
COLLECTION_PSEUDOTITLE_PARAMS = 'collection_pseudotitle_params'
NATIVE_SECTION_TITLE_PARAMS = 'native_section_title_params'
CONTENT_CUSTOMIZATION_MARK_EXPERIMENT = (
    'superapp_shortcuts_content_customization_mark'
)
CONTENT_CUSTOMIZATION_EXPERIMENT = 'superapp_shortcuts_content_customization'
SLEEP_EXPERIMENT = 'sleep_in_blender_shortcuts'
HEADER_PARAMS_EXPERIMENT = 'shortcuts_header_params'
HEADER_LOGGING_EXPERIMENT = 'blender_shortcuts_header_cells_logging'
DELIVERY_AVAILABILITY_EXPERIMENT = 'shortcuts_delivery_brick_availability'
SUPERAPP_BRICKS_APPEARANCE_EXPERIMENT = 'superapp_bricks_appearance'
SUPERAPP_BUTTONS_APPEARANCE_EXPERIMENT = 'superapp_buttons_appearance'
SUPERAPP_MEDIUM_WIDGET_OVERRIDES = 'superapp_medium_widget_overrides'
ULTIMA_AVAILABILITY_EXPERIMENT = 'shortcuts_ultima_availability'
SHORTCUTS_OVERLAYS_EXPERIMENT = 'shortcuts_overlays'
SHORTCUTS_COLOR_REPLACEMENT_SETTINGS_EXP = (
    'shortcuts_color_replacement_settings'
)
RTL_POLICY_EXPERIMENT = 'shortcuts_rtl_policy'
ONBOARDINGS_EXP = 'shortcuts_onboardings'
CHAOS_BRICK_EXP = 'shortcuts_chaotic_brick'
CITY_MODE_PARAMS_EXP = 'city_mode_button_params'
CITY_MODE_LAYERS_CONTEXT_EXP = 'city_mode_layers_context'
SHOP_SCENARIO_EXP = 'shop_scenario_controller'
BUTTONS_CONTAINER_TITLE_EXP = 'buttons_container_title'

TANKER_KEY = 'shortcuts_badge_text'
EATS_TANKER_KEY = 'shortcuts_eats_badge_text'
GROCERY_TANKER_KEY = 'shortcuts_grocery_badge_text'

CITY_SCREEN_TITLE_TANKER_KEY = 'superapp.city.screen_title'

DEFAULT_LAYOUT = {'grid_id': 'id', 'type': 'linear_grid', 'width': 2}

DEFAULT_ATTRIBUTED_TITLE = {
    'items': [
        {
            'type': 'text',
            'text': {'text': 'test text'},
            'font_size': 14,
            'font_weight': 'regular',
            'font_style': 'normal',
            'color': '#000000',
        },
        {'type': 'image', 'image_tag': 'test_image', 'width': 10},
    ],
}

DEFAULT_APPEARANCE = {
    'title_key': 'default_title_key',
    'background_color': 'default_background_color',
    'active_text_color': 'default_active_text_color',
    'disabled_text_color': 'default',
    'icon_tag': 'default_icon_tag',
    'multicolor_icon': {
        'enabled_tag': 'default_enabled_tag',
        'disabled_tag': 'default_disabled_tag',
    },
}

DEFAULT_ICON = {
    'icon_tag': 'mono_tag',
    'multicolor_icon': {
        'enabled_tag': 'colored_enabled_tag',
        'disabled_tag': 'colored_disabled_tag',
    },
}

DEFAULT_GROCERY_SHORTCUT = {
    'id': 'grocery_shortcut_id',
    'scenario': 'grocery_category',
    'content': {'title': 'grocery_title', 'color': '#F5F2E4'},
    'scenario_params': {
        'grocery_category_params': {
            'action_type': 'grocery_category',
            'place_id': '',
            'slug': '',
            'category_id': '1',
        },
    },
}

DEFAULT_EATS_SHORTCUT = {
    'id': 'eats_shortcut_id',
    'scenario': 'eats_place',
    'content': {'title': 'eats_title', 'color': '#F5F2E4'},
    'scenario_params': {
        'eats_place_params': {
            'action_type': 'eats_place',
            'place_id': '1',
            'slug': 'slug',
            'rating': 4.2,
            'price_category': 2,
            'delivery_time': EATS_PLACES_DELIVERY_TIME[0][
                'deliveryTime'
            ],  # EATS_PLACES_DELIVERY_TIME[0] has id = 1
        },
    },
}

DEFAULT_SHOP_SHORTCUT = {
    'id': 'eats_shortcut_id',
    'scenario': 'eats_shop',
    'content': {'title': 'shop_title', 'color': '#F5F2E4'},
    'scenario_params': {
        'eats_place_params': {
            'action_type': 'eats_place',
            'place_id': '1',
            'slug': 'slug',
            'rating': 4.2,
            'price_category': 2,
            'delivery_time': EATS_PLACES_DELIVERY_TIME[0][
                'deliveryTime'
            ],  # EATS_PLACES_DELIVERY_TIME[0] has id = 1
        },
    },
}

DEFAULT_SCREEN_SHOPS_SHORTCUT = {
    'content': {
        'color': '#F5F4F2',
        'image_tag': 'shortcuts_shop_ab_daily_shortcut',
        'title': 'АВ Daily',
    },
    'id': 'eda-place-ea762767447d47869a6440d5260cf481',
    'scenario': 'eats_shop',
    'scenario_params': {
        'eats_place_params': {
            'action_type': 'eats_place',
            'delivery_time': {'max': 30, 'min': 20},
            'place_id': '139755',
            'rating': 4.920000076293945,
            'slug': 'avdaily_2ya_frunzenskaya_10',
        },
    },
}

DEFAULT_MARKET_CATEGORY_SHORTCUT = {
    'id': 'market-f2a1446b57ab4d18926752f31dbc3b6b',
    'scenario': 'market_category',
    'content': {
        'image_tag': 'shortcuts_market_category_21448850',
        'title': 'Бытовая химия',
    },
    'scenario_params': {
        'market_category_params': {
            'url': (
                '/yandex-go/search?nid=21448850'
                '&gps=37.69558289806989%2C55.7278709834352&lr=213'
            ),
        },
    },
}

DEFAULT_SCOOTERS_SHORTCUT = {
    'id': 'discovery_scooters:d26f9aaaf42b4072bee15742c199c5a7',
    'scenario': 'scooters_qr_scan',
    'content': {
        'title': 'Сканировать',
        'subtitle': 'QR-код на руле самоката',
        'color': '#F1F0ED',
        'overlays': [
            {'shape': 'bottom_right', 'image_tag': 'app_shortcut_poi_airport'},
        ],
    },
    'scenario_params': {
        'scooters_qr_scan_params': {'action_type': 'scooters_qr_scan'},
    },
}

WEBAPP_ACTION = {
    'type': 'webapp',
    'web_app_url': (
        'https://m.taxi.taxi.tst.yandex.ru/scooters/subscription/main'
    ),
    'webapp_type': 'scooters-subscription',
}

DEFAULT_ANYACTION_SHORTCUT = {
    'id': 'anyaction-id',
    'scenario': 'some-scenario',
    'content': {'title': 'Подписка'},
    'scenario_params': {'action_params': WEBAPP_ACTION},
}

DEFAULT_TAXI_SHORTCUT = {
    'id': 'taxi_shortcut_id',
    'scenario': 'taxi_expected_destination',
    'content': {
        'title': 'Работа',
        'color': '#F5F2E4',
        'attributed_title': {'items': [{'type': 'text', 'text': 'attr text'}]},
    },
    'scenario_params': {
        'taxi_expected_destination_params': {
            'action_type': 'taxi_expected_destination',
            'position': [1, 2],
            'log': 'some-log',
            'uri': 'some-uri',
        },
    },
}

DEFAULT_TAXI_USERLACE_HOME_SHORTCUT = {
    'id': 'taxi_shortcut_id_userplace_home',
    'scenario': 'taxi_expected_destination',
    'content': {'title': 'Home', 'color': '#F5F2E4'},
    'scenario_params': {
        'taxi_expected_destination_params': {
            'action_type': 'taxi_expected_destination',
            'position': [37.5, 55.5],
            'log': 'some-log',
            'uri': 'some-uri',
            'method': 'userplace',
            'userplace_info': {'place_type': 'home'},
        },
    },
}

DEFAULT_TAXI_AIRPORT_SHORTCUT = {
    'id': 'taxi_shortcut_id_airport',
    'scenario': 'taxi_expected_destination',
    'content': {'title': 'Airport', 'color': '#F5F2E4'},
    'scenario_params': {
        'taxi_expected_destination_params': {
            'action_type': 'taxi_expected_destination',
            'position': [38, 56],
            'log': 'some-log',
            'uri': 'some-uri',
            'icon': {
                'image_tag': 'app_shortcut_poi_airport',
                'background': {'color': '#C4BFA7'},
            },
        },
    },
}

DEFAULT_ANIMATED_TAXI_SHORTCUT = {
    'id': 'taxi_shortcut_id',
    'scenario': 'taxi_expected_destination',
    'content': {
        'title': 'Работа',
        'color': '#F5F2E4',
        'background': {
            'color': '#F2E7E7',
            'image_tag': 'referral_image_tag',
            'animation': {
                'id': 'sdc_onboarding_animation',
                'type': 'pulse_circles',
                'source': {
                    'color': '#FFFFFF',
                    'anchor': {
                        'shape': 'bubble',
                        'point': {'x': 0.5, 'y': 0.0},
                    },
                    'delay_per_circle': 100,
                    'circle_count': 3,
                    'duration': 3000,
                },
                'count': 3,
                'delay': 2.0,
            },
        },
        'attributed_title': {'items': [{'type': 'text', 'text': 'attr text'}]},
    },
    'scenario_params': {
        'taxi_expected_destination_params': {
            'action_type': 'taxi_expected_destination',
            'position': [1, 2],
            'log': 'some-log',
            'uri': 'some-uri',
        },
    },
}

DEFAULT_MEDIA_SHORTCUT = {
    'id': 'media_shortcut_id',
    'scenario': 'does not matter',
    'content': {
        'image_url': (
            'https://taxi-promotions-testing.s3.mdst.yandex.net/'
            'db6b0c3542a74c609a58c391248cb3c8.png'
        ),
        'title': 'tap',
        'color': '0C1E40',
    },
    'scenario_params': {
        'media_stories_params': {
            'action_type': 'media_stories',
            'promo_id': '1bdcff0422cf4d80ac8363915ff5c5ba',
        },
    },
}

DEFAULT_PROMO_SHORTCUT = {
    'id': 'promo_shortcut_id',
    'scenario': 'does not matter',
    'content': {
        'image_url': (
            'https://taxi-promotions-testing.s3.mdst.yandex.net/'
            'db6b0c3542a74c609a58c391248cb3c8.png'
        ),
        'title': 'tap',
        'color': '0C1E40',
    },
    'scenario_params': {
        'promo_stories_params': {
            'action_type': 'promo_stories',
            'promo_id': 'some_promo_stories_id',
        },
    },
}

DEFAULT_INVITE_SHORTCUT = {
    'id': 'invite_shortcut_id',
    'content': {
        'text_color': '#FFFFFF',
        'title': 'Позвать 5 друзей',
        'color': '#75736F',
    },
    'scenario_params': {
        'invites_params': {
            'content': {'title_text': 'Показать друзьям Go'},
            'action_type': 'invites',
            'deeplink': 'deeplink',
        },
    },
    'scenario': 'invites',
}

DEFAULT_REFERRAL_SHORTCUT = {
    'id': 'referral_shortcut_id',
    'content': {
        'text_color': '#FFFFFF',
        'title': 'Some referral',
        'subtitle': 'Some subtitle referral',
        'color': '#75736F',
        'image_tag': 'referral_image_tag',
    },
    'scenario_params': {'referral_params': {'deeplink': 'referral_deeplink'}},
    'scenario': 'referral',
}

DEFAULT_MAAS_SHORTCUT = {
    'id': 'maas_shortcut_id',
    'content': {
        'text_color': '#FFFFFF',
        'title': 'Subscription',
        'subtitle': 'Buy subscription',
        'color': '#75736F',
        'image_tag': 'maas_image_tag',
        'overlays': [
            {
                'shape': 'poi',
                'background': {'color': '#C4BFA7'},
                'image_tag': 'custom_shortcut_default_tag_2',
            },
        ],
    },
    'scenario_params': {'maas_params': {'deeplink': 'maas_deeplink'}},
    'scenario': 'maas',
}

DEFAULT_DEEPLINK_PARAMS_SHORTCUT = {
    'id': 'default_deeplink_params_shortcut_id',
    'content': {
        'text_color': '#deeplink_params_text_color',
        'title': 'Some deeplink_params title',
        'subtitle': 'Some deeplink_params subtitle',
        'color': '#deeplink_params_color',
        'image_tag': 'deeplink_image_tag',
        'overlays': [{'shape': 'bubble'}],
    },
    'scenario_params': {'deeplink_params': {'deeplink': 'referral_deeplink'}},
    'scenario': (
        ''  # sic: if shortcut has deeplink_params, we derive action from it
    ),
}

DEFAULT_DRIVE_SHORTCUT = {
    'content': {'color': '#F5F2E4', 'title': 'Домой', 'subtitle': 'на Драйве'},
    'id': 'fe062acb30bb4fb3bba44f71c909838a',
    'scenario': 'drive_fixpoint_offers',
    'scenario_params': {
        'drive_fixpoint_offers_params': {
            'action_type': 'drive_fixpoint_offers',
            'overlays': [
                {'shape': 'car', 'image_tag': 'drive_shortcut_car_tag'},
                {'shape': 'poi', 'image_tag': 'drive_shortcut_car_poi'},
            ],
            'layers_context': {
                'type': 'drive_fixpoint_offers',
                'src': [33.33, 55.55],
                'dst': [33.307668, 53.246202],
                'destination_name': 'Дом',
                'offer_count_limit': 3,
            },
        },
    },
}

DEFAULT_REDIRECT_DRIVE_SHORTCUT = {
    'content': {
        'color': '#F5F2E4',
        'title': 'Домой',
        'subtitle': 'на Драйве',
        'overlays': [
            {'shape': 'car', 'image_tag': 'drive_shortcut_car_tag'},
            {'shape': 'poi', 'image_tag': 'drive_shortcut_car_poi'},
        ],
    },
    'id': 'default_redirect_drive_shortcut_id',
    'scenario': 'drive_fixpoint_offers',
    'scenario_params': {
        'taxi_summary_redirect_params': {
            'vertical': 'drive',
            'class': 'drive_cargo',
            'state': 'collapsed',
            'vertical_trap': True,
            'destination': {
                'position': [37.211375, 55.577065],
                'log': 'log',
                'uri': 'uri',
            },
        },
    },
}

DEFAULT_SDC_ROUTE_SELECTION_SHORTCUT = {
    'content': {
        'color': '#F5F2E4',
        'title': 'Беспилотник',
        'subtitle': '24 мин',
        'overlays': [
            {'shape': 'car', 'image_tag': 'sdc_shortcut_car_tag'},
            {'shape': 'poi', 'image_tag': 'sdc_shortcut_car_poi'},
        ],
    },
    'id': 'default_sdc_route_selection_shortcut_id',
    'scenario': 'sdc_route_selection',
    'scenario_params': {
        'sdc_route_selection_params': {
            'mode': 'sdc',
            'tariff_class': 'selfdriving',
            'onboarding_promo_id': 'sdc_onboarding_promo',
            'unavailable_reason_fullscreen_id': (
                'emergency_disabled_sdc_onboarding_promo'
            ),
            'selection_screens': [
                {
                    'type': 'a',
                    'text': 'Выберите точку А',
                    'subtitle_text': 'беспилотник там вас подберет',
                    'button': {
                        'text': 'далее',
                        'color': '#ABCABC',
                        'background_color': '#FFF000',
                    },
                },
                {
                    'type': 'b',
                    'text': 'Выберите точку Б',
                    'subtitle_text': 'беспилотник вас там высадит',
                    'button': {
                        'text': 'Готово',
                        'color': '#000FFF',
                        'background_color': '#CABCAB',
                    },
                },
            ],
        },
    },
}

DEFAULT_REDIRECT_SHUTTLE_SHORTCUT = {
    'content': {
        'color': '#F5F2E4',
        'title': 'Домой',
        'subtitle': '24 мин',
        'overlays': [
            {'shape': 'car', 'image_tag': 'shuttle_shortcut_car_tag'},
            {'shape': 'poi', 'image_tag': 'shuttle_shortcut_car_poi'},
        ],
    },
    'id': 'default_redirect_shuttle_shortcut_id',
    'scenario': 'shuttle_route_offer',
    'scenario_params': {
        'taxi_summary_redirect_params': {
            'vertical': 'taxi',
            'class': 'shuttle',
            'state': 'collapsed',
            'vertical_trap': True,
            'maybe_wait_for_routestats': True,
            'destination': {
                'position': [37.211375, 55.577065],
                'log': 'log',
                'uri': 'uri',
            },
        },
    },
}

MEDIA_SHORTCUT_TPL = {
    'scenario': 'does not matter',
    'content': {'title': 'tap', 'color': '0C1E40'},
    'scenario_params': {
        'media_stories_params': {
            'action_type': 'media_stories',
            'promo_id': '1bdcff0422cf4d80ac8363915ff5c5ba',
        },
    },
}

MEDIA_SHORTCUT_CLASS_VIP_ICON_TAG = copy.deepcopy(MEDIA_SHORTCUT_TPL)
MEDIA_SHORTCUT_CLASS_VIP_ICON_TAG['content'][  # type: ignore
    'image_tag'
] = 'class_vip_icon'
MEDIA_SHORTCUT_CLASS_VIP_ICON_TAG['id'] = 'class_vip_icon_id'

MEDIA_SHORTCUT_CLASS_ECONOM_ICON_TAG = copy.deepcopy(MEDIA_SHORTCUT_TPL)
MEDIA_SHORTCUT_CLASS_ECONOM_ICON_TAG['content'][  # type: ignore
    'image_tag'
] = 'class_econom_icon'
MEDIA_SHORTCUT_CLASS_ECONOM_ICON_TAG['id'] = 'class_econom_icon_id'

MEDIA_SHORTCUT_CLASS_BUSINESS_ICON_TAG = copy.deepcopy(MEDIA_SHORTCUT_TPL)
MEDIA_SHORTCUT_CLASS_BUSINESS_ICON_TAG['content'][  # type: ignore
    'image_tag'
] = 'class_business_icon'
MEDIA_SHORTCUT_CLASS_BUSINESS_ICON_TAG['id'] = 'class_business_icon_id'

MEDIA_SHORTCUT_TAG_NOT_IN_CACHE = copy.deepcopy(MEDIA_SHORTCUT_TPL)
MEDIA_SHORTCUT_TAG_NOT_IN_CACHE['content'][  # type: ignore
    'image_tag'
] = 'not_in_cache'
MEDIA_SHORTCUT_TAG_NOT_IN_CACHE['id'] = 'not_in_cache_id'

NATIVE_DELIVERY_ACTION = {
    'vertical': 'vertical',
    'class': 'class',
    'state': 'collapsed',
}

TYPED_NATIVE_DELIVERY_ACTION = {
    **NATIVE_DELIVERY_ACTION,
    'type': 'taxi:summary-redirect',
}

DEEPLINK_ACTION = {'deeplink': 'default_deeplink'}

TYPED_DEEPLINK_ACTION = {**DEEPLINK_ACTION, 'type': 'deeplink'}

TYPED_DISCOVERY_ACTION_TEMPLATE = {
    'mode': 'undefined',  # must be overrided
    'layers_context': {'param_1': 'xxxx'},
    'type': 'discovery',
}

TYPED_MASSTRANSIT_ACTION = {
    **TYPED_DISCOVERY_ACTION_TEMPLATE,  # type: ignore
    'mode': 'masstransit',
}

TYPED_SHUTTLE_ACTION = {
    **TYPED_DISCOVERY_ACTION_TEMPLATE,  # type: ignore
    'mode': 'shuttle',
}

TYPED_DRIVE_ACTION = {
    **TYPED_DISCOVERY_ACTION_TEMPLATE,  # type: ignore
    'mode': 'drive',
}

TYPED_SCOOTERS_ACTION = {
    **TYPED_DISCOVERY_ACTION_TEMPLATE,  # type: ignore
    'mode': 'scooters',
}

TYPED_RESTAURANTS_ACTION = {
    **TYPED_DISCOVERY_ACTION_TEMPLATE,  # type: ignore
    'mode': 'restaurants',
}

TYPED_CONTACTS_ACTION = {
    **TYPED_DISCOVERY_ACTION_TEMPLATE,  # type: ignore
    'mode': 'contacts',
}

TYPED_TAXI_ROUTE_INPUT_ACTION = {'type': 'taxi:route-input'}

ULTIMA_ACTION = {
    'vertical': 'ultima',
    'class': 'vip',
    'state': 'collapsed',
    'vertical_trap': True,
}

TYPED_ULTIMA_ACTION = {
    **ULTIMA_ACTION,  # type: ignore
    'type': 'taxi:summary-redirect',
}
