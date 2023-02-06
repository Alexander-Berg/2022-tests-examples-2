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
                    "sub_operation_id": 1
                }
            ],
            "common_alg_params": {
                "m": 5,
                "a1": 3,
                "a2": 4,
                "step": 5,
                "alg_type": "stepwise",
                "maxtrips": 30,
                "has_commission": false,
                "price_increase": 1
            },
            "subvention_end_date": "2022-11-01",
            "subvention_start_date": "2021-11-01"
        }',
        '2021-10-21 05:03:03.546877 +00:00',
        'user'),
       ('61711eb7b7e4790047d4fe51',
        'moscow',
        '{"econom", "comfort"}',
        '{}',
        '{"sticker"}',
        '{
            "tariffs": [
                "econom",
                "comfort"
            ],
            "end_date": "2021-10-08",
            "start_date": "2021-10-01",
            "tariff_zone": "moscow",
            "sub_operations": [
                {
                    "week_days": [
                        "sat",
                        "sun"
                    ],
                    "alg_params": {
                        "sub_gmv": 0.05
                    },
                    "branding_type": "sticker",
                    "sub_operation_id": 1
                },
                {
                    "week_days": [
                        "sat",
                        "sun"
                    ],
                    "alg_params": {
                        "sub_gmv": 0.05
                    },
                    "branding_type": "sticker",
                    "sub_operation_id": 2
                }
            ],
            "common_alg_params": {
                "m": 5,
                "a1": 3,
                "a2": 4,
                "step": 5,
                "alg_type": "continuous",
                "maxtrips": 15,
                "has_commission": true,
                "price_increase": 1
            },
            "subvention_end_date": "2022-12-01",
            "subvention_start_date": "2021-12-01"
        }',
        '2021-10-21 06:03:03 +00:00',
        'user_2'),
       ('61711eb7b7e4790047d4fe52',
        'spb',
        '{"econom"}',
        '{"super_tag"}',
        '{"unspecified"}',
        '{
            "tariffs": [
                "econom"
            ],
            "end_date": "2021-10-08",
            "start_date": "2021-10-01",
            "tariff_zone": "spb",
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
                    "sub_operation_id": 1
                }
            ],
            "common_alg_params": {
                "m": 5,
                "a1": 3,
                "a2": 4,
                "step": 5,
                "alg_type": "stepwise",
                "maxtrips": 30,
                "has_commission": false,
                "price_increase": 1
            },
            "subvention_end_date": "2022-11-01",
            "subvention_start_date": "2021-11-01",
            "tag": "super_tag"
        }',
        '2021-10-21 05:03:03.546877 +00:00',
        'user_2'),
       ('62541f18637ede004af0cbdc', 'novosibirsk', '{selfdriving}', '{}', '{unspecified}', '{
           "tariffs": [
               "selfdriving"
           ],
           "end_date": "2022-04-10",
           "start_date": "2022-03-27",
           "tariff_zone": "novosibirsk",
           "sub_operations": [
               {
                   "week_days": [
                       "mon",
                       "tue",
                       "wed",
                       "thu",
                       "fri",
                       "sat",
                       "sun"
                   ],
                   "alg_params": {
                       "sub_gmv": 0.01
                   },
                   "guarantees": [
                       {
                           "guarantee": 10,
                           "count_trips": 1
                       }
                   ],
                   "min_activity": 0,
                   "branding_type": "unspecified",
                   "sub_operation_id": 0
               }
           ],
           "common_alg_params": {
               "a1": 0,
               "alg_type": "continuous",
               "maxtrips": 1,
               "round_to": 25,
               "has_commission": true,
               "price_increase": 1
           },
           "subvention_end_date": "2022-04-26",
           "subvention_start_date": "2022-04-12"
       }', '2022-04-11 09:29:12.277726 +00:00', 'dpano');
