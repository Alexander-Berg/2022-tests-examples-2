INSERT INTO "operation_calculations"."operations_params"(id,
                                                         tariff_zone,
                                                         tariffs,
                                                         tags,
                                                         branding_types,
                                                         params,
                                                         created_at,
                                                         created_by)
VALUES ('61711eb7b7e4790047d4fe50',
        'moscow',
        '{"econom"}',
        '{}',
        '{"unspecified"}',
        '{
            "tariffs": [
                "econom"
            ],
            "end_date": "2021-10-08",
            "start_date": "2021-10-01",
            "tariff_zone": "moscow",
            "sub_operations": [
                {
                    "week_days": [
                        "mon",
                        "tue",
                        "wed",
                        "thu",
                        "fri"
                    ],
                    "alg_params": {
                        "sub_gmv": 0.05
                    },
                    "branding_type": "unspecified",
                    "sub_operation_id": 0
                },
                {
                    "week_days": [
                        "mon",
                        "tue",
                        "wed",
                        "thu",
                        "fri"
                    ],
                    "alg_params": {
                        "sub_gmv": 0.01
                    },
                    "tag":"a",
                    "branding_type": "unspecified",
                    "sub_operation_id": 1
                },
                {
                    "week_days": [
                        "mon",
                        "tue",
                        "wed",
                        "thu",
                        "fri"
                    ],
                    "alg_params": {
                        "sub_gmv": 0.01
                    },
                    "tag":"c",
                    "branding_type": "unspecified",
                    "sub_operation_id": 2
                },
                {
                    "week_days": [
                        "mon",
                        "tue",
                        "wed",
                        "thu",
                        "fri"
                    ],
                    "alg_params": {
                        "sub_gmv": 0.01
                    },
                    "tag":"immposible",
                    "branding_type": "unspecified",
                    "sub_operation_id": 3
                }
            ],
            "common_alg_params": {
                "m": 5,
                "a1": 3,
                "a2": 4,
                "step": 5,
                "alg_type": "stepwise",
                "maxtrips": 30,
                "has_commission": true,
                "price_increase": 1
            },
            "subvention_end_date": "2022-11-01",
            "subvention_start_date": "2021-11-01"
        }',
        '2021-10-21 05:03:03.546877 +00:00',
        'user');
