INSERT INTO discounts.discounts_entities
    (
        description,
        discount_class,
        enabled,
        select_params,
        calculation_params,
        discount_method,
        discount_meta_info
    )
VALUES
    ('discount1', 'discount_class1', true,
    '{
        "classes": ["econom"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc"
        },
        "discount_target": "all",
        "payment_types": ["card", "applepay","cash"],
        "bin_filter": ["123456"]
    }',
    '{
        "round_digits": 2,
        "max_value": 0.35,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "recalc_type": "surge_price",
        "calculation_method": "calculation_formula",
        "discount_calculator": {
            "calculation_formula_v1_threshold": 600,
            "calculation_formula_v1_p1": 35,
            "calculation_formula_v1_p2": 35,
            "calculation_formula_v1_a2": 0,
            "calculation_formula_v1_a1": 0,
            "calculation_formula_v1_c1": 100,
            "calculation_formula_v1_c2": 100
        }
    }',
    'full-driver-less',
    '{
        "branding_keys": {
            "default_branding_keys": {
              "card_title": "key_card_title",
              "card_subtitle": "key_card_subtitle",
              "payment_method_subtitle": "key_payment_method_subtitle"
            },
            "combined_branding_keys": {
              "card_title": "combined_key_card_title",
              "card_subtitle": "combined_key_card_subtitle",
              "payment_method_subtitle": "combined_key_payment_method_subtitle"
            }
        }
    }'),
    ('discount2', 'discount_class2', true,
    '{
        "classes": ["business"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc"
        },
        "discount_target": "all",
        "payment_types": ["card", "applepay","cash"],
        "bin_filter": ["654321"]
    }',
    '{
        "round_digits": 2,
        "max_value": 0.35,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "recalc_type": "surge_price",
        "calculation_method": "calculation_formula",
        "discount_calculator": {
            "calculation_formula_v1_threshold": 600,
            "calculation_formula_v1_p1": 35,
            "calculation_formula_v1_p2": 35,
            "calculation_formula_v1_a2": 0,
            "calculation_formula_v1_a1": 0,
            "calculation_formula_v1_c1": 100,
            "calculation_formula_v1_c2": 100
        }
    }',
    'full-driver-less',
    '{}'),
    ('discount3', 'discount_class3', true,
    '{
        "classes": ["econom"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "date_to": "2019-01-01T00:10:00",
            "timezone_type": "utc"
        },
        "discount_target": "all",
        "payment_types": ["card", "applepay","cash"],
        "bin_filter": ["123456"]
    }',
    '{
        "round_digits": 2,
        "max_value": 0.35,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "recalc_type": "surge_price",
        "calculation_method": "calculation_formula",
        "discount_calculator": {
            "calculation_formula_v1_threshold": 600,
            "calculation_formula_v1_p1": 35,
            "calculation_formula_v1_p2": 35,
            "calculation_formula_v1_a2": 0,
            "calculation_formula_v1_a1": 0,
            "calculation_formula_v1_c1": 100,
            "calculation_formula_v1_c2": 100
        }
    }',
    'full-driver-less',
    '{
        "branding_keys": {
            "default_branding_keys": {
            "card_title": "key_card_title3",
            "card_subtitle": "key_card_subtitle3",
            "payment_method_subtitle": "key_payment_method_subtitle3"
            },
            "combined_branding_keys": {
            "card_title": "combined_key_card_title3",
            "card_subtitle": "combined_key_card_subtitle3",
            "payment_method_subtitle": "combined_key_payment_method_subtitle3"
            }
        }
    }')
