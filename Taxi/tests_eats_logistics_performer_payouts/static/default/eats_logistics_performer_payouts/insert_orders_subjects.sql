-- insert factors
INSERT INTO eats_logistics_performer_payouts.factors (id, name, type, subject_type_id)
VALUES (74, 'name', 'string', 6),
       (75, 'commission', 'decimal', 6),
       (76, 'marketing_commission', 'decimal', 6),
       (77, 'is_self_employed', 'integer', 6),
       (78, 'is_self_employed_non_resident', 'integer', 6),
       (79, 'is_courier_service', 'integer', 6),
       (80, 'username', 'string', 1),
       (81, 'started_work_at', 'datetime', 1),
       (82, 'billing_type', 'string', 1),
       (83, 'meta_is_picker', 'integer', 1),
       (84, 'meta_is_dedicated_picker', 'integer', 1),
       (85, 'meta_is_rover', 'integer', 1),
       (86, 'meta_is_storekeeper', 'integer', 1),
       (87, 'eats_region_id', 'string', 1),
       (88, 'pool', 'string', 1),
       (90, 'calculated', 'integer', 2),
       (91, 'travel_type', 'string', 2),
       (92, 'eats_region_id', 'string', 2),
       (93, 'type', 'string', 2),
       (94, 'status', 'string', 2),
       (95, 'planned_start_at', 'datetime', 2),
       (96, 'actual_start_at', 'datetime', 2),
       (97, 'planned_end_at', 'datetime', 2),
       (98, 'actual_end_at', 'datetime', 2),
       (99, 'duration', 'integer', 2),
       (100, 'offline_time', 'integer', 2),
       (101, 'missed_time', 'integer', 2),
       (102, 'guarantee', 'decimal', 2),
       (103, 'pause_duration', 'integer', 2),
       (105, 'fraud_on_start', 'integer', 2),
       (106, 'fraud_share', 'decimal', 2),
       (107, 'is_newbie', 'integer', 2),
       (108, 'created_at', 'datetime', 8),
       (109, 'pool', 'string', 8),
       (110, 'weight', 'integer', 8),
       (111, 'cancel_reason', 'string', 8),
       (112, 'cancel_reason_group', 'string', 8),
       (113, 'is_surge', 'integer', 8),
       (114, 'surge_bonus', 'decimal', 8),
       (115, 'payment_fee', 'decimal', 8),
       (116, 'payment_tips', 'decimal', 8),
       (117, 'package_ready_at', 'datetime', 8),
       (118, 'package_given_at', 'datetime', 8),
       (119, 'package_accepted_at', 'datetime', 8),
       (120, 'finished_at', 'datetime', 8),
       (121, 'confirmed_at', 'datetime', 8),
       (122, 'order_type', 'string', 8),
       (123, 'corp_client_id', 'string', 3),
       (124, 'calculated', 'integer', 3),
       (125, 'eats_region_id', 'string', 3),
       (126, 'travel_type', 'string', 3),
       (127, 'created_at', 'datetime', 3),
       (128, 'actual_assigned_at', 'datetime', 3),
       (129, 'in_batch_order', 'integer', 3),
       (130, 'estimated_package_ready_at', 'datetime', 3),
       (131, 'status', 'string', 3),
       (132, 'cancel_reason', 'string', 3),
       (133, 'fraud_status_arrived_source', 'integer', 3),
       (134, 'fraud_status_arrived_destination', 'integer', 3),
       (135, 'fraud_status_taken', 'integer', 3),
       (136, 'fraud_status_delivered', 'integer', 3),
       (137, 'visit_order', 'integer', 4),
       (138, 'type', 'string', 4),
       (139, 'planned_arrived_at', 'datetime', 4),
       (140, 'actual_arrived_at', 'datetime', 4),
       (141, 'actual_action_completed_at', 'datetime', 4),
       (142, 'distance_from_prev_waypoint', 'integer', 4),
       (143, 'in_batch_order', 'integer', 10),
       (144, 'transport_type', 'string', 1),
       (145, 'country_id', 'string', 1),
       (146, 'post', 'string', 2),
       (147, 'is_orphan', 'integer', 8),
       (150, 'surge_bonus_currency', 'string', 8),
       (152, 'payment_fee_currency', 'string', 8),
       (154, 'payment_tips_currency', 'string', 8),
       (155, 'meta_is_ultima', 'integer', 1);

-- insert subjects
INSERT INTO eats_logistics_performer_payouts.subjects (external_id,
                                                       subject_type_id)
VALUES ('1', 2),      -- shift (1)
       ('2', 2),      -- shift (2)
       ('3', 2),      -- shift (3)
       ('4', 2),      -- shift (4)
       ('42', 1),     -- performer (5)
       ('73', 1),     -- performer (6)
       ('42_75', 5),  -- driver_profile (7)
       ('73_56', 5),  -- driver_profile (8)
       ('42-73', 8),  -- order (9)
       ('42-74', 8),  -- order (10)
       ('42-75', 8);  -- order (11)

