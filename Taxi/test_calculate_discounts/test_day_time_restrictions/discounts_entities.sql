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
    ('discount1', 'discount_class1', true,
    '{
        "classes": ["econom"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc",
            "active_day_type": "schedules",
            "schedules": [
                {
                    "timezone": "LOCAL",
                    "intervals": [
                        {
                          "exclude": false,
                          "day": [ 2, 4, 6]
                        },
                        {
                            "exclude": false,
                            "daytime": [
                                {
                                    "from": "10:00:00",
                                    "to": "19:00:00"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "discount_target": "all",
        "payment_types": ["card", "applepay","cash"]
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
    'full-driver-less'),
    ('discount2', 'discount_class2', true,
    '{
        "classes": ["business"],
        "datetime_params": {
            "date_from": "2019-01-01T00:00:00",
            "timezone_type": "utc",
            "active_day_type": "schedules",
            "schedules": [
                {
                    "timezone": "LOCAL",
                    "intervals": [
                        {
                          "exclude": false,
                          "day": [ 1, 3, 5, 7 ]
                        },
                        {
                            "exclude": false,
                            "daytime": [
                                {
                                    "from": "10:00:00",
                                    "to": "19:00:00"
                                }
                            ]
                        }
                    ]
                }
            ]
        },
        "discount_target": "all",
        "payment_types": ["card", "applepay","cash"]
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
    'full-driver-less'),
    ('discount3', 'discount_class3', true,
     '{
         "classes": ["comfortplus"],
         "datetime_params": {
             "date_from": "2019-01-01T00:00:00",
             "timezone_type": "utc",
             "active_day_type": "everyday",
             "active_local_hours": [
                {
                    "from_time": {
                        "hour": 10,
                        "minute": 0
                    },
                    "to_time": {
                        "hour": 19,
                        "minute":0
                    }
                }
             ]
         },
         "discount_target": "all",
         "payment_types": ["card", "applepay","cash"]
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
     'full-driver-less')
