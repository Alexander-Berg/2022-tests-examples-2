INSERT INTO discounts_operation_calculations.suggests(
    id,
    algorithm_ids,
    author,
    discounts_city,
    draft_url,
    status,
    statistics,
    multidraft_params,
    created_at,
    updated_at,
    draft_id,
    budget,
    date_to,
    date_from,
    with_push,
    calc_segments_params,
    max_absolute_value,
    tariff_zones
)
VALUES  (
            1,
            ARRAY['test_algo_3'],
            'eugenest',
            'Абиджан',
            'https://ya.ru/1',
            'NEED_APPROVAL',
            '[{"plot": {"data": [[0.64, 78], [1.25, 78.01]], "x_label": "Бюджет", "y_label": "название метрики: экстра трипы, отобранные офферы"}, "algorithm_id": "test_algo_3"}, {"plot": {"data": [[0.61, 64.0], [1.25, 66.99]], "x_label": "Бюджет", "y_label": "название второй метрики"}, "algorithm_id": "test_algo_3"}]',
            '{
                "charts": [
                    {
                        "plot": {
                            "data": [[50, 0], [100, 0]],
                            "label": "0",
                            "x_label": "Цена поездки",
                            "y_label": "Скидка"
                        },
                        "algorithm_id": "test_algo_3"
                    }
                ],
                "discount_meta": {
                    "test_algo_3": {
                        "cur_cpeo": 363.03717288301254,
                        "with_push": false,
                        "budget_spent": 330069.2602347456,
                        "segments_meta": {
                            "3": {
                                "budget": 0,
                                "avg_discount": 0,
                                "max_discount_percent": 0,
                                "max_price_with_discount": 0
                            },
                            "random": {
                                "budget": 330069.2602347457,
                                "avg_discount": 0.021487615114763072,
                                "max_discount_percent": 12,
                                "max_price_with_discount": 250
                            },
                            "control": {
                                "budget": 0,
                                "avg_discount": 0,
                                "max_discount_percent": 0,
                                "max_price_with_discount": 0
                            }
                        },
                        "fixed_discounts": [
                            {
                                "segment": "control",
                                "discount_value": 0
                            },
                            {
                                "segment": "random",
                                "discount_value": 12
                            }
                        ],
                        "fallback_discount": 0
                    }
                }
            }',
            '2022-01-28 12:23:05',
            '2022-01-28 12:24:36',
            529481,
            345675,
            '2022-02-16 12:23:16',
            '2022-01-28 12:53:31',
            false,
            '{"common_params": {"tariffs": ["econom"], "companies": ["didi"], "max_discount": 30, "min_discount": 0, "discounts_city": "Москва"}, "custom_params": [{"max_surge": 1.2, "with_push": false, "algorithm_id": "test_algo_3"}]}',
            1000,
            ARRAY ['abidjan']
        ),
        (
            2,
            ARRAY['test_algo_2', 'test_algo_3'],
            'eugenest',
            'Абиджан',
            'https://ya.ru/2',
            'NEED_APPROVAL',
            '[{"plot": {"data": [[0.64, 78], [1.25, 78.01]], "x_label": "Бюджет", "y_label": "название метрики: экстра трипы, отобранные офферы"}, "algorithm_id": "test_algo_3"}, {"plot": {"data": [[0.61, 64.0], [1.25, 66.99]], "x_label": "Бюджет", "y_label": "название второй метрики"}, "algorithm_id": "test_algo_3"}]',
            '{
                "charts": [
                    {
                        "plot": {
                            "data": [[50, 0], [100, 0]],
                            "label": "0",
                            "x_label": "Цена поездки",
                            "y_label": "Скидка"
                        },
                        "algorithm_id": "test_algo_3"
                    },
                    {
                        "plot": {
                            "data": [[50, 0], [100, 0]],
                            "label": "metrika_active_Hconv",
                            "x_label": "Цена поездки",
                            "y_label": "Скидка"
                        },
                        "algorithm_id": "test_algo_2"
                    },
                    {
                        "plot": {
                            "data": [[50, 48], [100, 12], [150, 0]],
                            "label": "metrika_notactive_Mconv",
                            "x_label": "Цена поездки",
                            "y_label": "Скидка"
                        },
                        "algorithm_id": "test_algo_2"
                    },
                    {
                        "plot": {
                            "data": [[50, 12], [100, 12]],
                            "label": "random",
                            "x_label": "Цена поездки",
                            "y_label": "Скидка"
                        },
                        "algorithm_id": "test_algo_2"
                    }
                ],
                "discount_meta": {
                    "test_algo_3": {
                        "cur_cpeo": 75.98515147558453,
                        "with_push": false,
                        "budget_spent": 607002.6763301387,
                        "segments_meta": {
                            "3": {
                                "budget": 63743.73740576281,
                                "avg_discount": 0.005741409771862867,
                                "max_discount_percent": 21,
                                "max_price_with_discount": 200
                            }
                        },
                        "fixed_discounts": [
                            {
                                "segment": "control",
                                "discount_value": 0
                            },
                            {
                                "segment": "random",
                                "discount_value": 12
                            }
                        ],
                        "fallback_discount": 0
                    },
                    "test_algo_2": {
                        "cur_cpeo": 93.60499173303528,
                        "with_push": false,
                        "budget_spent": 599260.4715202763,
                        "segments_meta": {
                            "random": {
                                "budget": 304497.2137872865,
                                "avg_discount": 0.018177695900786633,
                                "max_discount_percent": 12,
                                "max_price_with_discount": 650
                            },
                            "metrika_active_Mconv": {
                                "budget": 3.86304,
                                "avg_discount": 3.0993372708486274e-8,
                                "max_discount_percent": 48,
                                "max_price_with_discount": 50
                            }
                        },
                        "fixed_discounts": [
                            {
                                "segment": "control",
                                "discount_value": 0
                            },
                            {
                                "segment": "random",
                                "discount_value": 12
                            }
                        ],
                        "fallback_discount": 0
                    }
                }
            }',
             '2022-01-28 11:42:36',
             '2022-01-28 12:23:30',
             529429,
             1234124,
             '2022-02-11 11:42:48',
             '2022-01-28 12:12:58',
             false,
             '{"common_params": {"tariffs": ["econom"], "companies": ["citymobil"], "max_discount": 30, "min_discount": 0, "discounts_city": "Москва"}, "custom_params": [{"max_surge": 1.2, "with_push": false, "algorithm_id": "test_algo_3"}, {"max_surge": 1.2, "with_push": false, "algorithm_id": "test_algo_2"}]}',
             1000,
             ARRAY ['abidjan']
        ),
        (
            3,
            ARRAY['test_algo_2', 'test_algo_3'],
            'eugenest',
            'Тестовый город',
            'https://ya.ru/2',
            'NEED_APPROVAL',
            '[{"plot": {"data": [[0.64, 78], [1.25, 78.01]], "x_label": "Бюджет", "y_label": "название метрики: экстра трипы, отобранные офферы"}, "algorithm_id": "test_algo_3"}, {"plot": {"data": [[0.61, 64.0], [1.25, 66.99]], "x_label": "Бюджет", "y_label": "название второй метрики"}, "algorithm_id": "test_algo_3"}]',
            '{
                "charts": [],
                "discount_meta": {
                    "test_algo_3": {
                        "cur_cpeo": 75.98515147558453,
                        "with_push": false,
                        "budget_spent": 607002.6763301387,
                        "segments_meta": {
                            "3": {
                                "budget": 63743.73740576281,
                                "avg_discount": 0.005741409771862867,
                                "max_discount_percent": 21,
                                "max_price_with_discount": 200
                            }
                        },
                        "fixed_discounts": [
                        ],
                        "fallback_discount": 0
                    }
                }
            }',
             '2022-01-28 11:42:36',
             '2022-01-28 12:23:30',
             529429,
             1234124,
             '2022-02-11 11:42:48',
             '2022-01-28 12:12:58',
             false,
             '{"common_params": {"tariffs": ["econom"], "companies": ["citymobil"], "max_discount": 30, "min_discount": 0, "discounts_city": "Москва"}, "custom_params": [{"max_surge": 1.2, "with_push": false, "algorithm_id": "test_algo_3"}, {"max_surge": 1.2, "with_push": false, "algorithm_id": "test_algo_2"}]}',
             1000,
             ARRAY ['test', 'test2']
        ),
        (
            4,
            ARRAY['test_algo_1'],
            'raifox',
            'Саратов',
            'https://ya.ru/4',
            'NEED_APPROVAL',
            '[{"plot": {"data": [[0.64, 78], [1.25, 78.01]], "x_label": "Бюджет", "y_label": "название метрики: экстра трипы, отобранные офферы"}, "algorithm_id": "test_algo_3"}, {"plot": {"data": [[0.61, 64.0], [1.25, 66.99]], "x_label": "Бюджет", "y_label": "название второй метрики"}, "algorithm_id": "test_algo_3"}]',
            '{
                "charts": [],
                "discount_meta": {
                    "test_algo_1": {
                        "cur_cpeo": 75.98515147558453,
                        "with_push": false,
                        "budget_spent": 607002.6763301387,
                        "segments_meta": {
                            "3": {
                                "budget": 63743.73740576281,
                                "avg_discount": 0.005741409771862867,
                                "max_discount_percent": 21,
                                "max_price_with_discount": 200
                            }
                        },
                        "fixed_discounts": [
                        ],
                        "fallback_discount": 0
                    }
                }
            }',
             '2022-01-28 11:42:36',
             '2022-01-28 12:23:30',
             529429,
             1234124,
             '2022-02-11 11:42:48',
             '2022-01-28 12:12:58',
             false,
             '{"common_params": {"tariffs": ["comfortplus", "econom", "business", "uberx"], "companies": ["citymobil"], "max_discount": 30, "min_discount": 0, "discounts_city": "Москва"}, "custom_params": [{"max_surge": 1.2, "with_push": false, "algorithm_id": "test_algo_3"}, {"max_surge": 1.2, "with_push": false, "algorithm_id": "test_algo_2"}]}',
             1000,
             ARRAY ['saratov']
        ),
        (
            5,
            ARRAY['test_algo_1'],
            'testlogin',
            'Тест город',
            'https://ya.ru/5',
            'NEED_APPROVAL',
            '[{"plot": {"data": [[0.64, 78], [1.25, 78.01]], "x_label": "Бюджет", "y_label": "название метрики: экстра трипы, отобранные офферы"}, "algorithm_id": "test_algo_3"}, {"plot": {"data": [[0.61, 64.0], [1.25, 66.99]], "x_label": "Бюджет", "y_label": "название второй метрики"}, "algorithm_id": "test_algo_3"}]',
            '{
                "charts": [],
                "discount_meta": {
                    "test_algo_1": {
                        "cur_cpeo": 75.98515147558453,
                        "with_push": false,
                        "budget_spent": 607002.6763301387,
                        "segments_meta": {
                            "3": {
                                "budget": 63743.73740576281,
                                "avg_discount": 0.005741409771862867,
                                "max_discount_percent": 21,
                                "max_price_with_discount": 200
                            }
                        },
                        "fixed_discounts": [
                        ],
                        "fallback_discount": 0
                    }
                }
            }',
             '2022-01-28 11:42:36',
             '2022-01-28 12:23:30',
             529429,
             1234124,
             '2022-02-11 11:42:48',
             '2022-01-28 12:12:58',
             false,
             '{"common_params": {"tariffs": ["econom", "business", "uberx"], "companies": ["citymobil"], "max_discount": 30, "min_discount": 0, "discounts_city": "Москва"}, "custom_params": [{"max_surge": 1.2, "with_push": false, "algorithm_id": "test_algo_3"}, {"max_surge": 1.2, "with_push": false, "algorithm_id": "test_algo_2"}]}',
             1000,
             ARRAY ['omsk']
        );
