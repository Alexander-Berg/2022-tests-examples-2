INSERT INTO discounts_operation_calculations.suggests(
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
    with_push
)
VALUES ('{"kt2"}',
        'another_user',
        'Москва',
        'ya.ru/99',
        99,
        'SUCCEEDED',
        '[]',
        '{}',
        '2020-09-01 00:00:00.000000',
        '2020-09-01 00:00:20.000000',
        10000,
        '2020-09-01 01:00:00',
        '2021-09-01 01:00:00',
        false
       ),
       ('{"kt2"}',
        NULL,
        'Москва',
        NULL,
        NULL,
        'NOT_PUBLISHED',
        '[[{"y_label": "test_metric_name", "x_label": "Бюджет", "data": [[3239.9408999999996, 318.35294117647055]]}, {"y_label": "Цена дополнительного оффера", "x_label": "Бюджет", "data": [[3239.9408999999996, 149.26556991869967]]}]]',
        '{"charts": [{"plot": {"x_label": "Цена поездки", "y_label": "Скидка", "data": [[25, 3.0], [50, 2.0]], "label": "test_segment"}, "algorithm_id": "kt2"}, {"plot": {"x_label": "Цена поездки", "y_label": "Скидка", "data": [[25, 5.0], [50, 3.0]], "label": "test_segment2"}, "algorithm_id": "kt2"}], "discount_meta": {"kt2": {"budget_spent": 3239.9408999999996, "cur_cpeo": 149.26556991869984, "segments_meta": {"test_segment": {"avg_discount": 0.03, "budget": 2915.94681}}}}}',
        '2020-09-07 00:00:00.000000',
        '2020-09-07 00:05:00.000000',
        20000,
        NULL,
        NULL,
        false
        ),
        (
        ARRAY['kt6', 'test2'],
        'artem-mazanov',
        'Нижний Тагил',
        'https://ya.ru/103',
        103,
        'SUCCEEDED',
        '[[{"y_label": "test_metric_name", "x_label": "Бюджет", "data": [[3239.9408999999996, 318.35294117647055]]}, {"y_label": "Цена дополнительного оффера", "x_label": "Бюджет", "data": [[3239.9408999999996, 149.26556991869967]]}]]',
        '{
  "charts": [
    {
      "algorithm_id": "kt6",
      "plot": {
        "data": [
          [
            25,
            3.0
          ],
          [
            50,
            2.0
          ]
        ],
        "label": "random",
        "x_label": "Цена поездки",
        "y_label": "Скидка"
      }
    },
    {
      "algorithm_id": "kt6",
      "plot": {
        "data": [
          [
            25,
            3.0
          ],
          [
            50,
            2.0
          ]
        ],
        "label": "control",
        "x_label": "Цена поездки",
        "y_label": "Скидка"
      }
    },
    {
      "algorithm_id": "test2",
      "plot": {
        "data": [
          [
            25,
            3.0
          ],
          [
            50,
            2.0
          ]
        ],
        "label": "random",
        "x_label": "Цена поездки",
        "y_label": "Скидка"
      }
    },
    {
      "algorithm_id": "test2",
      "plot": {
        "data": [
          [
            25,
            6.0
          ],
          [
            50,
            0.0
          ]
        ],
        "label": "control",
        "x_label": "Цена поездки",
        "y_label": "Скидка"
      }
    },
    {
      "algorithm_id": "kt6fallback",
      "plot": {
        "data": [
          [
            50,
            3
          ],
          [
            700,
            3
          ],
          [
            750,
            0
          ]
        ],
        "label": "control",
        "x_label": "Цена поездки",
        "y_label": "Скидка"
      }
    },
    {
      "algorithm_id": "kt6fallback",
      "plot": {
        "data": [
          [
            50,
            3
          ],
          [
            700,
            3
          ],
          [
            750,
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
    "kt6": {
      "budget_spent": 45326175.24480001,
      "cur_cpeo": 7619.925805238771,
      "fallback_discount": 3,
      "fixed_discounts": [
        {
          "discount_value": 6,
          "segment": "control"
        },
        {
          "discount_value": 12,
          "segment": "random"
        }
      ],
      "segments_meta": {
        "control": {
          "avg_discount": 0.40942267441448776,
          "budget": 34690759.87200001,
          "max_price_with_discount": 50,
          "max_discount_percent": 3.0
        },
        "random": {
          "avg_discount": 3.066118618310774,
          "budget": 10635415.372800002,
          "max_price_with_discount": 50,
          "max_discount_percent": 3.0
        }
      },
      "with_push": true
    },
    "kt6fallback": {
      "budget_spent": 0,
      "cur_cpeo": 0,
      "fallback_discount": 3,
      "fixed_discounts": [],
      "segments_meta": {},
      "with_push": true
    },
    "test2": {
      "budget_spent": 24019284.595200002,
      "cur_cpeo": 11975.623981732246,
      "fallback_discount": null,
      "fixed_discounts": [
        {
          "discount_value": 6,
          "segment": "control"
        },
        {
          "discount_value": 12,
          "segment": "random"
        }
      ],
      "segments_meta": {
        "control": {
          "avg_discount": 0.39973642830739947,
          "budget": 16935017.664,
          "max_price_with_discount": 25,
          "max_discount_percent": 6.0
        },
        "random": {
          "avg_discount": 4.0566636962837395,
          "budget": 7084266.9312,
          "max_price_with_discount": 50,
          "max_discount_percent": 3.0
        }
      },
      "with_push": false
    }
  }
}',
        '2020-08-11 19:25:58',
        '2020-08-12 02:55:10',
        69345459.84,
        '2020-09-23T12:49:22.373412Z',
        '2020-10-07T12:49:22.373412Z',
        true
        ),
        ('{"kt5"}',
        NULL,
        'Нижний Тагил',
        NULL,
        NULL,
        'NOT_PUBLISHED',
        '[[{"y_label": "test_metric_name", "x_label": "Бюджет", "data": [[3239.9408999999996, 318.35294117647055]]}, {"y_label": "Цена дополнительного оффера", "x_label": "Бюджет", "data": [[3239.9408999999996, 149.26556991869967]]}]]',
        '{
  "charts": [
    {
      "algorithm_id": "kt5",
      "plot": {
        "data": [
          [
            25,
            3.0
          ],
          [
            50,
            2.0
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
            25,
            3.0
          ],
          [
            50,
            2.0
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
            50,
            3
          ],
          [
            700,
            3
          ],
          [
            750,
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
            50,
            3
          ],
          [
            700,
            3
          ],
          [
            750,
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
    "kt5": {
      "budget_spent": 45326175.24480001,
      "cur_cpeo": 7619.925805238771,
      "fallback_discount": 3,
      "fixed_discounts": [
        {
          "discount_value": 6,
          "segment": "control"
        },
        {
          "discount_value": 12,
          "segment": "random"
        }
      ],
      "segments_meta": {
        "control": {
          "avg_discount": 0.40942267441448776,
          "budget": 34690759.87200001,
          "max_price_with_discount": 50,
          "max_discount_percent": 3.0
        },
        "random": {
          "avg_discount": 3.066118618310774,
          "budget": 10635415.372800002,
          "max_price_with_discount": 50,
          "max_discount_percent": 3.0
        }
      },
      "with_push": true
    },
    "kt5fallback": {
      "budget_spent": 0,
      "cur_cpeo": 0,
      "fallback_discount": 3,
      "fixed_discounts": [],
      "segments_meta": {},
      "with_push": true
    }
  }
}',
        '2020-09-07 00:00:00.000000',
        '2020-09-07 00:05:00.000000',
        69345459.84,
        NULL,
        NULL,
        true
        ),
        ('{"kt2"}',
        'another_user',
        'Санкт-Петербург',
        'ya.ru/99',
        999,
        'NEED_APPROVAL',
        '[]',
        '{}',
        '2020-09-01 00:00:00.000000',
        '2020-09-01 00:00:20.000000',
        10000,
        '2020-09-01 01:00:00',
        '2021-09-01 01:00:00',
        false
       ),
       ('{"kt2"}',
        NULL,
        'Санкт-Петербург',
        NULL,
        NULL,
        'NOT_PUBLISHED',
        '[[{"y_label": "test_metric_name", "x_label": "Бюджет", "data": [[3239.9408999999996, 318.35294117647055]]}, {"y_label": "Цена дополнительного оффера", "x_label": "Бюджет", "data": [[3239.9408999999996, 149.26556991869967]]}]]',
        '{"charts": [{"plot": {"x_label": "Цена поездки", "y_label": "Скидка", "data": [[25, 3.0], [50, 2.0]], "label": "test_segment"}, "algorithm_id": "kt2"}, {"plot": {"x_label": "Цена поездки", "y_label": "Скидка", "data": [[25, 5.0], [50, 3.0]], "label": "test_segment2"}, "algorithm_id": "kt2"}], "discount_meta": {"kt2": {"budget_spent": 3239.9408999999996, "cur_cpeo": 149.26556991869984, "segments_meta": {"test_segment": {"avg_discount": 0.03, "budget": 2915.94681}}}}}',
        '2020-09-07 00:00:00.000000',
        '2020-09-07 00:05:00.000000',
        20000,
        NULL,
        NULL,
        false
        )
;
