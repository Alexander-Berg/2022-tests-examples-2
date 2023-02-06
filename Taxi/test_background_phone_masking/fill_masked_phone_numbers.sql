INSERT INTO eats_orders_tracking.masked_courier_phone_numbers
(
    order_nr,
    phone_number,
    extension,
    ttl,
    error_count
)
VALUES
    ('111111-111111', '10012', '101', '2120-10-28+00:00', 0),
    ('111111-222222', '20012', '201', '2021-01-09+00:00', 0),
    ('111111-333333',    NULL,  NULL,               NULL, 3),
    ('111111-444444', '40012', '401', '2021-01-09+00:00', 9),
    ('111111-555555', '50012', '501', '2021-01-09+00:00', 10),
    ('111111-666666',    NULL,  NULL,               NULL, 0),
    ('111111-888888', '80012', '801', '2021-01-09+00:00', 0);

INSERT INTO eats_orders_tracking.couriers (order_nr, payload)
VALUES ('111111-111111', '{
  "courier_id": "courier1",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false,
  "claim_id": "id1",
  "claim_alias": "default"
}'),
       ('111111-222222', '{
  "courier_id": "courier1",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false,
  "claim_id": "id2",
  "claim_alias": "default"
}'),
       ('111111-333333', '{
  "courier_id": "courier1",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false,
  "claim_id": "id3",
  "claim_alias": "default"
}'),
       ('111111-444444', '{
  "courier_id": "courier1",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false,
  "claim_id": "id4",
  "claim_alias": "default"
}'),
       ('111111-555555', '{
  "courier_id": "courier1",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false,
  "claim_id": "id8",
  "claim_alias": "default"
}'),
       ('111111-666666', '{
  "courier_id": "courier1",
  "name": "Коля",
  "raw_type": "vehicle",
  "type": "vehicle",
  "car_model": "Kia Rio",
  "car_number": "x000xx199",
  "is_hard_of_hearing": false,
  "claim_id": "id6",
  "claim_alias": "default"
}');

INSERT INTO eats_orders_tracking.orders (order_nr, eater_id, payload)
VALUES ('111111-111111', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
  "created_at": "2020-10-28T18:15:43.51+00:00",
  "updated_at": "2120-10-28T18:15:43.51+00:00"}'),
       ('111111-222222', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
  "created_at": "2020-10-28T18:15:43.51+00:00",
  "updated_at": "2120-10-28T18:15:43.51+00:00"}'),
       ('111111-333333', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
  "created_at": "2020-10-28T18:15:43.51+00:00",
  "updated_at": "2120-10-28T18:15:43.51+00:00"}'),
       ('111111-444444', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
  "created_at": "2020-10-28T18:15:43.51+00:00",
  "updated_at": "2120-10-28T18:15:43.51+00:00"}'),
       ('111111-555555', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
  "created_at": "2020-10-28T18:15:43.51+00:00",
  "updated_at": "2120-10-28T18:15:43.51+00:00"}'),
       ('111111-888888', 'eater1', '{
  "raw_status": "2",
  "status": "place_confirmed",
  "created_at": "2020-10-28T18:15:43.51+00:00",
  "updated_at": "2120-10-28T18:15:43.51+00:00"}');

INSERT INTO eats_orders_tracking.waybills(waybill_ref, performer_info, points, order_nrs, chained_previous_waybill_ref, waybill_revision, created_at)
VALUES ('waybill_ref_1',
        '{"driver_id":"driver_1", "park_id": "park_1", "name": "SuperTom", "raw_type": "car", "type": "vehicle", "is_hard_of_hearing": true, "car_model": "Fiat", "car_number": "x000xx200", "personal_phone_id": "pd_123"}'::jsonb,
        '[{"id":1, "claim_id": "id8", "address":{"coordinates":[1.0, 1.0]}, "type": "source", "visit_order": 1, "visit_status": "visited", "corp_client_id": "corp_111", "external_order_id":"111111-888888"}, {"id":2, "claim_id": "id8", "address":{"coordinates":[1.0, 1.0]}, "type": "destination", "visit_order": 3, "visit_status": "pending", "corp_client_id": "corp_111", "external_order_id":"111111-888888"}, {"id":3, "claim_id": "456", "address":{"coordinates":[1.0, 1.0]}, "type": "source", "visit_order": 2, "visit_status": "pending", "corp_client_id": "corp_111", "external_order_id":"some_second_order"}, {"id":4, "claim_id": "456", "address":{"coordinates":[1.0, 1.0]}, "type": "destination", "visit_order": 4, "visit_status": "pending", "corp_client_id": "corp_111", "external_order_id":"some_second_order"}]'::jsonb,
        array['111111-888888', 'some_second_order']::text[],
        null, 1, '2021-01-08T17:20:00.00+00:00'),
    ('waybill_ref_2',
        '{"driver_id":"driver_1", "park_id": "park_1", "name": "SuperTom1", "raw_type": "car", "type": "vehicle", "is_hard_of_hearing": true, "car_model": "Fiat", "car_number": "x000xx200", "personal_phone_id": "pd_123"}'::jsonb,
        '[{"id":1, "claim_id": "old_claim", "address":{"coordinates":[1.0, 1.0]}, "type": "source", "visit_order": 1, "visit_status": "visited", "corp_client_id": "corp_111", "external_order_id":"111111-888888"}, {"id":2, "claim_id": "old_claim", "address":{"coordinates":[1.0, 1.0]}, "type": "destination", "visit_order": 3, "visit_status": "pending", "corp_client_id": "corp_111", "external_order_id":"111111-888888"}, {"id":3, "claim_id": "456", "address":{"coordinates":[1.0, 1.0]}, "type": "source", "visit_order": 2, "visit_status": "pending", "corp_client_id": "corp_111", "external_order_id":"some_second_order"}, {"id":4, "claim_id": "456", "address":{"coordinates":[1.0, 1.0]}, "type": "destination", "visit_order": 4, "visit_status": "pending", "corp_client_id": "corp_111", "external_order_id":"some_second_order"}]'::jsonb,
        array['111111-888888', 'some_second_order']::text[],
        null, 1, '2021-01-08T17:10:00.00+00:00');
