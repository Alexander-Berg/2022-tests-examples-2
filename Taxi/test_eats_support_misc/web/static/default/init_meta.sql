INSERT INTO eats_support_misc.support_meta (order_nr, courier_support_meta, updated_at)
VALUES 
('123456-123456', NULL, NOW()),
('123456-123457', '{}', NOW()),
('123456-123458', '{"claim_id":"bad_claim_id"}', NOW()),
('123456-123459', '{"claim_id":"some_claim_id"}', '2020-04-28T12:00:00+03:00'),
('123456-123460', '{"claim_id":"some_claim_id"}', NOW()),
('123456-123461', '{"claim_id":"some_claim_id","place_eta":"2020-04-28 09:15:00","eater_eta":"2020-04-28 09:25:00","courier_type": "car"}', NOW());
