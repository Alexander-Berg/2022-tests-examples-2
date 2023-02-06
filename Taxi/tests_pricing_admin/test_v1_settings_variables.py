import pytest


YANDEX_LOGIN_HEADER = 'X-Yandex-Login'


async def test_v1_settings_variables_get(taxi_pricing_admin):
    response = await taxi_pricing_admin.get('v1/settings/variables')
    assert response.status_code == 200
    assert response.json() == {
        'fix': {
            'extra_price': {'type': 'optional', 'value': {'type': 'double'}},
            'previous_payment_type': {
                'type': 'optional',
                'value': {'type': 'string'},
            },
            'pricing_antisurge_settings': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {
                        'apply_discount': {'type': 'boolean'},
                        'apply_to_boarding': {'type': 'boolean'},
                        'max_abs_discount': {'type': 'double'},
                        'min_abs_gain': {'type': 'double'},
                        'min_rel_gain': {'type': 'double'},
                    },
                },
            },
            'offer_statistics': {
                'type': 'optional',
                'value': {'type': 'map', 'value': {'type': 'double'}},
            },
            'country_code2': {'type': 'string'},
            'zone': {'type': 'string'},
            'category': {'type': 'string'},
            'preorder_multiplier': {
                'type': 'optional',
                'value': {'type': 'double'},
            },
            'previous_different_category': {
                'type': 'optional',
                'value': {'type': 'string'},
            },
            'forced_fixprice': {
                'type': 'optional',
                'value': {'type': 'double'},
            },
            'waypoints_count': {'type': 'double'},
            'category_data': {
                'type': 'object',
                'value': {
                    'min_paid_supply_price_for_paid_cancel': {
                        'type': 'double',
                    },
                    'callcenter_discount_percents': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'callcenter_extra_percents': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'callcenter_fix_charge': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'decoupling': {'type': 'boolean'},
                    'disable_paid_supply': {
                        'type': 'optional',
                        'value': {'type': 'boolean'},
                    },
                    'disable_surge': {
                        'type': 'optional',
                        'value': {'type': 'boolean'},
                    },
                    'fixed_price': {'type': 'boolean'},
                    'paid_cancel_waiting_time_limit': {'type': 'double'},
                    'yaplus_coeff': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'corp_decoupling': {
                        'type': 'optional',
                        'value': {'type': 'boolean'},
                    },
                },
            },
            'complements': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {
                        'personal_wallet': {
                            'type': 'optional',
                            'value': {
                                'type': 'object',
                                'value': {'balance': {'type': 'double'}},
                            },
                        },
                    },
                },
            },
            'shuttle_params': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {'is_street_hail_booking': {'type': 'boolean'}},
                },
            },
            'alt_offer_discount': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {
                        'params': {'type': 'map', 'value': {'type': 'double'}},
                        'type': {'type': 'string'},
                    },
                },
            },
            'coupon': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {
                        'currency_code': {'type': 'string'},
                        'descr': {'type': 'string'},
                        'details': {
                            'type': 'optional',
                            'value': {
                                'type': 'array',
                                'value': {'type': 'string'},
                            },
                        },
                        'error_code': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'format_currency': {'type': 'boolean'},
                        'limit': {
                            'type': 'optional',
                            'value': {'type': 'double'},
                        },
                        'percent': {
                            'type': 'optional',
                            'value': {'type': 'double'},
                        },
                        'series': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'valid': {'type': 'boolean'},
                        'valid_any': {
                            'type': 'optional',
                            'value': {'type': 'boolean'},
                        },
                        'valid_classes': {
                            'type': 'optional',
                            'value': {
                                'type': 'array',
                                'value': {'type': 'string'},
                            },
                        },
                        'valid_payment_types': {
                            'type': 'optional',
                            'value': {
                                'type': 'set',
                                'value': {'type': 'string'},
                            },
                        },
                        'value': {'type': 'double'},
                    },
                },
            },
            'discount': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {
                        'calc_data_coeff': {
                            'type': 'optional',
                            'value': {'type': 'double'},
                        },
                        'calc_data_hyperbolas': {
                            'type': 'optional',
                            'value': {
                                'type': 'object',
                                'value': {
                                    'hyperbola_lower': {
                                        'type': 'object',
                                        'value': {
                                            'a': {'type': 'double'},
                                            'c': {'type': 'double'},
                                            'p': {'type': 'double'},
                                        },
                                    },
                                    'hyperbola_upper': {
                                        'type': 'object',
                                        'value': {
                                            'a': {'type': 'double'},
                                            'c': {'type': 'double'},
                                            'p': {'type': 'double'},
                                        },
                                    },
                                    'threshold': {'type': 'double'},
                                },
                            },
                        },
                        'calc_data_table_data': {
                            'type': 'optional',
                            'value': {
                                'type': 'array',
                                'value': {
                                    'type': 'object',
                                    'value': {
                                        'coeff': {'type': 'double'},
                                        'price': {'type': 'double'},
                                    },
                                },
                            },
                        },
                        'id': {'type': 'string'},
                        'payment_system': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'is_cashback': {
                            'type': 'optional',
                            'value': {'type': 'boolean'},
                        },
                        'restrictions': {
                            'type': 'object',
                            'value': {
                                'driver_less_coeff': {'type': 'double'},
                                'max_absolute_value': {
                                    'type': 'optional',
                                    'value': {'type': 'double'},
                                },
                                'max_discount_coeff': {'type': 'double'},
                                'min_discount_coeff': {'type': 'double'},
                            },
                        },
                        'limited_rides': {
                            'type': 'optional',
                            'value': {'type': 'boolean'},
                        },
                        'with_restriction_by_usages': {
                            'type': 'optional',
                            'value': {'type': 'boolean'},
                        },
                        'description': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'discount_class': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'method': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'limit_id': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'is_price_strikethrough': {
                            'type': 'optional',
                            'value': {'type': 'boolean'},
                        },
                        'competitors': {
                            'type': 'optional',
                            'value': {
                                'type': 'set',
                                'value': {'type': 'string'},
                            },
                        },
                    },
                },
            },
            'cashback_discount': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {
                        'calc_data_coeff': {
                            'type': 'optional',
                            'value': {'type': 'double'},
                        },
                        'calc_data_hyperbolas': {
                            'type': 'optional',
                            'value': {
                                'type': 'object',
                                'value': {
                                    'hyperbola_lower': {
                                        'type': 'object',
                                        'value': {
                                            'a': {'type': 'double'},
                                            'c': {'type': 'double'},
                                            'p': {'type': 'double'},
                                        },
                                    },
                                    'hyperbola_upper': {
                                        'type': 'object',
                                        'value': {
                                            'a': {'type': 'double'},
                                            'c': {'type': 'double'},
                                            'p': {'type': 'double'},
                                        },
                                    },
                                    'threshold': {'type': 'double'},
                                },
                            },
                        },
                        'calc_data_table_data': {
                            'type': 'optional',
                            'value': {
                                'type': 'array',
                                'value': {
                                    'type': 'object',
                                    'value': {
                                        'coeff': {'type': 'double'},
                                        'price': {'type': 'double'},
                                    },
                                },
                            },
                        },
                        'id': {'type': 'string'},
                        'payment_system': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'is_cashback': {
                            'type': 'optional',
                            'value': {'type': 'boolean'},
                        },
                        'restrictions': {
                            'type': 'object',
                            'value': {
                                'driver_less_coeff': {'type': 'double'},
                                'max_absolute_value': {
                                    'type': 'optional',
                                    'value': {'type': 'double'},
                                },
                                'max_discount_coeff': {'type': 'double'},
                                'min_discount_coeff': {'type': 'double'},
                            },
                        },
                        'limited_rides': {
                            'type': 'optional',
                            'value': {'type': 'boolean'},
                        },
                        'with_restriction_by_usages': {
                            'type': 'optional',
                            'value': {'type': 'boolean'},
                        },
                        'description': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'discount_class': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'method': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'limit_id': {
                            'type': 'optional',
                            'value': {'type': 'string'},
                        },
                        'is_price_strikethrough': {
                            'type': 'optional',
                            'value': {'type': 'boolean'},
                        },
                        'competitors': {
                            'type': 'optional',
                            'value': {
                                'type': 'set',
                                'value': {'type': 'string'},
                            },
                        },
                    },
                },
            },
            'exps': {
                'type': 'map',
                'value': {
                    'type': 'map',
                    'value': {
                        'type': 'object',
                        'value': {
                            'str': {
                                'type': 'optional',
                                'value': {'type': 'string'},
                            },
                            'val': {
                                'type': 'optional',
                                'value': {'type': 'double'},
                            },
                            'boolean': {
                                'type': 'optional',
                                'value': {'type': 'boolean'},
                            },
                        },
                    },
                },
            },
            'paid_supply_price': {
                'type': 'optional',
                'value': {'type': 'double'},
            },
            'payment_type': {'type': 'optional', 'value': {'type': 'string'}},
            'requirements': {
                'type': 'object',
                'value': {
                    'select': {
                        'type': 'map',
                        'value': {
                            'type': 'array',
                            'value': {
                                'type': 'object',
                                'value': {
                                    'independent': {'type': 'boolean'},
                                    'name': {'type': 'string'},
                                },
                            },
                        },
                    },
                    'simple': {'type': 'set', 'value': {'type': 'string'}},
                },
            },
            'editable_requirements': {
                'type': 'optional',
                'value': {
                    'type': 'map',
                    'value': {
                        'type': 'object',
                        'value': {
                            'default_value': {'type': 'double'},
                            'max_value': {
                                'type': 'optional',
                                'value': {'type': 'double'},
                            },
                            'min_value': {
                                'type': 'optional',
                                'value': {'type': 'double'},
                            },
                        },
                    },
                },
            },
            'cargo_requirements': {
                'type': 'optional',
                'value': {
                    'type': 'map',
                    'value': {
                        'type': 'object',
                        'value': {
                            'max_value': {
                                'type': 'optional',
                                'value': {'type': 'double'},
                            },
                            'min_value': {
                                'type': 'optional',
                                'value': {'type': 'double'},
                            },
                        },
                    },
                },
            },
            'surge_params': {
                'type': 'object',
                'value': {
                    'explicit_antisurge': {
                        'type': 'optional',
                        'value': {
                            'type': 'object',
                            'value': {
                                'surcharge': {
                                    'type': 'optional',
                                    'value': {'type': 'double'},
                                },
                                'surcharge_alpha': {
                                    'type': 'optional',
                                    'value': {'type': 'double'},
                                },
                                'surcharge_beta': {
                                    'type': 'optional',
                                    'value': {'type': 'double'},
                                },
                                'value': {'type': 'double'},
                            },
                        },
                    },
                    'surcharge': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'surcharge_alpha': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'surcharge_beta': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'value': {'type': 'double'},
                    'value_raw': {'type': 'double'},
                    'pins_approx': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'trend_time_delta_sec': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'surge_trend': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'value_b': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'value_smooth': {'type': 'double'},
                    'free_drivers': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'free_drivers_chain': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'pins': {'type': 'optional', 'value': {'type': 'double'}},
                    'radius': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                    'total_drivers': {
                        'type': 'optional',
                        'value': {'type': 'double'},
                    },
                },
            },
            'plus_promo': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {
                        'max_tariffs_ratio_percent': {
                            'type': 'optional',
                            'value': {'type': 'double'},
                        },
                        'change_diff_percent': {'type': 'double'},
                        'tariff_from': {'type': 'string'},
                    },
                },
            },
            'tariff': {
                'type': 'object',
                'value': {
                    'boarding_price': {'type': 'double'},
                    'minimum_price': {'type': 'double'},
                    'paid_cancel_options': {
                        'type': 'optional',
                        'value': {
                            'type': 'object',
                            'value': {
                                'add_minimal_to_paid_cancel': {
                                    'type': 'boolean',
                                },
                                'paid_cancel_fix': {'type': 'double'},
                            },
                        },
                    },
                    'requirement_multipliers': {
                        'type': 'optional',
                        'value': {'type': 'map', 'value': {'type': 'double'}},
                    },
                    'requirement_prices': {
                        'type': 'map',
                        'value': {'type': 'double'},
                    },
                    'requirements_included_one_of': {
                        'type': 'optional',
                        'value': {'type': 'set', 'value': {'type': 'string'}},
                    },
                    'transfer_prices': {
                        'type': 'optional',
                        'value': {
                            'type': 'object',
                            'value': {
                                'boarding_price': {'type': 'double'},
                                'minimum_price': {'type': 'double'},
                                'waiting_price': {
                                    'type': 'object',
                                    'value': {
                                        'free_waiting_time': {
                                            'type': 'double',
                                        },
                                        'price_per_minute': {'type': 'double'},
                                    },
                                },
                            },
                        },
                    },
                    'waiting_price': {
                        'type': 'object',
                        'value': {
                            'free_waiting_time': {'type': 'double'},
                            'price_per_minute': {'type': 'double'},
                        },
                    },
                },
            },
            'user_data': {
                'type': 'object',
                'value': {
                    'has_yaplus': {'type': 'boolean'},
                    'has_cashback_plus': {'type': 'boolean'},
                },
            },
            'user_tags': {'type': 'set', 'value': {'type': 'string'}},
            'rounding_factor': {'type': 'double'},
            'base_price_discount': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {
                        'boarding_discount': {'type': 'double'},
                        'distance_discount': {'type': 'double'},
                        'time_discount': {'type': 'double'},
                    },
                },
            },
            'cashback_rates': {
                'type': 'optional',
                'value': {
                    'type': 'array',
                    'value': {
                        'type': 'object',
                        'value': {
                            'max_value': {
                                'type': 'optional',
                                'value': {'type': 'double'},
                            },
                            'rate': {'type': 'double'},
                            'sponsor': {'type': 'string'},
                        },
                    },
                },
            },
            'previously_calculated_categories': {
                'type': 'optional',
                'value': {
                    'type': 'map',
                    'value': {
                        'type': 'object',
                        'value': {
                            'driver': {
                                'type': 'object',
                                'value': {
                                    'base_price_total': {'type': 'double'},
                                    'final_prices': {
                                        'type': 'map',
                                        'value': {
                                            'type': 'object',
                                            'value': {
                                                'meta': {
                                                    'type': 'map',
                                                    'value': {
                                                        'type': 'double',
                                                    },
                                                },
                                                'strikeout': {
                                                    'type': 'optional',
                                                    'value': {
                                                        'type': 'double',
                                                    },
                                                },
                                                'total': {'type': 'double'},
                                            },
                                        },
                                    },
                                },
                            },
                            'user': {
                                'type': 'object',
                                'value': {
                                    'base_price_total': {'type': 'double'},
                                    'final_prices': {
                                        'type': 'map',
                                        'value': {
                                            'type': 'object',
                                            'value': {
                                                'meta': {
                                                    'type': 'map',
                                                    'value': {
                                                        'type': 'double',
                                                    },
                                                },
                                                'strikeout': {
                                                    'type': 'optional',
                                                    'value': {
                                                        'type': 'double',
                                                    },
                                                },
                                                'total': {'type': 'double'},
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'combo_offers_data': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {
                        'combo_coeff': {
                            'type': 'optional',
                            'value': {'type': 'double'},
                        },
                        'combo_inner_coeff': {
                            'type': 'optional',
                            'value': {'type': 'double'},
                        },
                        'combo_outer_coeff': {
                            'type': 'optional',
                            'value': {'type': 'double'},
                        },
                        'combo_inner_settings': {
                            'type': 'optional',
                            'value': {
                                'type': 'object',
                                'value': {
                                    'discount_function': {'type': 'string'},
                                    'extra': {
                                        'type': 'map',
                                        'value': {'type': 'double'},
                                    },
                                },
                            },
                        },
                        'combo_outer_settings': {
                            'type': 'optional',
                            'value': {
                                'type': 'object',
                                'value': {
                                    'discount_function': {'type': 'string'},
                                    'extra': {
                                        'type': 'map',
                                        'value': {'type': 'double'},
                                    },
                                },
                            },
                        },
                        'apply_combo_discount_for_driver': {
                            'type': 'optional',
                            'value': {'type': 'boolean'},
                        },
                    },
                },
            },
            'forced_skip_label': {
                'type': 'optional',
                'value': {'type': 'enum', 'value': ['kWithoutSurge']},
            },
            'new_fixprice_params': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {
                        'distance_ab': {'type': 'double'},
                        'distance_ac': {'type': 'double'},
                        'distance_bc': {'type': 'double'},
                        'distance_cb': {'type': 'double'},
                        'distance_abf': {'type': 'double'},
                        'distance_bfb': {'type': 'double'},
                        'fixed_price_boarding': {'type': 'double'},
                        'fixed_price_distance': {'type': 'double'},
                        'fixed_price_time': {'type': 'double'},
                    },
                },
            },
            'quasifixed_params': {
                'type': 'optional',
                'value': {
                    'type': 'object',
                    'value': {
                        'distance_a_b': {'type': 'double'},
                        'distance_a_bf': {'type': 'double'},
                        'distance_b_bf': {'type': 'double'},
                        'distance_bf_b': {'type': 'double'},
                        'fixed_price_boarding': {'type': 'double'},
                        'fixed_price_distance': {'type': 'double'},
                        'fixed_price_time': {'type': 'double'},
                    },
                },
            },
            'expected_prices': {
                'type': 'optional',
                'value': {'type': 'map', 'value': {'type': 'double'}},
            },
            'accepted_driver_price': {
                'type': 'optional',
                'value': {'type': 'double'},
            },
        },
        'ride': {
            'price': {
                'type': 'object',
                'value': {
                    'boarding': {'type': 'double'},
                    'destination_waiting': {'type': 'double'},
                    'distance': {'type': 'double'},
                    'requirements': {'type': 'double'},
                    'time': {'type': 'double'},
                    'transit_waiting': {'type': 'double'},
                    'waiting': {'type': 'double'},
                },
            },
            'ride': {
                'type': 'object',
                'value': {
                    'user_options': {
                        'type': 'map',
                        'value': {'type': 'double'},
                    },
                    'user_meta': {'type': 'map', 'value': {'type': 'double'}},
                    'waiting_in_destination_time': {'type': 'double'},
                    'waiting_in_transit_time': {'type': 'double'},
                    'waiting_time': {'type': 'double'},
                },
            },
        },
        'trip': {'distance': {'type': 'double'}, 'time': {'type': 'double'}},
    }
