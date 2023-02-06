INSERT INTO discounts.discounts_entities
    (
        description,
        discount_class,
        enabled,
        select_params,
        calculation_params,
        discount_method
    )
VALUES
    ('city_discount_econom',
    'city_discount_econom_discount_class',
     true,
    '{
        "classes": ["econom"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc"
        },
        "discount_target": "all",
        "payment_types": ["card", "applepay","cash"],
        "order_type_settings": ["other"]
    }',
    '{
        "round_digits": 2,
        "max_value": 0.35,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "recalc_type": "none",
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
    'full'),
    ('to_airport_discount_econom',
    'to_airport_discount_econom_discount_class',
    true,
    '{
        "classes": ["econom"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc"
        },
        "discount_target": "all",
        "payment_types": ["card", "applepay","cash"],
        "order_type_settings": ["to_airport"]
    }',
    '{
        "round_digits": 2,
        "max_value": 0.35,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "recalc_type": "none",
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
    'full'),
    ('from_airport_discount_econom',
    'from_airport_discount_econom_discount_class',
    true,
    '{
        "classes": ["econom"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc"
        },
        "discount_target": "all",
        "payment_types": ["card", "applepay","cash"],
        "order_type_settings": ["from_airport"]
    }',
    '{
        "round_digits": 2,
        "max_value": 0.35,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "recalc_type": "none",
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
    'full'),
    ('city_comfortplus',
    'city_comfortplus_discount_class',
    true,
    '{
        "classes": ["comfortplus"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc"
        },
        "discount_target": "all",
        "payment_types": ["card", "applepay","cash"],
        "apply_for_airport_orders": false
    }',
    '{
        "round_digits": 2,
        "max_value": 0.35,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "recalc_type": "none",
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
    'full'),
    ('from_or_to_airport_comfortplus',
    'from_or_to_airport_comfortplus_discount_class',
    true,
    '{
        "classes": ["comfortplus"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc"
        },
        "discount_target": "all",
        "payment_types": ["card", "applepay","cash"],
        "apply_for_airport_orders": true
    }',
    '{
        "round_digits": 2,
        "max_value": 0.35,
        "min_value": 0.01,
        "newbie_max_coeff": 1.5,
        "newbie_num_coeff": 0.15,
        "recalc_type": "none",
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
    'full')