-- insert relations
INSERT INTO eats_logistics_performer_payouts.subjects_subjects (subject_id, related_subject_id)
VALUES (1, 5), (5, 1), -- '1' x '42'
       (2, 5), (5, 2), -- '2' x '42'
       (3, 6), (6, 3), -- '3' x '73'
       (4, 6), (6, 4), -- '4' x '73'

       (5, 7), (7, 5), -- '42' x '42_75'
       (6, 8), (8, 6); -- '73' x '73_56'

-- insert factors of the shift '1'
INSERT INTO eats_logistics_performer_payouts.factor_datetime_values (subject_id, factor_id, value)
VALUES (1, 95, '2021-12-24 09:14:50.000000 +00:00'),
       (1, 96, '2021-12-24 09:14:51.000000 +00:00'),
       (1, 97, '2021-12-24 17:14:50.000000 +00:00');
INSERT INTO eats_logistics_performer_payouts.factor_integer_values (subject_id, factor_id, value)
VALUES (1, 99, 28819),
       (1, 100, 26701),
       (1, 103, 0);
INSERT INTO eats_logistics_performer_payouts.factor_string_values (subject_id, factor_id, value)
VALUES (1, 91, 'pedestrian'),
       (1, 92, '1'),
       (1, 93, 'unplanned'),
       (1, 94, 'in_progress');

-- insert factors of the shift '2'
INSERT INTO eats_logistics_performer_payouts.factor_datetime_values (subject_id, factor_id, value)
VALUES (2, 95, '2021-12-24 06:14:50.000000 +00:00'),
       (2, 96, '2021-12-24 06:14:51.000000 +00:00'),
       (2, 97, '2021-12-24 09:00:00.000000 +00:00'),
       (2, 98, '2021-12-24 09:00:00.000000 +00:00');
INSERT INTO eats_logistics_performer_payouts.factor_integer_values (subject_id, factor_id, value)
VALUES (2, 99, 28819),
       (2, 100, 26701),
       (2, 103, 0);
INSERT INTO eats_logistics_performer_payouts.factor_string_values (subject_id, factor_id, value)
VALUES (2, 91, 'pedestrian'),
       (2, 92, '1'),
       (2, 93, 'unplanned'),
       (2, 94, 'closed');

-- insert factors of the shift '3'
INSERT INTO eats_logistics_performer_payouts.factor_datetime_values (subject_id, factor_id, value)
VALUES (3, 95, '2021-12-24 09:14:50.000000 +00:00'),
       (3, 96, '2021-12-24 09:14:51.000000 +00:00'),
       (3, 97, '2021-12-24 17:14:50.000000 +00:00');
INSERT INTO eats_logistics_performer_payouts.factor_integer_values (subject_id, factor_id, value)
VALUES (3, 99, 28819),
       (3, 100, 26701),
       (3, 103, 0);
INSERT INTO eats_logistics_performer_payouts.factor_string_values (subject_id, factor_id, value)
VALUES (3, 91, 'pedestrian'),
       (3, 92, '1'),
       (3, 93, 'unplanned'),
       (3, 94, 'in_progress');

-- no factors for shift '4'

-- insert factors for performer '42'
INSERT INTO eats_logistics_performer_payouts.factor_datetime_values (subject_id, factor_id, value)
VALUES (5, 81, '2021-12-24 08:00:14.000000 +00:00');
INSERT INTO eats_logistics_performer_payouts.factor_integer_values (subject_id, factor_id, value)
VALUES (5, 83, 0),
       (5, 84, 0),
       (5, 85, 0),
       (5, 86, 0);
INSERT INTO eats_logistics_performer_payouts.factor_string_values (subject_id, factor_id, value)
VALUES (5, 80, 'Шурпе Питерский Питерскович'),
       (5, 82, 'courier_service'),
       (5, 87, '3'),
       (5, 88, 'eda'),
       (5, 144, 'pedestrian'),
       (5, 145, '35');

-- no factors for performer '73'

--- insert factors for order '42-73'
INSERT INTO eats_logistics_performer_payouts.factor_datetime_values (subject_id, factor_id, value)
VALUES (9, 108, '2021-12-24 12:05:47.000000 +00:00'),
       (9, 118, '2021-12-24 12:19:48.000000 +00:00'),
       (9, 119, '2021-12-24 12:07:23.000000 +00:00'),
       (9, 120, '2021-12-24 12:30:27.000000 +00:00'),
       (9, 121, '2021-12-24 12:19:46.000000 +00:00');
INSERT INTO eats_logistics_performer_payouts.factor_integer_values (subject_id, factor_id, value)
VALUES (9, 110, 6000);
INSERT INTO eats_logistics_performer_payouts.factor_string_values (subject_id, factor_id, value)
VALUES (9, 122, 'native');

-- no factors for order '42-74'

-- no factors for order '42-75'
