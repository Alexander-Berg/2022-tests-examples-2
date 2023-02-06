
INSERT INTO eats_orders_tracking.couriers (order_nr, payload)
VALUES ('111111-222222', '{
  "courier_id": "courier2",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false,
  "claim_id": "claim1",
  "claim_alias": "default"
}'),
       ('111111-333333', '{
  "courier_id": "courier3",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false
}');

INSERT INTO eats_orders_tracking.masked_courier_phone_numbers (order_nr)
VALUES ('111111-222222');
