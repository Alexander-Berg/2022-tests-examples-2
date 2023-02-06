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
        "discount_target": "tag_service",
        "payment_types": ["coop_account"],
        "limited_rides_params": {"num_rides_for_newbies": 10},
        "application_platforms": ["android"],
        "user_tags": ["dummy_tag"],
        "bin_filter": ["123456"]
    }',
    '{
        "round_digits": 2,
        "max_value": 0.20,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "calculation_method": "calculation_formula",
        "discount_calculator": {
            "calculation_formula_v1_threshold": 600,
            "calculation_formula_v1_p1": -8,
            "calculation_formula_v1_p2": 8,
            "calculation_formula_v1_a2": 3000,
            "calculation_formula_v1_a1": 42000,
            "calculation_formula_v1_c1": 1400,
            "calculation_formula_v1_c2": 0
        }
    }',
    'full',
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
        },
        "is_price_strikethrough" : true
    }'),
    ('discount2', 'discount_class2', true,
    '{
        "classes": ["econom"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc"
        },
        "discount_target": "newbie",
        "payment_types": ["card", "applepay","cash"],
        "limited_rides_params": {"num_rides_for_newbies": 10},
        "application_platforms": ["iphone"]
    }',
    '{
        "round_digits": 2,
        "max_value": 0.20,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "calculation_method": "calculation_formula",
        "discount_calculator": {
            "calculation_formula_v1_threshold": 600,
            "calculation_formula_v1_p1": -8,
            "calculation_formula_v1_p2": 8,
            "calculation_formula_v1_a2": 3000,
            "calculation_formula_v1_a1": 42000,
            "calculation_formula_v1_c1": 1400,
            "calculation_formula_v1_c2": 0
        }
    }',
    'full',
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
        },
        "is_price_strikethrough" : false
    }'),
    ('discount3', 'discount_class3', true,
    '{
        "classes": ["business"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc"
        },
        "discount_target": "all",
        "payment_types": ["card", "coop_account"],
        "limited_rides_params": {"num_rides_for_newbies": 10},
        "application_platforms": []
    }',
    '{
        "round_digits": 2,
        "max_value": 0.20,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "calculation_method": "calculation_table",
        "discount_calculator": {
            "table": [
                {"cost": 100, "discount": 0.5},
                {"cost": 200, "discount": 0.3},
                {"cost": 300, "discount": 0.1}
             ]
        }
    }',
    'full',
    '{
        "is_price_strikethrough" : false
    }'),
    ('discount4', 'discount_class5',true,
    '{
        "classes": ["business"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc"
        },
        "discount_target": "all",
        "payment_types": ["card", "applepay","cash"],
        "limited_rides_params": {"num_rides_for_newbies": 10},
        "application_platforms": ["iphone"]
    }',
    '{
        "round_digits": 2,
        "max_value": 0.20,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "calculation_method": "calculation_formula",
        "discount_calculator": {
            "calculation_formula_v1_threshold": 600,
            "calculation_formula_v1_p1": -8,
            "calculation_formula_v1_p2": 8,
            "calculation_formula_v1_a2": 3000,
            "calculation_formula_v1_a1": 42000,
            "calculation_formula_v1_c1": 1400,
            "calculation_formula_v1_c2": 0
        }
    }',
    'full',
     '{
         "is_price_strikethrough" : false
     }'),
    ('discount5', 'discount_class5',true,
    '{
        "classes": ["comfortplus"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc"
        },
        "discount_target": "all",
        "payment_types": ["business_account"],
        "limited_rides_params": {"num_rides_for_newbies": 10}
    }',
    '{
        "round_digits": 2,
        "max_value": 0.20,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "calculation_method": "calculation_formula",
        "discount_calculator": {
            "calculation_formula_v1_threshold": 600,
            "calculation_formula_v1_p1": -8,
            "calculation_formula_v1_p2": 8,
            "calculation_formula_v1_a2": 3000,
            "calculation_formula_v1_a1": 42000,
            "calculation_formula_v1_c1": 1400,
            "calculation_formula_v1_c2": 0
        }
    }',
     'full',
     '{
         "is_price_strikethrough" : true
     }')
