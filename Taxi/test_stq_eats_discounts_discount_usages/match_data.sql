INSERT INTO eats_discounts.match_data (data_id, series_id, data)
VALUES (1,
        '11111111-1111-1111-1111-111111111111',
        '{
          "name": "with_restrictions",
          "discount_usage_restrictions": [
            {
              "max_count": 1
            }
          ],
          "values_with_schedules": [
            {
              "schedule": {
                "timezone": "UTC",
                "intervals": [
                  {
                    "day": [
                      1,
                      2,
                      3,
                      4,
                      5,
                      6,
                      7
                    ],
                    "exclude": false
                  },
                  {
                    "daytime": [
                      {
                        "to": "23:59:59"
                      }
                    ],
                    "exclude": false
                  }
                ]
              },
              "product_value": {
                "value": [
                  {
                    "step": {
                      "discount": "100.000000",
                      "from_cost": "10.000000"
                    },
                    "bundle": 1,
                    "products": [
                      {
                        "id": "536189040"
                      }
                    ]
                  }
                ]
              }
            }
          ]
        }'),
       (2,
        '22222222-2222-2222-2222-222222222222',
        '{
          "name": "without_restrictions",
          "values_with_schedules": [
            {
              "schedule": {
                "timezone": "UTC",
                "intervals": [
                  {
                    "day": [
                      1,
                      2,
                      3,
                      4,
                      5,
                      6,
                      7
                    ],
                    "exclude": false
                  },
                  {
                    "daytime": [
                      {
                        "to": "23:59:59"
                      }
                    ],
                    "exclude": false
                  }
                ]
              },
              "product_value": {
                "value": [
                  {
                    "step": {
                      "discount": "100.000000",
                      "from_cost": "10.000000"
                    },
                    "bundle": 1,
                    "products": [
                      {
                        "id": "536189040"
                      }
                    ]
                  }
                ]
              }
            }
          ]
        }'),
       (3,
        '22222222-2222-2222-2222-222222222222',
        '{
            "name": "with_limit",
            "limit": {
                "closing_threshold": 10,
                "currency": "RUB",
                "value": "600"
            },
            "values_with_schedules": [
                {
                    "schedule": {
                        "timezone": "UTC",
                        "intervals": [
                            {
                                "day": [
                                    1,
                                    2,
                                    3,
                                    4,
                                    5,
                                    6,
                                    7
                                ],
                                "exclude": false
                            },
                            {
                                "daytime": [
                                    {
                                        "to": "23:59:59"
                                    }
                                ],
                                "exclude": false
                            }
                        ]
                    },
                    "product_value": {
                        "value": [
                            {
                                "step": {
                                    "discount": "100.000000",
                                    "from_cost": "10.000000"
                                },
                                "bundle": 1,
                                "products": [
                                    {
                                        "id": "536189040"
                                    }
                                ]
                            }
                        ]
                    }
                }
            ]
        }');
