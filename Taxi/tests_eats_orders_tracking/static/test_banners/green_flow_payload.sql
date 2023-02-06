INSERT INTO eats_orders_tracking.orders (order_nr, eater_id, payload)
VALUES ('000000-000001', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
  "status_detail": {"id": 1, "date": "2020-10-28T18:25:43.51+00:00"},
  "promise": "2020-10-28T18:15:43.51+00:00",
  "location": {"latitude": 50.0, "longitude": 20.0},
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
  "status_history": {},
  "region": {
    "name": "Москва",
    "code": "moscow",
    "timezone": "Europe/Moscow",
    "country_code": "RU"
  }
}'),
('000000-000002', 'eater2', '{
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
  "service": "eats",
  "client_app": "taxi-app",
  "status_history": {},
  "region": {
    "name": "Москва",
    "code": "moscow",
    "timezone": "Europe/Moscow",
    "country_code": "RU"
  }
}'),
('000000-000003', 'eater3', '{
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
  "service": "eats",
  "client_app": "taxi-app",
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
  "brand_slug": "vkusnaya_eda"
}');

INSERT INTO eats_orders_tracking.couriers (order_nr, payload)
VALUES ('000000-000001', '{
  "courier_id": "courier1",
  "name": "Коля",
  "raw_type": "pedestrian",
  "type": "pedestrian",
  "is_hard_of_hearing": false
}'),
('000000-000002', '{
  "courier_id": "courier2",
  "name": "Коля",
  "raw_type": "rover",
  "type": "rover",
  "is_hard_of_hearing": false
}'),
('000000-000003', '{
  "courier_id": "courier3",
  "name": "Коля",
  "raw_type": "pedestrian",
  "type": "pedestrian",
  "is_hard_of_hearing": false
}');
