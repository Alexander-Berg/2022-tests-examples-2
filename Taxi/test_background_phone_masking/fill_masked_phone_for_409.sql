INSERT INTO eats_orders_tracking.masked_courier_phone_numbers
(
    order_nr,
    phone_number,
    extension,
    ttl,
    error_count
)
VALUES
    ('111111-777777', '20012', '201', '2021-01-09+00:00', 0);

INSERT INTO eats_orders_tracking.couriers (order_nr, payload)
VALUES ('111111-777777', '{
  "courier_id": "courier1",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false,
  "claim_id": "id7",
  "claim_alias": "default"
}');

INSERT INTO eats_orders_tracking.orders (order_nr, eater_id, payload)
VALUES ('111111-777777', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
  "created_at": "2020-10-28T18:15:43.51+00:00",
  "updated_at": "2120-10-28T18:15:43.51+00:00"}');
