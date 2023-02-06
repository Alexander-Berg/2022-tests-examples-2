INSERT INTO eats_orders_tracking.orders (order_nr, eater_id, payload)
VALUES ('000000-000000', 'eater1', '{
  "raw_status": "1",
  "status": "call_center_confirmed",
  "status_detail": {"id": 1, "date": "2020-10-28T18:25:43.51+00:00"},
  "promise": "2020-10-28T18:15:43.51+00:00",
  "location": {"latitude": 60.029139, "longitude": 30.144101},
  "is_asap": true,
  "raw_type": "retail",
  "type": "retail",
  "raw_delivery_type": "native",
  "delivery_type": "native",
  "raw_shipping_type": "delivery",
  "shipping_type": "delivery",
  "place_id": "40",
  "created_at": "2020-10-28T18:15:43.51+00:00",
  "updated_at": "2120-10-28T18:15:43.51+00:00",
  "service": "eats",
  "client_app": "taxi-app",
  "application": "eda_android",
  "deivce_id": "123_device",
  "taxi_user_id": "taxi_user_id_123",
  "application": "eda_android",
  "changes_state": {
    "applicable_until": "2020-10-28T18:15:43.51+00:00"
  },
  "status_history": {},
  "region": {
    "name": "Москва",
    "code": "moscow",
    "timezone": "Europe/Moscow",
    "country_code": "RU"
  },
  "order_to_another_eater": {
    "personal_phone_id": "ppid"
  }
}');
