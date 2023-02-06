INSERT INTO discounts_operation_calculations.suggests(
    id,
    algorithm_ids,
    author,
    discounts_city,
    draft_url,
    draft_id,
    status,
    statistics,
    multidraft_params,
    created_at,
    updated_at,
    budget,
    date_from,
    date_to,
    with_push,
    calc_segments_params,
    max_absolute_value
)
VALUES (7,
        ARRAY['kt2', 'kt5'],
        NULL,
        'Казань',
        NULL,
        NULL,
        'NOT_PUBLISHED',
        '[[{"y_label": "test_metric_name", "x_label": "Бюджет", "data": [[3239.9408999999996, 318.35294117647055]]}, {"y_label": "Цена дополнительного оффера", "x_label": "Бюджет", "data": [[3239.9408999999996, 149.26556991869967]]}]]',
        '{
    "charts": [
      {
        "algorithm_id": "kt2",
        "plot": {
          "data": [
            [
              50,
              0.0
            ],
            [
              100,
              0.0
            ],
            [
              150,
              0.0
            ],
            [
              200,
              0.0
            ],
            [
              250,
              0.0
            ],
            [
              300,
              0.0
            ],
            [
              350,
              0.0
            ],
            [
              400,
              0.0
            ],
            [
              450,
              0.0
            ],
            [
              500,
              0.0
            ],
            [
              550,
              0.0
            ]
          ],
          "label": "control",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt2",
        "plot": {
          "data": [
            [
              50,
              0.0
            ],
            [
              100,
              0.0
            ],
            [
              150,
              0.0
            ],
            [
              200,
              0.0
            ],
            [
              250,
              0.0
            ],
            [
              300,
              0.0
            ],
            [
              350,
              0.0
            ],
            [
              400,
              0.0
            ],
            [
              450,
              0.0
            ],
            [
              500,
              0.0
            ],
            [
              550,
              0.0
            ]
          ],
          "label": "metrika_active_Hconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt2",
        "plot": {
          "data": [
            [
              50,
              3.0
            ],
            [
              100,
              3.0
            ],
            [
              150,
              3.0
            ],
            [
              200,
              3.0
            ],
            [
              250,
              3.0
            ],
            [
              300,
              3.0
            ],
            [
              350,
              3.0
            ],
            [
              400,
              0.0
            ],
            [
              450,
              0.0
            ],
            [
              500,
              0.0
            ],
            [
              550,
              0.0
            ]
          ],
          "label": "metrika_active_Lconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt2",
        "plot": {
          "data": [
            [
              50,
              3.0
            ],
            [
              100,
              3.0
            ],
            [
              150,
              3.0
            ],
            [
              200,
              0.0
            ],
            [
              250,
              0.0
            ],
            [
              300,
              0.0
            ],
            [
              350,
              0.0
            ],
            [
              400,
              0.0
            ],
            [
              450,
              0.0
            ],
            [
              500,
              0.0
            ],
            [
              550,
              0.0
            ]
          ],
          "label": "metrika_active_Mconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt2",
        "plot": {
          "data": [
            [
              50,
              0.0
            ],
            [
              100,
              0.0
            ],
            [
              150,
              0.0
            ],
            [
              200,
              0.0
            ],
            [
              250,
              0.0
            ],
            [
              300,
              0.0
            ],
            [
              350,
              0.0
            ],
            [
              400,
              0.0
            ],
            [
              450,
              0.0
            ],
            [
              500,
              0.0
            ],
            [
              550,
              0.0
            ]
          ],
          "label": "metrika_notactive_Hconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt2",
        "plot": {
          "data": [
            [
              50,
              3.0
            ],
            [
              100,
              3.0
            ],
            [
              150,
              3.0
            ],
            [
              200,
              3.0
            ],
            [
              250,
              3.0
            ],
            [
              300,
              3.0
            ],
            [
              350,
              3.0
            ],
            [
              400,
              3.0
            ],
            [
              450,
              0.0
            ],
            [
              500,
              0.0
            ],
            [
              550,
              0.0
            ]
          ],
          "label": "metrika_notactive_Lconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt2",
        "plot": {
          "data": [
            [
              50,
              3.0
            ],
            [
              100,
              3.0
            ],
            [
              150,
              3.0
            ],
            [
              200,
              3.0
            ],
            [
              250,
              0.0
            ],
            [
              300,
              0.0
            ],
            [
              350,
              0.0
            ],
            [
              400,
              0.0
            ],
            [
              450,
              0.0
            ],
            [
              500,
              0.0
            ],
            [
              550,
              0.0
            ]
          ],
          "label": "metrika_notactive_Mconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt2",
        "plot": {
          "data": [
            [
              50,
              12.0
            ],
            [
              100,
              12.0
            ],
            [
              150,
              0.0
            ],
            [
              200,
              0.0
            ],
            [
              250,
              0.0
            ],
            [
              300,
              0.0
            ],
            [
              350,
              0.0
            ],
            [
              400,
              0.0
            ],
            [
              450,
              0.0
            ],
            [
              500,
              0.0
            ],
            [
              550,
              0.0
            ]
          ],
          "label": "random",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5fallback",
        "plot": {
          "data": [
            [
              75,
              0
            ],
            [
              625.0,
              0
            ],
            [
              675.0,
              0
            ]
          ],
          "label": "control",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5fallback",
        "plot": {
          "data": [
            [
              75,
              6
            ],
            [
              625.0,
              6
            ],
            [
              675.0,
              0
            ]
          ],
          "label": "metrika_active_Hconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5fallback",
        "plot": {
          "data": [
            [
              75,
              6
            ],
            [
              625.0,
              6
            ],
            [
              675.0,
              0
            ]
          ],
          "label": "metrika_active_Lconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5fallback",
        "plot": {
          "data": [
            [
              75,
              6
            ],
            [
              625.0,
              6
            ],
            [
              675.0,
              0
            ]
          ],
          "label": "metrika_active_Mconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5fallback",
        "plot": {
          "data": [
            [
              75,
              6
            ],
            [
              625.0,
              6
            ],
            [
              675.0,
              0
            ]
          ],
          "label": "metrika_notactive_Hconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5fallback",
        "plot": {
          "data": [
            [
              75,
              6
            ],
            [
              625.0,
              6
            ],
            [
              675.0,
              0
            ]
          ],
          "label": "metrika_notactive_Lconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5fallback",
        "plot": {
          "data": [
            [
              75,
              6
            ],
            [
              625.0,
              6
            ],
            [
              675.0,
              0
            ]
          ],
          "label": "metrika_notactive_Mconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5fallback",
        "plot": {
          "data": [
            [
              75,
              6
            ],
            [
              625.0,
              6
            ],
            [
              675.0,
              0
            ]
          ],
          "label": "random",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5",
        "plot": {
          "data": [
            [
              75,
              30.0
            ],
            [
              125,
              30.0
            ],
            [
              175,
              30.0
            ],
            [
              225,
              30.0
            ],
            [
              275,
              30.0
            ],
            [
              325,
              30.0
            ],
            [
              375,
              30.0
            ],
            [
              425,
              30.0
            ],
            [
              475,
              30.0
            ],
            [
              525,
              30.0
            ],
            [
              575,
              30.0
            ],
            [
              625.0,
              0
            ]
          ],
          "label": "metrika_active_Hconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5",
        "plot": {
          "data": [
            [
              75,
              30.0
            ],
            [
              125,
              30.0
            ],
            [
              175,
              30.0
            ],
            [
              225,
              30.0
            ],
            [
              275,
              30.0
            ],
            [
              325,
              30.0
            ],
            [
              375,
              30.0
            ],
            [
              425,
              30.0
            ],
            [
              475,
              30.0
            ],
            [
              525,
              30.0
            ],
            [
              575,
              30.0
            ],
            [
              625.0,
              0
            ]
          ],
          "label": "metrika_active_Lconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5",
        "plot": {
          "data": [
            [
              75,
              30.0
            ],
            [
              125,
              30.0
            ],
            [
              175,
              30.0
            ],
            [
              225,
              30.0
            ],
            [
              275,
              30.0
            ],
            [
              325,
              30.0
            ],
            [
              375,
              30.0
            ],
            [
              425,
              30.0
            ],
            [
              475,
              30.0
            ],
            [
              525,
              30.0
            ],
            [
              575,
              30.0
            ],
            [
              625.0,
              0
            ]
          ],
          "label": "metrika_active_Mconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5",
        "plot": {
          "data": [
            [
              75,
              30.0
            ],
            [
              125,
              30.0
            ],
            [
              175,
              30.0
            ],
            [
              225,
              30.0
            ],
            [
              275,
              30.0
            ],
            [
              325,
              30.0
            ],
            [
              375,
              30.0
            ],
            [
              425,
              30.0
            ],
            [
              475,
              30.0
            ],
            [
              525,
              30.0
            ],
            [
              575,
              30.0
            ],
            [
              625.0,
              0
            ]
          ],
          "label": "metrika_notactive_Hconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5",
        "plot": {
          "data": [
            [
              75,
              30.0
            ],
            [
              125,
              30.0
            ],
            [
              175,
              30.0
            ],
            [
              225,
              30.0
            ],
            [
              275,
              30.0
            ],
            [
              325,
              30.0
            ],
            [
              375,
              30.0
            ],
            [
              425,
              30.0
            ],
            [
              475,
              30.0
            ],
            [
              525,
              30.0
            ],
            [
              575,
              30.0
            ],
            [
              625.0,
              0
            ]
          ],
          "label": "metrika_notactive_Lconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5",
        "plot": {
          "data": [
            [
              75,
              30.0
            ],
            [
              125,
              30.0
            ],
            [
              175,
              30.0
            ],
            [
              225,
              30.0
            ],
            [
              275,
              30.0
            ],
            [
              325,
              30.0
            ],
            [
              375,
              30.0
            ],
            [
              425,
              30.0
            ],
            [
              475,
              30.0
            ],
            [
              525,
              30.0
            ],
            [
              575,
              30.0
            ],
            [
              625.0,
              0
            ]
          ],
          "label": "metrika_notactive_Mconv",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      },
      {
        "algorithm_id": "kt5",
        "plot": {
          "data": [
            [
              75,
              12.0
            ],
            [
              125,
              12.0
            ],
            [
              175,
              12.0
            ],
            [
              225,
              12.0
            ],
            [
              275,
              12.0
            ],
            [
              325,
              12.0
            ],
            [
              375,
              12.0
            ],
            [
              425,
              12.0
            ],
            [
              475,
              12.0
            ],
            [
              525,
              12.0
            ],
            [
              575,
              12.0
            ],
            [
              625.0,
              0
            ]
          ],
          "label": "random",
          "x_label": "Цена поездки",
          "y_label": "Скидка"
        }
      }
    ],
    "discount_meta": {
      "kt2": {
        "budget_spent": 23511307.080858976,
        "cur_cpeo": 16049.782220100333,
        "fallback_discount": 0,
        "fixed_discounts": [
          {
            "discount_value": 12,
            "segment": "random"
          },
          {
            "discount_value": 0,
            "segment": "control"
          }
        ],
        "segments_meta": {
          "control": {
            "avg_discount": 0.0,
            "budget": 0.0,
            "max_discount_percent": 0.0,
            "max_price_with_discount": 0
          },
          "metrika_active_Hconv": {
            "avg_discount": 0.0,
            "budget": 0.0,
            "max_discount_percent": 0.0,
            "max_price_with_discount": 0
          },
          "metrika_active_Lconv": {
            "avg_discount": 1.1633296302302398,
            "budget": 1184567.55075,
            "max_discount_percent": 3.0,
            "max_price_with_discount": 350
          },
          "metrika_active_Mconv": {
            "avg_discount": 0.5311176948788272,
            "budget": 7400252.866258351,
            "max_discount_percent": 3.0,
            "max_price_with_discount": 150
          },
          "metrika_notactive_Hconv": {
            "avg_discount": 0.0,
            "budget": 0.0,
            "max_discount_percent": 0.0,
            "max_price_with_discount": 0
          },
          "metrika_notactive_Lconv": {
            "avg_discount": 1.215853514844711,
            "budget": 5677170.432170626,
            "max_discount_percent": 3.0,
            "max_price_with_discount": 400
          },
          "metrika_notactive_Mconv": {
            "avg_discount": 0.6710080420941349,
            "budget": 6907508.92368,
            "max_discount_percent": 3.0,
            "max_price_with_discount": 200
          },
          "random": {
            "avg_discount": 1.2359788951514634,
            "budget": 2341807.308,
            "max_discount_percent": 12.0,
            "max_price_with_discount": 100
          }
        },
        "with_push": false
      },
      "kt5": {
        "budget_spent": 16338928.198748117,
        "cur_cpeo": 165.02789808917208,
        "fallback_discount": 6,
        "fixed_discounts": [
          {
            "discount_value": 12,
            "segment": "random"
          },
          {
            "discount_value": 0,
            "segment": "control"
          }
        ],
        "segments_meta": {
          "metrika_active_Hconv": {
            "avg_discount": 0.06187080874299954,
            "budget": 633178.81421775,
            "max_discount_percent": 30.0,
            "max_price_with_discount": 575
          },
          "metrika_active_Lconv": {
            "avg_discount": 0.1295624156649569,
            "budget": 628047.9896714999,
            "max_discount_percent": 30.0,
            "max_price_with_discount": 575
          },
          "metrika_active_Mconv": {
            "avg_discount": 0.09852054220970471,
            "budget": 4711395.398998951,
            "max_discount_percent": 30.0,
            "max_price_with_discount": 575
          },
          "metrika_notactive_Hconv": {
            "avg_discount": 0.06513057738018622,
            "budget": 131613.741,
            "max_discount_percent": 30.0,
            "max_price_with_discount": 575
          },
          "metrika_notactive_Lconv": {
            "avg_discount": 0.14179398890299036,
            "budget": 4247041.21956225,
            "max_discount_percent": 30.0,
            "max_price_with_discount": 575
          },
          "metrika_notactive_Mconv": {
            "avg_discount": 0.11665459986633642,
            "budget": 5710045.26727367,
            "max_discount_percent": 30.0,
            "max_price_with_discount": 575
          },
          "random": {
            "avg_discount": 0.05163811594178587,
            "budget": 277605.768024,
            "max_discount_percent": 12.0,
            "max_price_with_discount": 575
          }
        },
        "with_push": true
      },
      "kt5fallback": {
        "budget_spent": 0,
        "cur_cpeo": 0,
        "fallback_discount": 6,
        "fixed_discounts": [],
        "segments_meta": {},
        "with_push": true
      }
    }
  }',
        '2020-09-07 00:00:00.000000',
        '2020-09-07 00:05:00.000000',
        20000,
        NULL,
        NULL,
        false,
        '{
  "common_params": {
    "companies": [
      "tuda-suda"
    ],
    "discounts_city": "Казань",
    "max_discount": 30,
    "min_discount": 6,
    "payment_methods": [
      "card",
      "bitkoin",
      "cash"
    ],
    "tariffs": [
      "econom",
      "business"
    ]
  },
  "custom_params": [
    {
      "algorithm_id": "kt2",
      "max_surge": 1.31,
      "with_push": false
    },
    {
      "algorithm_id": "kt5",
      "fallback_discount": 6,
      "max_surge": 1.21,
      "with_push": true
    }
  ]
}',
        700
        )
;
