INSERT INTO ride_discounts.match_data (data_id, data, series_id)
VALUES (1,
        '{
            "name": "with_maximum_budget_per_person",
            "values_with_schedules": [
                {
                    "schedule": {
                        "timezone": "LOCAL",
                        "intervals": [
                            {
                                "day": [
                                    1
                                ],
                                "exclude": false
                            }
                        ]
                    },
                    "cashback_value": {
                        "discount_value": {
                            "value": [
                                {
                                    "from_cost": 0,
                                    "discount": 5
                                }
                            ],
                            "value_type": "table"
                        },
                        "max_absolute_value": 50.0
                    }
                }
            ],
            "limits": {
                "id": "discount_with_maximum_budget_per_person",
                "daily_limit": {
                    "value": "145000.0000",
                    "threshold": 100
                },
                "weekly_limit": {
                    "value": "1000000.0000",
                    "threshold": 100,
                    "type": "sliding"
                }
            },
            "maximum_budget_per_person": [{"value": 1000}]
        }',
        '11111111-1111-1111-1111-111111111111'),
       (2,
        '{
            "name": "with_discount_usage_restrictions",
            "values_with_schedules": [
                {
                    "schedule": {
                        "timezone": "LOCAL",
                        "intervals": [
                            {
                                "day": [
                                    1
                                ],
                                "exclude": false
                            }
                        ]
                    },
                    "money_value": {
                        "discount_value": {
                            "value": [
                                {
                                    "from_cost": 0,
                                    "discount": 5
                                }
                            ],
                            "value_type": "table"
                        },
                        "max_absolute_value": 50.0
                    }
                }
            ],
            "discount_usage_restrictions": [{"max_count": 2}]
        }',
        '22222222-2222-2222-2222-222222222222'),
       (3,
        '{
            "name": "without_any_restrictions",
                        "values_with_schedules": [
                {
                    "schedule": {
                        "timezone": "LOCAL",
                        "intervals": [
                            {
                                "day": [
                                    1
                                ],
                                "exclude": false
                            }
                        ]
                    },
                    "money_value": {
                        "discount_value": {
                            "value": [
                                {
                                    "from_cost": 0,
                                    "discount": 5
                                }
                            ],
                            "value_type": "table"
                        },
                        "max_absolute_value": 50.0
                    }
                }
            ],
            "limits": {
                "id": "discount_without_any_restrictions",
                "daily_limit": {
                    "value": "145000.0000",
                    "threshold": 100
                },
                "weekly_limit": {
                    "value": "1000000.0000",
                    "threshold": 100,
                    "type": "sliding"
                }
            }
        }',
        '33333333-3333-3333-3333-333333333333');
