INSERT INTO discounts_operation_calculations.suggests(
    id,
    algorithm_ids,
    author,
    discounts_city,
    draft_url,
    draft_id,
    status,
    created_at,
    updated_at,
    statistics,
    multidraft_params,
    budget
)
VALUES (1, ARRAY['kt1'], 'eugenest', 'Москва', 'https://ya.ru/123', 123, 'NEED_APPROVAL', '2020-08-10 23:43:21', '2020-08-10 23:53:21', '[]', '{}', 100500),
       (2, ARRAY['kt1', 'kt2'], 'shedx', 'Санкт-Петербург', 'https://ya.ru/15', 15, 'REJECTED', '2020-08-09 18:21:04', '2020-08-10 10:14:04', '[]', '{}', 1000),
       (3, ARRAY['kt1', 'test'], NULL, 'Москва', NULL, NULL, 'NOT_PUBLISHED', '2020-08-08 17:23:11', '2020-08-09 12:23:01', '[]', '{}', 2000),
       (
        4,
        ARRAY['kt2'],
        'artem-mazanov',
        'Москва',
        'https://ya.ru/42',
        42,
        'SUCCEEDED',
        '2020-08-11 19:25:58',
        '2020-08-12 02:55:10',
        '[[{"y_label": "test_metric_name", "x_label": "Бюджет", "data": [[3239.9408999999996, 318.35294117647055]]}, {"y_label": "Цена дополнительного оффера", "x_label": "Бюджет", "data": [[3239.9408999999996, 149.26556991869967]]}]]',
        '{"charts": [{"plot": {"x_label": "Цена поездки", "y_label": "Скидка", "data": [[25, 3.0], [50, 2.0]], "label": "test_segment"}, "algorithm_id": "kt2"}],
        "discount_meta": {
            "kt2": {
              "budget_spent": 45326175.24480001,
              "cur_cpeo": 7619.925805238771,
              "fallback_discount": 0,
              "fixed_discounts": [
                {
                  "discount_value": 0,
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
                  "budget": 34690759.87200001
                },
                "random": {
                  "avg_discount": 3.066118618310774,
                  "budget": 10635415.372800002
                }
              },
              "with_push": false
            }
        }}',
        45326175.24480001
        ),
        (
        5,
        ARRAY['kt6', 'test2'],
        'artem-mazanov',
        'Нижний Тагил',
        'https://ya.ru/110',
        110,
        'SUCCEEDED',
        '2020-08-05 17:23:11',
        '2020-08-06 02:55:10',
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
          "budget": 34690759.87200001
        },
        "random": {
          "avg_discount": 3.066118618310774,
          "budget": 10635415.372800002
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
          "budget": 16935017.664
        },
        "random": {
          "avg_discount": 4.0566636962837395,
          "budget": 7084266.9312
        }
      },
      "with_push": false
    }
  }
}',
        69345459.84
        ),
        (
        6,
        ARRAY['kt2'],
        'artem-mazanov',
        'Санкт-Петербург',
        'https://ya.ru/426',
        426,
        'WAITING_TO_STOP',
        '2020-07-11 19:25:58',
        '2020-07-13 02:55:10',
        '[[{"y_label": "test_metric_name", "x_label": "Бюджет", "data": [[3239.9408999999996, 318.35294117647055]]}, {"y_label": "Цена дополнительного оффера", "x_label": "Бюджет", "data": [[3239.9408999999996, 149.26556991869967]]}]]',
        '{"charts": [{"plot": {"x_label": "Цена поездки", "y_label": "Скидка", "data": [[25, 3.0], [50, 2.0]], "label": "test_segment"}, "algorithm_id": "kt2"}]}',
        120000
        )
;
