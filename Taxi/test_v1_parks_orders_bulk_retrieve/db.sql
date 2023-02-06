INSERT INTO orders_0 (
  id,
  park_id,
  driver_id,
  number,
  provider,
  status,
  categorys,
  category,
  payment,
  date_create,
  date_transporting,
  date_booking,
  date_end,
  date_waiting,
  tariff_name,
  address_from,
  address_to,
  cost_total,
  receipt_data,
  paid_supply,
  route_points,
  tariff_id,
  description_canceled,
  fixed_price,
  price_corrections,
  description
)
VALUES (
  'yandex',--id
  'park_id_0',--park_id
  'driver_id_0',--driver_id
  1,--number
  2,--provider
  50,--status
  1,--categorys
  'econom',--category
  1,--payment
  '2019-12-01T10:00:00',--date_create
  '2019-12-01T10:05:00',--date_transporting
  '2019-12-01T10:10:00',--date_booking
  '2019-12-01T10:20:00',--date_end
  '2019-12-01T10:30:00',--date_waiting
  NULL,--tariff_name
  '{"City": "Москва", "Street":"Рядом с: улица Островитянова, 47","Region":"","Lat":55.6348324304,"Lon":37.541191945}',--address_from,
  '{"City": "Москва", "Street":"Гостиница Прибалтийская", "Lat": 55.5545, "Lon": 37.8989, "Order": 3}',--address_to
  553.0,--cost_total
  '{
    "services": {
        "child_chair.booster": 100
    },
    "services_count": {
        "child_chair.booster": {
            "count": 1,
            "price": 100,
            "sum": 100
        },
        "unknown_service": {
            "count": 1,
            "price": 50.31,
            "sum": 50.31
        }
    },
    "sum": 553,
    "total": 553,
    "total_distance": 5570.93553934032,
    "waiting_cost": 13,
    "waiting_in_transit_cost": 13,
    "waiting_in_transit_sum": 106.383333333333,
    "waiting_in_transit_time": 491,
    "waiting_sum": 28.6,
    "waiting_time": 132
  }',--receipt_data
  100,--paid_supply
  '[
      {"City": "Москва", "Street":"Улица 1", "Lat": 55.5111, "Lon": 37.222, "Order": 2},
      {"City": "Химки", "Street": "Нагорная улица", "Country": "Россия", "Lat": 55.123, "Lon": 37.1, "Order": 1}
   ]',--route_points
  'tariff_id_yandex_0',--tariff_id
  'description_canceled_0',--description_canceled
  NULL,--fixed_price
  NULL,--price_correction
  NULL--description
),
(
  'park',--id
  'park_id_0',--park_id
  'driver_id_0',--driver_id
  2,--number
  1,--provider
  50,--status
  0,--categorys
  NULL,--category
  0,--payment
  '2019-12-01T10:00:00',--date_create
  '2019-12-01T10:05:00',--date_transporting
  '2019-12-01T10:10:00',--date_booking
  '2019-12-01T10:20:00',--date_end
  '2019-12-01T10:30:00',--date_waiting
  'Тариф парка',--tariff_name
  '{"Street":"От борта: Россия, Ростов-на-Дону, микрорайон Темерник, улица Думенко","Lat":47.292952,"Lon":39.738583}',--address_from,
  '{"Order":1,"ArrivalDistance":500.0,"Street":"По указанию"}',--address_to
  1410.0,--cost_total
  '{
    "sum": 1410,
    "total": 1410,
    "total_distance": 9305.427734375,
    "waiting_in_transit_cost": 20,
    "waiting_in_transit_sum": 209.333333333333,
    "waiting_in_transit_time": 628
  }',--receipt_data
  NULL,--paid_supply
  NULL,--route_points
  'tariff_id_park_0',--tariff_id
  'description_canceled_1',--description_canceled
  NULL,--fixed_price
  NULL,--price_correction
  NULL--description
),
(
  'yandex_incorrect_receipt_address',--id
  'park_id_0',--park_id
  'driver_id_0',--driver_id
  3,--number
  2,--provider
  50,--status
  1 << 9,--categorys
  'comfortplus',--category
  0,--payment
  '2019-12-01T10:00:00',--date_create
  '2019-12-01T10:05:00',--date_transporting
  '2019-12-01T10:10:00',--date_booking
  '2019-12-01T10:20:00',--date_end
  '2019-12-01T10:30:00',--date_waiting
  NULL,--tariff_name
  '{Invalid JSON}',--address_from,
  '{"City": "Москва", "Street":"Гостиница Прибалтийская", "Lat": 55.5545, "Lon": 37.8989, "Order": 3}',--address_to
  223.0,--cost_total
  '{
    "services": {
        "child_chair": 100,
        "child_chair.booster": 150
    },
    "services_count": {
        "child_chair": {
            "count": 1,
            "price": 100,
            "sum": 100
        },
        "child_chair.booster": {
            "count": 1,
            "price": 150,
            "sum": 150
        }
    },
    "sum": 223,
    "total": 223,
    "total_distance": 811.174268766784
  }',--receipt_data
  100,--paid_supply
  '[]',--route_points
  NULL,--tariff_id
  'description_canceled_2',--description_canceled
  NULL,--fixed_price
  NULL,--price_correction
  NULL--description
),
(
  'yandex_cancelled',--id
  'park_id_0',--park_id
  'driver_id_0',--driver_id
  4,--number
  2,--provider
  70,--status
  1 << 2,--categorys
  'vip',--category
  5,--payment
  '2019-12-01T10:00:00',--date_create
  '2019-12-01T10:05:00',--date_transporting
  '2019-12-01T10:10:00',--date_booking
  '2019-12-01T10:20:00',--date_end
  '2019-12-01T10:30:00',--date_waiting
  NULL,--tariff_name
  '{"Street":"Abc5","Lat":55.6022246645,"Lon":37.5224489641}',--address_from
  NULL,--address_to
  223.0,--cost_total
  NULL,--receipt_data
  100,--paid_supply
  '{}',--route_points
  NULL,--tariff_id
  NULL,--description_canceled
  NULL,--fixed_price
  NULL,--price_correction
  NULL--description
),
(
  'fields',--id
  'park_id_0',--park_id
  'driver_id_0',--driver_id
  5,--number
  2,--provider
  50,--status
  1,--categorys
  'econom',--category
  1,--payment
  '2019-12-01T10:00:00',--date_create
  '2019-12-01T10:05:00',--date_transporting
  '2019-12-01T10:10:00',--date_booking
  '2019-12-01T10:20:00',--date_end
  '2019-12-01T10:30:00',--date_waiting
  NULL,--tariff_name
  '{"City": "Москва", "Street":"Рядом с: улица Островитянова, 47","Region":"","Lat":55.6348324304,"Lon":37.541191945}',--address_from,
  '{"City": "Москва", "Street":"Гостиница Прибалтийская", "Lat": 55.5545, "Lon": 37.8989, "Order": 3}',--address_to
  553.0,--cost_total
  '{
    "services": {
        "child_chair.booster": 100
    },
    "services_count": {
        "child_chair.booster": {
            "count": 1,
            "price": 100,
            "sum": 100
        },
        "unknown_service": {
            "count": 1,
            "price": 50.31,
            "sum": 50.31
        }
    },
    "sum": 553,
    "total": 553,
    "total_distance": 5570.93553934032,
    "waiting_cost": 13,
    "waiting_in_transit_cost": 13,
    "waiting_in_transit_sum": 106.383333333333,
    "waiting_in_transit_time": 491,
    "waiting_sum": 28.6,
    "waiting_time": 132
  }',--receipt_data
  100,--paid_supply
  '[
      {"City": "Москва", "Street":"Улица 1", "Lat": 55.5111, "Lon": 37.222, "Order": 2},
      {"City": "Химки", "Street": "Нагорная улица", "Country": "Россия", "Lat": 55.123, "Lon": 37.1, "Order": 1}
   ]',--route_points
  'tariff_id_yandex_fp',--tariff_id
  'description_canceled_fp',--description_canceled
  '{"show":true,"price":1145.0}',--fixed_price
  '{"surcharge":1500.0,"surge_text":"+30p"}',--price_correction
  'description_value'--description
),
(
  'wrong_fields',--id
  'park_id_0',--park_id
  'driver_id_0',--driver_id
  5,--number
  2,--provider
  50,--status
  1,--categorys
  'econom',--category
  1,--payment
  '2019-12-01T10:00:00',--date_create
  '2019-12-01T10:05:00',--date_transporting
  '2019-12-01T10:10:00',--date_booking
  '2019-12-01T10:20:00',--date_end
  '2019-12-01T10:30:00',--date_waiting
  NULL,--tariff_name
  '{"City": "Москва", "Street":"Рядом с: улица Островитянова, 47","Region":"","Lat":55.6348324304,"Lon":37.541191945}',--address_from,
  '{"City": "Москва", "Street":"Гостиница Прибалтийская", "Lat": 55.5545, "Lon": 37.8989, "Order": 3}',--address_to
  553.0,--cost_total
  '{
    "services": {
        "child_chair.booster": 100
    },
    "services_count": {
        "child_chair.booster": {
            "count": 1,
            "price": 100,
            "sum": 100
        },
        "unknown_service": {
            "count": 1,
            "price": 50.31,
            "sum": 50.31
        }
    },
    "sum": 553,
    "total": 553,
    "total_distance": 5570.93553934032,
    "waiting_cost": 13,
    "waiting_in_transit_cost": 13,
    "waiting_in_transit_sum": 106.383333333333,
    "waiting_in_transit_time": 491,
    "waiting_sum": 28.6,
    "waiting_time": 132
  }',--receipt_data
  100,--paid_supply
  '[
      {"City": "Москва", "Street":"Улица 1", "Lat": 55.5111, "Lon": 37.222, "Order": 2},
      {"City": "Химки", "Street": "Нагорная улица", "Country": "Россия", "Lat": 55.123, "Lon": 37.1, "Order": 1}
   ]',--route_points
  'tariff_id_yandex_fp',--tariff_id
  'description_canceled_fp',--description_canceled
  'null',--fixed_price
  'null',--price_correction
  'description_value'--description
),
(
  'string_fields',--id
  'park_id_0',--park_id
  'driver_id_0',--driver_id
  5,--number
  2,--provider
  50,--status
  1,--categorys
  'econom',--category
  1,--payment
  '2019-12-01T10:00:00',--date_create
  '2019-12-01T10:05:00',--date_transporting
  '2019-12-01T10:10:00',--date_booking
  '2019-12-01T10:20:00',--date_end
  '2019-12-01T10:30:00',--date_waiting
  NULL,--tariff_name
  '{"City": "Москва", "Street":"Рядом с: улица Островитянова, 47","Region":"","Lat":55.6348324304,"Lon":37.541191945}',--address_from,
  '{"City": "Москва", "Street":"Гостиница Прибалтийская", "Lat": 55.5545, "Lon": 37.8989, "Order": 3}',--address_to
  553.0,--cost_total
  '{
    "services": {
        "child_chair.booster": 100
    },
    "services_count": {
        "child_chair.booster": {
            "count": 1,
            "price": "100",
            "sum": "100"
        },
        "unknown_service": {
            "count": 1,
            "price": "50.31",
            "sum": "50.31"
        }
    },
    "sum": 553,
    "total": 553,
    "total_distance": 5570.93553934032,
    "waiting_cost": 13,
    "waiting_in_transit_cost": 13,
    "waiting_in_transit_sum": 106.383333333333,
    "waiting_in_transit_time": 491,
    "waiting_sum": 28.6,
    "waiting_time": 132
  }',--receipt_data
  100,--paid_supply
  '[
      {"City": "Москва", "Street":"Улица 1", "Lat": 55.5111, "Lon": 37.222, "Order": 2},
      {"City": "Химки", "Street": "Нагорная улица", "Country": "Россия", "Lat": 55.123, "Lon": 37.1, "Order": 1}
   ]',--route_points
  'tariff_id_yandex_fp',--tariff_id
  'description_canceled_fp',--description_canceled
  'null',--fixed_price
  'null',--price_correction
  'description_value'--description
);
