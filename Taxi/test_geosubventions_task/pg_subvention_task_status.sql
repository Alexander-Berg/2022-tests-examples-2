INSERT INTO "operation_calculations"."subvention_task_status" ("id",
                                                               "status",
                                                               "stage",
                                                               "message",
                                                               "updated")
VALUES ('5f9b08b19da21d53ed964473',
        'STARTED',
        'some_stage',
        'some_message',
        '2003-01-08 14:05:06'),
       ('5f9b08b19da21d53ed964474',
        'STARTED',
        'some_stage',
        'some_message',
        '2003-01-08 14:05:06'),
       ('5f9b08b19da21d53ed964490',
        'STARTED',
        'some_stage',
        'some_message',
        '2003-01-08 14:05:06')
;

INSERT INTO "operation_calculations"."subvention_tasks" ("id",
                                                         "task",
                                                         "creator",
                                                         "experimental_conf")
VALUES ('5f9b08b19da21d53ed964473',
        '{
            "rush_hours": {
                "data": {},
                "percentile": 0.65,
                "surge_pwr": 2.2,
                "distance_threshold": 0.3
            },
            "polygons": {
                "data": [],
                "surge_weight_power": 1.3,
                "cost_weight_power": 1.3,
                "eps": 0.028,
                "min_samples": 1,
                "cluster_percent_of_sample": 0.01,
                "alpha_param": 0.007,
                "surge_threshold": 1.2
            },
            "draft_rules": [],
            "data_loader": {
                "date_from": "2020-12-15 15:20:47",
                "date_to": "2020-12-29 15:20:47",
                "tariff_zones": [
                    "kaluga"
                ],
                "tariffs": [
                    "econom"
                ]
            },
            "budget": {
                "how_apply": "driver"
            }
        }'::jsonb,
        'amneziya',
        NULL),
       ('5f9b08b19da21d53ed964474',
        '{
            "rush_hours": {
                "data": {},
                "percentile": 0.65,
                "surge_pwr": 2.2,
                "distance_threshold": 0.3
            },
            "polygons": {
                "data": [],
                "surge_weight_power": 1.3,
                "cost_weight_power": 1.3,
                "eps": 0.028,
                "min_samples": 1,
                "cluster_percent_of_sample": 0.01,
                "alpha_param": 0.007,
                "surge_threshold": 1.2
            },
            "draft_rules": [],
            "data_loader": {
                "date_from": "2020-12-15 15:20:47",
                "date_to": "2020-12-29 15:20:47",
                "tariff_zones": [
                    "kaluga"
                ],
                "tariffs": [
                    "econom"
                ]
            },
            "budget": {
                "how_apply": "driver"
            }
        }'::jsonb,
        'amneziya',
        '{
            "time_m5_money_m10": {
                "share": 0.11,
                "shift_guarantee": -10,
                "shift_interval": -5
            },
            "geotool_empty": {
                "share": 0.5,
                "is_empty": true
            }
        }'::jsonb),
       ('5f9b08b19da21d53ed964490',
        '{
            "budget": {
                "how_apply": "driver",
                "budget_scale": 1
            },
            "polygons": {
                "eps": 0.028,
                "data": [
                    {
                        "id": "618d10858d2606004715b9b7pol0",
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [
                                        36,
                                        54
                                    ],
                                    [
                                        36,
                                        55
                                    ],
                                    [
                                        37,
                                        55
                                    ],
                                    [
                                        37,
                                        54
                                    ],
                                    [
                                        36,
                                        54
                                    ]
                                ]
                            ]
                        },
                        "properties": {
                            "name": "pol0"
                        }
                    },
                    {
                        "id": "subgmv_test_618d10858d2606004715b9b7pol1",
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [
                                        22,
                                        22
                                    ],
                                    [
                                        24,
                                        22
                                    ],
                                    [
                                        24,
                                        24
                                    ],
                                    [
                                        22,
                                        24
                                    ],
                                    [
                                        22,
                                        22
                                    ]
                                ]
                            ]
                        },
                        "properties": {
                            "name": "pol1"
                        }
                    }
                ],
                "alpha_param": 0.007,
                "min_samples": 1,
                "surge_threshold": 1.2,
                "cost_weight_power": 0,
                "surge_weight_power": 1.3,
                "cluster_percent_of_sample": 0.03
            },
            "tag_conf": {
                "main_tag": "",
                "current_rules_tags": []
            },
            "rush_hours": {
                "data": {
                    "0": [
                        {
                            "end_time": "11:00",
                            "start_time": "07:00",
                            "end_dayofweek": 0,
                            "start_dayofweek": 0
                        },
                        {
                            "end_time": "15:00",
                            "start_time": "12:00",
                            "end_dayofweek": 1,
                            "start_dayofweek": 1
                        },
                        {
                            "end_time": "22:00",
                            "start_time": "18:00",
                            "end_dayofweek": 2,
                            "start_dayofweek": 2
                        },
                        {
                            "end_time": "18:00",
                            "start_time": "16:00",
                            "end_dayofweek": 2,
                            "start_dayofweek": 2
                        }
                    ]
                }
            },
            "data_loader": {
                "date_to": "2020-12-29 15:20:47",
                "tariffs": [
                    "econom"
                ],
                "date_from": "2020-12-15 15:20:47",
                "tariff_zones": [
                    "kaluga"
                ]
            },
            "draft_rules": [
                {
                    "geoareas": [
                        "618d10858d2606004715b9b7pol0"
                    ],
                    "interval": {
                        "end_time": "11:00",
                        "start_time": "07:00",
                        "end_dayofweek": 0,
                        "start_dayofweek": 0
                    },
                    "rule_sum": 135,
                    "rule_type": "guarantee",
                    "categories": [
                        "econom"
                    ]
                },
                {
                    "geoareas": [
                        "618d10858d2606004715b9b7pol0"
                    ],
                    "interval": {
                        "end_time": "15:00",
                        "start_time": "12:00",
                        "end_dayofweek": 1,
                        "start_dayofweek": 1
                    },
                    "rule_sum": 140,
                    "rule_type": "guarantee",
                    "categories": [
                        "econom"
                    ]
                },
                {
                    "geoareas": [
                        "subgmv_test_618d10858d2606004715b9b7pol1"
                    ],
                    "interval": {
                        "end_time": "22:00",
                        "start_time": "18:00",
                        "end_dayofweek": 2,
                        "start_dayofweek": 2
                    },
                    "rule_sum": 200,
                    "rule_type": "guarantee",
                    "categories": [
                        "econom"
                    ],
                    "is_changed" : true,
                    "rule_mode": "subgmv",
                    "rule_value": 1
                },
                {
                    "geoareas": [
                        "subgmv_test_618d10858d2606004715b9b7pol1"
                    ],
                    "interval": {
                        "end_time": "18:00",
                        "start_time": "16:00",
                        "end_dayofweek": 2,
                        "start_dayofweek": 2
                    },
                    "rule_sum": 200,
                    "rule_type": "guarantee",
                    "categories": [
                        "econom"
                    ],
                    "is_changed" : true,
                    "rule_mode": "quantile",
                    "rule_value": 0.75
                },
                {
                    "geoareas": [
                        "618d10858d2606004715b9b7pol0"
                    ],
                    "interval": {
                        "end_time": "22:00",
                        "start_time": "18:00",
                        "end_dayofweek": 2,
                        "start_dayofweek": 2
                    },
                    "rule_sum": 135,
                    "is_changed" : false,
                    "rule_type": "guarantee",
                    "categories": [
                        "econom"
                    ]
                }
            ]
        }'::jsonb,
        'dpano',
        NULL),
       ('5f9b08b19da21d53ed964491',
        '{
            "budget": {
                "how_apply": "driver",
                "budget_scale": 1
            },
            "polygons": {
                "eps": 0.028,
                "data": [
                    {
                        "id": "test_pol0",
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [
                                        0.5,
                                        0.5
                                    ],
                                    [
                                        0.5,
                                        -0.5
                                    ],
                                    [
                                        -0.5,
                                        -0.5
                                    ],
                                    [
                                        -0.5,
                                        0.5
                                    ],
                                    [
                                        0.5,
                                        0.5
                                    ]
                                ]
                            ]
                        },
                        "properties": {
                            "name": "pol0"
                        }
                    }
                ],
                "alpha_param": 0.007,
                "min_samples": 1,
                "surge_threshold": 1.2,
                "cost_weight_power": 0,
                "surge_weight_power": 1.3,
                "cluster_percent_of_sample": 0.03
            },
            "tag_conf": {
                "main_tag": "",
                "current_rules_tags": []
            },
            "rush_hours": {
                "data": {
                    "0": [
                        {
                            "end_time": "11:00",
                            "start_time": "07:00",
                            "end_dayofweek": 0,
                            "start_dayofweek": 0
                        },
                        {
                            "end_time": "15:00",
                            "start_time": "12:00",
                            "end_dayofweek": 1,
                            "start_dayofweek": 1
                        },
                        {
                            "end_time": "22:00",
                            "start_time": "18:00",
                            "end_dayofweek": 2,
                            "start_dayofweek": 2
                        }
                    ]
                }
            },
            "data_loader": {
                "date_to": "2020-12-29 00:00:00",
                "tariffs": [
                    "econom"
                ],
                "date_from": "2020-12-28 00:00:00",
                "tariff_zones": [
                    "moscow"
                ]
            },
            "draft_rules": [
                {
                    "geoareas": [
                        "test_pol0"
                    ],
                    "interval": {
                        "end_time": "11:00",
                        "start_time": "07:00",
                        "end_dayofweek": 0,
                        "start_dayofweek": 0
                    },
                    "rule_sum": 135,
                    "rule_type": "guarantee",
                    "categories": [
                        "econom"
                    ]
                },

                {
                    "geoareas": [
                        "test_pol0"
                    ],
                    "interval": {
                        "end_time": "15:00",
                        "start_time": "12:00",
                        "end_dayofweek": 1,
                        "start_dayofweek": 1
                    },
                    "rule_sum": 140,
                    "rule_type": "guarantee",
                    "categories": [
                        "econom"
                    ]
                },

                {
                    "geoareas": [
                        "test_pol0"
                    ],
                    "interval": {
                        "end_time": "22:00",
                        "start_time": "18:00",
                        "end_dayofweek": 2,
                        "start_dayofweek": 2
                    },
                    "rule_sum": 135,
                    "rule_type": "guarantee",
                    "categories": [
                        "econom"
                    ]
                }
            ]
        }'::jsonb,
        'afushta',
        NULL),
       ('5f9b08b19da21d53ed964492',
        '{
            "budget": {
                "how_apply": "driver",
                "budget_scale": 1
            },
            "polygons": {
                "eps": 0.028,
                "data": [
                    {
                        "id": "invalid_pol0",
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [
                                        36,
                                        54
                                    ],
                                    [
                                        40,
                                        54
                                    ],
                                    [
                                        36,
                                        54.00001
                                    ],
                                    [
                                        36,
                                        55
                                    ],
                                    [
                                        37,
                                        55
                                    ],
                                    [
                                        37,
                                        54
                                    ],
                                    [
                                        36,
                                        54
                                    ]
                                ]
                            ]
                        },
                        "properties": {
                            "name": "pol0"
                        }
                    },
                    {
                        "id": "invalid_pol1",
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [
                                        36,
                                        54
                                    ],
                                    [
                                        36,
                                        55
                                    ],
                                    [
                                        37,
                                        55
                                    ],
                                    [
                                        37,
                                        54
                                    ]
                                ]
                            ]
                        },
                        "properties": {
                            "name": "pol1"
                        }
                    },
                    {
                        "id": "invalid_pol2",
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [36, 54],
                                    [36, 55],
                                    [37, 55],
                                    [37, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54],
                                    [36, 54]
                                ]
                            ]
                        },
                        "properties": {
                            "name": "pol1"
                        }
                    },
                    {
                        "id": "invalid_pol3",
                        "type": "Feature",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [
                                        30.448816338319393,
                                        59.94286669032621
                                    ],
                                    [
                                        30.44379837042361,
                                        59.94151353213884
                                    ],
                                    [
                                        30.436271418579935,
                                        59.9388072157641
                                    ],
                                    [
                                        30.431253450684153,
                                        59.93610089938936
                                    ],
                                    [
                                        30.42623548278837,
                                        59.93339458301462
                                    ],
                                    [
                                        30.421217514892586,
                                        59.92662879207777
                                    ],
                                    [
                                        30.416199546996804,
                                        59.9252756338904
                                    ],
                                    [
                                        30.411181579101022,
                                        59.92256931751566
                                    ],
                                    [
                                        30.40616361120524,
                                        59.92256931751566
                                    ],
                                    [
                                        30.401145643309455,
                                        59.92392247570303
                                    ],
                                    [
                                        30.396127675413673,
                                        59.92662879207777
                                    ],
                                    [
                                        30.39110970751789,
                                        59.92933510845251
                                    ],
                                    [
                                        30.383582755674215,
                                        59.93204142482725
                                    ],
                                    [
                                        30.38860072357,
                                        59.93610089938936
                                    ],
                                    [
                                        30.39110970751789,
                                        59.94286669032621
                                    ],
                                    [
                                        30.396127675413673,
                                        59.94151353213884
                                    ],
                                    [
                                        30.398636659361564,
                                        59.94963248126306
                                    ],
                                    [
                                        30.403654627257346,
                                        59.9523387976378
                                    ],
                                    [
                                        30.40616361120524,
                                        59.9523387976378
                                    ],
                                    [
                                        30.411181579101022,
                                        59.95098563945043
                                    ],
                                    [
                                        30.416199546996804,
                                        59.9523387976378
                                    ],
                                    [
                                        30.421217514892586,
                                        59.95504511401254
                                    ],
                                    [
                                        30.42184476087956,
                                        59.956736561746744
                                    ],
                                    [
                                        30.416199546996804,
                                        59.95369195582517
                                    ],
                                    [
                                        30.42372649884048,
                                        59.957751430387276
                                    ],
                                    [
                                        30.42623548278837,
                                        59.96316406313676
                                    ],
                                    [
                                        30.428744466736262,
                                        59.96316406313676
                                    ],
                                    [
                                        30.433762434632044,
                                        59.96181090494939
                                    ],
                                    [
                                        30.430835286692837,
                                        59.96260024722535
                                    ],
                                    [
                                        30.42623548278837,
                                        59.95639827219991
                                    ],
                                    [
                                        30.431253450684153,
                                        59.95639827219991
                                    ],
                                    [
                                        30.436271418579935,
                                        59.95639827219991
                                    ],
                                    [
                                        30.441289386475717,
                                        59.95639827219991
                                    ],
                                    [
                                        30.446307354371502,
                                        59.95504511401254
                                    ],
                                    [
                                        30.451325322267284,
                                        59.9523387976378
                                    ],
                                    [
                                        30.458852274110956,
                                        59.95098563945043
                                    ],
                                    [
                                        30.468888209902524,
                                        59.94963248126306
                                    ],
                                    [
                                        30.473906177798305,
                                        59.94827932307569
                                    ],
                                    [
                                        30.48143312964198,
                                        59.94692616488832
                                    ],
                                    [
                                        30.486451097537763,
                                        59.94692616488832
                                    ],
                                    [
                                        30.473906177798305,
                                        59.94286669032621
                                    ],
                                    [
                                        30.468888209902524,
                                        59.94286669032621
                                    ],
                                    [
                                        30.46136125805885,
                                        59.944219848513576
                                    ],
                                    [
                                        30.456343290163066,
                                        59.944219848513576
                                    ],
                                    [
                                        30.448816338319393,
                                        59.94286669032621
                                    ]
                                ]
                            ]
                        },
                        "properties": {
                            "name": "pol1"
                        }
                    }
                ],
                "alpha_param": 0.007,
                "min_samples": 1,
                "surge_threshold": 1.2,
                "cost_weight_power": 0,
                "surge_weight_power": 1.3,
                "cluster_percent_of_sample": 0.03
            },
            "tag_conf": {
                "main_tag": "",
                "current_rules_tags": []
            },
            "rush_hours": {
                "data": {
                    "0": [
                        {
                            "end_time": "11:00",
                            "start_time": "07:00",
                            "end_dayofweek": 0,
                            "start_dayofweek": 0
                        },
                        {
                            "end_time": "15:00",
                            "start_time": "12:00",
                            "end_dayofweek": 1,
                            "start_dayofweek": 1
                        },
                        {
                            "end_time": "22:00",
                            "start_time": "18:00",
                            "end_dayofweek": 2,
                            "start_dayofweek": 2
                        }
                    ]
                }
            },
            "data_loader": {
                "date_to": "2020-12-29 15:20:47",
                "tariffs": [
                    "econom"
                ],
                "date_from": "2020-12-15 15:20:47",
                "tariff_zones": [
                    "kaluga"
                ]
            },
            "draft_rules": [
                {
                    "geoareas": [
                        "618d10858d2606004715b9b7pol0"
                    ],
                    "interval": {
                        "end_time": "11:00",
                        "start_time": "07:00",
                        "end_dayofweek": 0,
                        "start_dayofweek": 0
                    },
                    "rule_sum": 135,
                    "rule_type": "guarantee",
                    "categories": [
                        "econom"
                    ]
                },

                {
                    "geoareas": [
                        "618d10858d2606004715b9b7pol0"
                    ],
                    "interval": {
                        "end_time": "15:00",
                        "start_time": "12:00",
                        "end_dayofweek": 1,
                        "start_dayofweek": 1
                    },
                    "rule_sum": 140,
                    "rule_type": "guarantee",
                    "categories": [
                        "econom"
                    ]
                },

                {
                    "geoareas": [
                        "618d10858d2606004715b9b7pol0"
                    ],
                    "interval": {
                        "end_time": "22:00",
                        "start_time": "18:00",
                        "end_dayofweek": 2,
                        "start_dayofweek": 2
                    },
                    "rule_sum": 135,
                    "rule_type": "guarantee",
                    "categories": [
                        "econom"
                    ]
                }
            ]
        }'::jsonb,
        'dpano',
        NULL);


INSERT INTO operation_calculations.geosubventions_tasks_counter(id,
                                                                retry_cnt)
VALUES ('5f9b08b19da21d53ed964473',
        1);
