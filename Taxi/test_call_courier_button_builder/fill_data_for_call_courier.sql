INSERT INTO eats_orders_tracking.orders (order_nr, eater_id, payload)
VALUES ('000000-000001', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
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
  "payment_status": {"status": "payment.success"},
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
  }
}'),
('000000-000002', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
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
  "payment_status": {"status": "payment.success"},
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
    "country_code": "BY"
  }
}'),
('000000-000003', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
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
  "payment_status": {"status": "payment.success"},
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
  }
}'),
('000000-000004', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
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
  "payment_status": {"status": "payment.success"},
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
  "address_comment": "Вход со двора",
  "official_contact": {
    "personal_phone_id": "1111111",
    "extension": "12345"
  }
}');

INSERT INTO eats_orders_tracking.couriers (order_nr, payload)
VALUES ('000000-000001', '{
  "courier_id": "courier1",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false,
  "claim_id": "123",
  "claim_alias": "default",
  "personal_phone_id": "123"
}'),
('000000-000002', '{
  "courier_id": "courier2",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false,
  "claim_id": "124",
  "claim_alias": "default",
  "personal_phone_id": "124"
}'),
('000000-000003', '{
  "courier_id": "courier3",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false,
  "personal_phone_id": "125"
}'),
('000000-000004', '{
  "courier_id": "courier4",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false
}');

INSERT INTO eats_orders_tracking.masked_courier_phone_numbers
(order_nr, phone_number, extension, ttl)
VALUES ('000000-000001', '000001', '000001', '2120-10-28T18:15:43.51+00:00'),
('000000-000002', '000002', '000002', '2120-10-28T18:15:43.51+00:00');
