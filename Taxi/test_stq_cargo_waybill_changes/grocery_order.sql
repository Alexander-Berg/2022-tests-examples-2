INSERT INTO eats_orders_tracking.orders (order_nr, eater_id, payload)
VALUES ('grocery-extended-order-nr', 'eater1', '{
  "raw_status": "9",
  "status": "order_taken",
  "status_detail": {"id": 1, "date": "2020-10-28T18:25:43.51+00:00"},
  "promise": "2020-10-28T18:30:00.00+00:00",
  "location": {"latitude": 60.029139, "longitude": 30.144101},
  "is_asap": true,
  "raw_type": "grocery",
  "type": "grocery",
  "raw_delivery_type": "native",
  "delivery_type": "native",
  "raw_shipping_type": "delivery",
  "shipping_type": "delivery",
  "short_order_nr": "111111-222-3333",
  "place_id": "40",
  "created_at": "2020-10-28T18:15:43.51+00:00",
  "updated_at": "2120-10-28T18:15:43.51+00:00",
  "service": "eats",
  "client_app": "taxi-app",
  "changes_state": {
    "applicable_until": "2020-10-28T18:15:43.51+00:00"
  },
  "status_history": {
    "call_center_confirmed_at": "2020-10-28T18:15:43.51+00:00",
    "place_confirmed_at": "2020-10-28T18:15:43.51+00:00",
    "moved_to_delivery_at": "2020-10-28T18:15:43.51+00:00",
    "taken_at": "2020-10-28T18:15:43.51+00:00"
  },
  "region": {
    "name": "Москва",
    "code": "moscow",
    "timezone": "Europe/Moscow",
    "country_code": "RU"
  }
}'
),
('grocery-extended-order-nr-2', 'eater1', '{
  "raw_status": "9",
  "status": "order_taken",
  "status_detail": {"id": 1, "date": "2020-10-28T18:25:43.51+00:00"},
  "promise": "2020-10-28T18:30:00.00+00:00",
  "location": {"latitude": 60.029139, "longitude": 30.144101},
  "is_asap": true,
  "raw_type": "grocery",
  "type": "grocery",
  "raw_delivery_type": "native",
  "delivery_type": "native",
  "raw_shipping_type": "delivery",
  "shipping_type": "delivery",
  "short_order_nr": "333333-222-1111",
  "place_id": "40",
  "created_at": "2020-10-28T18:15:43.51+00:00",
  "updated_at": "2120-10-28T18:15:43.51+00:00",
  "service": "eats",
  "client_app": "taxi-app",
  "changes_state": {
    "applicable_until": "2020-10-28T18:15:43.51+00:00"
  },
  "status_history": {
    "call_center_confirmed_at": "2020-10-28T18:15:43.51+00:00",
    "place_confirmed_at": "2020-10-28T18:15:43.51+00:00",
    "moved_to_delivery_at": "2020-10-28T18:15:43.51+00:00",
    "taken_at": "2020-10-28T18:15:43.51+00:00"
  },
  "region": {
    "name": "Москва",
    "code": "moscow",
    "timezone": "Europe/Moscow",
    "country_code": "RU"
  }
}'
);
