INSERT INTO cache.user_offers (offer_id, user_id, table_name, offer_data)
VALUES (
        'offer_1', 'user3', '2021-09-22',
        '{
      "categories": {
        "business": {
          "fixed_price": true,
          "payment_type": "cash",
          "surge_value": 1.1,
          "user_price": 229.0
        },
        "maybach": {
          "fixed_price": true,
          "payment_type": "cash",
          "surge_value": 1.0,
          "user_price": 1799.0
        },
        "vip": {
          "fixed_price": true,
          "payment_type": "cash",
          "surge_value": 1.0,
          "user_price": 417.0
        }
      },
      "created": "2022-01-15T15:07:15.470004+03:00",
      "caller_link": "caller_link_1",
      "due": "2022-01-15T15:07:15.289561+03:00",
      "is_corp_decoupling": false,
      "tariff_name": "moscow", "has_fixed_price": true,
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
        );
