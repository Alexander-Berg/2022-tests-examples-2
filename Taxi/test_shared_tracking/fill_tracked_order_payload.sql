INSERT INTO eats_orders_tracking.orders (order_nr, eater_id, payload)
VALUES ('000000-000000', 'eater1', '{
  "raw_status": "9",
  "status": "order_taken",
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
  "delivery_class": "regular",
  "order_to_another_eater": {
    "personal_phone_id": "another_eater_ppid",
    "name": "Вася"
  }
}');

INSERT INTO eats_orders_tracking.places (place_id, payload)
VALUES ('40', '{
  "id": "40",
  "name": "Вкусная Еда",
  "location": {"latitude": 59.999102, "longitude": 30.220117},
  "address": "Санкт-Петербург, ул. Оптиков, д. 30",
  "place_slug": "vkusnaya_eda_optikov",
  "brand_slug": "vkusnaya_eda",
  "address_comment": "Вход со двора"
}');

INSERT INTO eats_orders_tracking.eater_to_place_masking_states
    (order_nr, state, proxy_phone_number, extension)
VALUES ('000000-000000', 'success', '+79990001122', '12345');

INSERT INTO eats_orders_tracking.couriers (order_nr, payload)
VALUES ('000000-000000', '{
  "courier_id": "courier1",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false
}');

INSERT INTO eats_orders_tracking.shared_tracking_links (shared_id, order_nr)
VALUES ('some_shared_id', '000000-000000');
