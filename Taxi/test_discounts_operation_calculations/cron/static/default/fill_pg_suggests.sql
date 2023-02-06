INSERT INTO discounts_operation_calculations.suggests(
    id,
    algorithm_ids,
    author,
    discounts_city,
    draft_url,
    draft_id,
    previous_suggest_id,
    status,
    created_at,
    updated_at,
    statistics,
    multidraft_params,
    date_from,
    date_to,
    with_push
)
VALUES (1, ARRAY['kt1'], 'eugenest', 'Москва', 'https://ya.ru/123', 123, NULL, 'NEED_APPROVAL', '2020-08-10 23:43:21', '2020-08-10 23:53:21', '{}', '{}', NULL, '2020-08-18T12:49:22.373412Z', false),
       (2, ARRAY['kt1', 'kt2'], 'shedx', 'Санкт-Петербург', 'https://ya.ru/15', 15, NULL, 'REJECTED', '2020-08-09 18:21:04', '2020-08-10 10:14:04', '{}', '{}', NULL, '2020-08-17T12:49:22.373412Z', false),
       (3, ARRAY['kt1', 'test'], NULL, 'Москва', NULL, NULL, NULL, 'NOT_PUBLISHED', '2020-08-08 17:23:11', '2020-08-09 12:23:01', '{}', '{}', NULL, NULL, false),
       (4, ARRAY['kt2'], 'artem-mazanov', 'Москва', 'https://ya.ru/42', 42, NULL, 'APPROVED', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', NULL, '2020-08-13T12:49:22.373412Z', false),
       (5, ARRAY['kt2'], 'shedx', 'Ярославль', 'https://ya.ru/99', 99, NULL, 'SUCCEEDED', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', NULL, '2020-08-13T12:49:22.373412Z', false),
       (6, ARRAY[]::text[], 'shedx', 'Казань', 'https://ya.ru/101', 101, NULL, 'SUCCEEDED', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', NULL, NULL, false),
       (
        7,
        ARRAY['kt3'],
        'artem-mazanov',
        'Санкт-Петербург',
        'https://ya.ru/107',
        107,
        NULL,
        'SUCCEEDED',
        '2020-08-11 19:25:58',
        '2020-08-12 02:55:10',
        '[[{"y_label": "test_metric_name", "x_label": "Бюджет", "data": [[3239.9408999999996, 318.35294117647055]]}, {"y_label": "Цена дополнительного оффера", "x_label": "Бюджет", "data": [[3239.9408999999996, 149.26556991869967]]}]]',
        '{
  "charts": [
    {
      "algorithm_id": "kt3",
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
      "algorithm_id": "kt3",
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
    }
  ],
  "discount_meta": {
    "kt3": {
      "budget_spent": 45326175.24480001,
      "cur_cpeo": 7619.925805238771,
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
          "avg_discount": 0.40942267441448776,
          "max_price_with_discount": 50,
          "max_discount_percent": 3.0,
          "budget": 34690759.87200001
        },
        "random": {
          "avg_discount": 3.066118618310774,
          "budget": 10635415.372800002,
          "max_price_with_discount": 50,
          "max_discount_percent": 3.0
        }
      },
      "with_push": false
    }
  }
}',
        '2020-08-13T12:49:22.373412Z',
        '2020-08-15T12:49:22.373412Z',
        false
        ),
       (
        8,
        ARRAY['kt4', 'test'],
        'artem-mazanov',
        'Йошкар-Ола',
        'https://ya.ru/108',
        108,
        NULL,
        'SUCCEEDED',
        '2020-08-11 19:25:58',
        '2020-08-12 02:55:10',
        '[[{"y_label": "test_metric_name", "x_label": "Бюджет", "data": [[3239.9408999999996, 318.35294117647055]]}, {"y_label": "Цена дополнительного оффера", "x_label": "Бюджет", "data": [[3239.9408999999996, 149.26556991869967]]}]]',
        '{
  "charts": [
    {
      "algorithm_id": "kt4",
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
      "algorithm_id": "kt4",
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
      "algorithm_id": "test",
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
      "algorithm_id": "test",
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
    }
  ],
  "discount_meta": {
    "kt4": {
      "budget_spent": 45326175.24480001,
      "cur_cpeo": 7619.925805238771,
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
      "with_push": false
    },
    "test": {
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
        '2020-08-13T12:49:22.373412Z',
        '2020-08-15T12:49:22.373412Z',
        false
        ),
       (
        9,
        ARRAY['kt5'],
        'artem-mazanov',
        'Миасс',
        'https://ya.ru/109',
        109,
        NULL,
        'WAITING_TO_STOP',
        '2020-08-11 19:25:58',
        '2020-08-12 02:55:10',
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
        '2020-08-13T12:49:22.373412Z',
        '2020-08-14T12:49:22.373412Z',
        true
        ),
       (
        10,
        ARRAY['kt6', 'test2'],
        'artem-mazanov',
        'Нижний Тагил',
        'https://ya.ru/110',
        110,
        NULL,
        'SUCCEEDED',
        '2020-08-11 19:25:58',
        '2020-08-12 02:55:10',
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
        '2020-08-13T12:49:22.373412Z',
        '2020-08-15T10:49:22.373412Z',
        true
        ),
       (
        11,
        ARRAY['kt5'],
        'artem-mazanov',
        'Вышний Волочек',
        'https://ya.ru/111',
        111,
        NULL,
        'WAITING_TO_START',
        '2020-08-11 19:25:58',
        '2020-08-12 02:55:10',
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
        '2020-08-14T10:49:22.373412Z',
        '2020-08-16T12:49:22.373412Z',
        true
        ),
       -- update new discount started and old stopped
       (12, ARRAY['kt2'], 'artem-mazanov', 'Челябинск', 'https://ya.ru/212', 212, NULL, 'WAITING_TO_STOP', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', '2020-08-13T12:49:22.373412Z', '2020-08-14T09:49:22.373412Z', false),
       (13, ARRAY['kt1', 'kt2'], 'shedx', 'Челябинск', 'https://ya.ru/213', 213, 12, 'WAITING_TO_START', '2020-08-09 18:21:04', '2020-08-10 10:14:04', '{}', '{}', '2020-08-14T09:49:22.373412Z', '2020-08-17T12:49:22.373412Z', false),
       -- updated appoved statuses
       (14, ARRAY['kt1'], 'eugenest', 'Париж', 'https://ya.ru/214', 214, NULL, 'NEED_APPROVAL', '2020-08-10 23:43:21', '2020-08-10 23:53:21', '{}', '{}', '2020-08-14T12:49:22.373412Z', '2020-08-18T12:49:22.373412Z', false),
       (15, ARRAY['kt2'], 'shedx', 'Нью-Йорк', 'https://ya.ru/215', 215, NULL, 'NEED_APPROVAL', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', '2020-08-14T12:49:22.373412Z', '2020-08-19T12:49:22.373412Z', false),
       -- update stopped statuses
       (16, ARRAY['kt2'], 'artem-mazanov', 'Усть-Каменогорск', 'https://ya.ru/216', 216, NULL, 'WAITING_TO_STOP', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', '2020-08-13T12:49:22.373412Z', '2020-08-14T09:49:22.373412Z', false),
       (17, ARRAY['stop'], 'artem-mazanov', 'Усть-Каменогорск', 'https://ya.ru/217', 217, 16, 'WAITING_TO_START', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '[]', '{}', '2020-08-14T09:49:22.373412Z', NULL, false),
       -- update succeded statuses to waiting_to_stop due to date_to - creation_lag < utcnow
       (18, ARRAY['kt2'], 'artem-mazanov', 'Арзамас', 'https://ya.ru/218', 218, NULL, 'SUCCEEDED', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', '2020-08-13T12:49:22.373412Z', '2020-08-14T11:49:22.373412Z', false),
       (19, ARRAY['kt2'], 'artem-mazanov', 'Арзамас16', 'https://ya.ru/219', 219, NULL, 'SUCCEEDED', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', '2020-08-13T12:49:22.373412Z', '2020-08-14T10:49:22.373412Z', false),
       -- as upper, but for with_push == true
       (20, ARRAY['kt2'], 'artem-mazanov', 'Арзамас2', 'https://ya.ru/220', 220, NULL, 'SUCCEEDED', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', '2020-08-13T12:49:22.373412Z', '2020-08-15T10:49:22.373412Z', true),
       (21, ARRAY['kt2'], 'artem-mazanov', 'Арзамас3', 'https://ya.ru/221', 221, NULL, 'SUCCEEDED', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', '2020-08-13T12:49:22.373412Z', '2020-08-15T09:49:22.373412Z', true),
       -- case when only WAITING_TO_START suggest exists and stop suggest approved
       (22, ARRAY['kt2'], 'artem-mazanov', 'Арзамас4', 'https://ya.ru/222', 222, NULL, 'WAITING_TO_START', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', '2020-08-14T09:49:22.373412Z', '2020-08-16T09:49:22.373412Z', false),
       (23, ARRAY['stop'], 'artem-mazanov', 'Арзамас4', 'https://ya.ru/223', 223, NULL, 'NEED_APPROVAL', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '[]', '{}', '2020-08-14T10:49:22.373412Z', NULL, false),
       -- case when WAITING_TO_START with WAITING_TO_STOP exists and approved stop suggest
       (24, ARRAY['kt2'], 'artem-mazanov', 'Арзамас5', 'https://ya.ru/224', 224, NULL, 'WAITING_TO_STOP', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', '2020-08-13T12:49:22.373412Z', '2020-08-14T10:49:22.373412Z', false),
       (25, ARRAY['kt1', 'kt2'], 'shedx', 'Арзамас5', 'https://ya.ru/225', 225, 24, 'WAITING_TO_START', '2020-08-09 18:21:04', '2020-08-10 10:14:04', '{}', '{}', '2020-08-14T10:49:22.373412Z', '2020-08-17T12:49:22.373412Z', false),
       (26, ARRAY['stop'], 'artem-mazanov', 'Арзамас5', 'https://ya.ru/226', 226, 24, 'NEED_APPROVAL', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '[]', '{}', '2020-08-14T11:49:22.373412Z', NULL, false),
       -- case when only WAITING_TO_START suggest exists and new suggest approved
       (27, ARRAY['kt1', 'kt2'], 'shedx', 'Арзамас6', 'https://ya.ru/227', 227, NULL, 'WAITING_TO_START', '2020-08-09 18:21:04', '2020-08-10 10:14:04', '{}', '{}', '2020-08-14T09:49:22.373412Z', '2020-08-17T12:49:22.373412Z', false),
       (28, ARRAY['kt1'], 'eugenest', 'Арзамас6', 'https://ya.ru/228', 228, NULL, 'NEED_APPROVAL', '2020-08-10 23:43:21', '2020-08-10 23:53:21', '{}', '{}', '2020-08-14T12:49:22.373412Z', '2020-08-18T12:49:22.373412Z', false),
       -- case when WAITING_TO_START with WAITING_TO_STOP exists and new suggest approved
       (29, ARRAY['kt2'], 'artem-mazanov', 'Арзамас7', 'https://ya.ru/229', 229, NULL, 'WAITING_TO_STOP', '2020-08-11 19:25:58', '2020-08-12 02:55:10', '{}', '{}', '2020-08-13T12:49:22.373412Z', '2020-08-14T10:49:22.373412Z', false),
       (30, ARRAY['kt1', 'kt2'], 'shedx', 'Арзамас7', 'https://ya.ru/230', 230, 29, 'WAITING_TO_START', '2020-08-09 18:21:04', '2020-08-10 10:14:04', '{}', '{}', '2020-08-14T10:49:22.373412Z', '2020-08-17T12:49:22.373412Z', false),
       (31, ARRAY['kt1'], 'eugenest', 'Арзамас7', 'https://ya.ru/231', 231, 29, 'NEED_APPROVAL', '2020-08-10 23:43:21', '2020-08-10 23:53:21', '{}', '{}', '2020-08-14T12:49:22.373412Z', '2020-08-18T12:49:22.373412Z', false)
;
