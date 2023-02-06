-- initial factors
INSERT INTO eats_logistics_performer_payouts.factors (id, name, type, subject_type_id)
VALUES
-- performer
(1, 'travel_type', 'string', 1),
(2, 'is_newbie', 'integer', 1),
-- shift
(3, 'type', 'string', 2),
(4, 'region_id', 'integer', 2),
(5, 'started_at', 'datetime', 2),
(6, 'ended_at', 'datetime', 2),
-- delivery
(7, 'region_id', 'integer', 3),
(8, 'weight_grams', 'integer', 3),
-- point
(9, 'distance_to_point', 'integer', 4),
(10, 'expected_visited_at', 'datetime', 4),
(11, 'actual_visited_at', 'datetime', 4),
(12, 'type', 'string', 4)
;
