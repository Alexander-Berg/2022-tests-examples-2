INSERT INTO cache.user_offers (offer_id, user_id, table_name, offer_data)
VALUES (
        'offer1', 'user3', '2021-09-22',
        '{
      "caller_link": "caller_link_1",
      "common_uuid": "common_uuid_1",
      "categories": {
        "business": {
          "fixed_price": true,
          "payment_type": "cash",
          "surge_value": 1.1,
          "user_price": 229.0
        }
      },
      "created": "2021-09-22T09:00:00+00:00",
      "due": "2021-09-22T09:00:00+00:00",
      "has_fixed_price": true,
      "is_corp_decoupling": false,
      "tariff_name": "moscow",
      "waypoints": [
        [
          37.67347722471099,
          55.70793157976327
        ],
        [
          37.667271047,
          55.706056341
        ]
      ]
    }'
        ),
       ('offer2', 'user3', '2021-09-22',
        '{
      "caller_link": "caller_link_2",
      "common_uuid": "common_uuid_2",
      "categories": {
        "business": {
          "fixed_price": true,
          "payment_type": "cash",
          "surge_value": 1.0,
          "user_price": 202.0
        }
      },
      "created": "2021-09-22T10:00:00+00:00",
      "due": "2021-09-20T12:00:00+00:00",
      "has_fixed_price": true,
      "is_corp_decoupling": false,
      "tariff_name": "moscow",
      "waypoints": [
        [
          37.6587677001953,
          55.63993835449217
        ],
        [
          37.648362,
          55.654268
        ]
      ]
    }'
        );
