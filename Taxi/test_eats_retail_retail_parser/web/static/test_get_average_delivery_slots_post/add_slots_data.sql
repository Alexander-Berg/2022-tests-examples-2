INSERT INTO partner_slot
(
    place_group_id,
    origin_id,
    slots
)
VALUES
(
 'place_group_id1',
 'external_id1',
 '[{"from": "1937-01-01T12:00:27.870000+00:20", "to": "1937-01-01T12:00:27.870000+00:20", "delivery_cost": "123.1"}]'::json
 ),
(
 'place_group_id2',
 'external_id2',
 '[{"from": "1937-01-01T12:00:27.870000+00:20", "to": "1937-01-01T12:00:27.870000+00:20", "delivery_cost": "123.1"}]'::json
 );
