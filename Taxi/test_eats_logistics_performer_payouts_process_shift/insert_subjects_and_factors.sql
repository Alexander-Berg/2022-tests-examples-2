-- insert performers
INSERT INTO eats_logistics_performer_payouts.performers (id, external_id)
VALUES (1, '1')
;

-- insert subjects
INSERT INTO eats_logistics_performer_payouts.subjects (id,
                                                       external_id,
                                                       subject_type_id,
                                                       performer_id)
VALUES (1, '1', 2, 0), -- shift
       (2, '1', 1, 0), -- performer
       (3, '2', 2, 0),
       (4, '0023_A6FE', 5, 0) -- driver_profile

;

--- insert factors
INSERT INTO eats_logistics_performer_payouts.factors (id, name, type, subject_type_id)
VALUES (1, 'actual_end_at', 'datetime', 2),
       (2, 'planned_end_at', 'datetime', 2),
       (3, 'actual_start_at', 'datetime', 2),
       (4, 'planned_start_at', 'datetime', 2),

       (5, 'fraud_on_start', 'integer', 2),
       (6, 'is_newbie', 'integer', 2),
       (17, 'missed_time', 'integer', 2),

       (7, 'eats_region_id', 'string', 2),
       (8, 'post', 'string', 2),
       (9, 'travel_type', 'string', 2),
       (10, 'type', 'string', 2),

       (12, 'country_id', 'string', 1),
       (13, 'eats_region_id', 'string', 1),
       (14, 'pool', 'string', 1),
       (15, 'transport_type', 'string', 1),
       (16, 'username', 'string', 1),
       (18, 'status', 'string', 2)
;

INSERT INTO eats_logistics_performer_payouts.factor_datetime_values (factor_id, subject_id, value)
VALUES (1, 1, '2019-04-10T20:28:13+00:00'),
       (2, 1, '2019-04-10T21:00:00+00:00'),
       (3, 1, '2019-04-10T12:27:45+00:00'),
       (4, 1, '2019-04-10T12:00:00+00:00')
;

INSERT INTO eats_logistics_performer_payouts.factor_integer_values (factor_id, subject_id, value)
VALUES (5, 1, 0),
       (6, 1, 0),
       (17, 1, 10)
;

INSERT INTO eats_logistics_performer_payouts.factor_string_values (factor_id, subject_id, value)
VALUES (7, 1, '1'),
       (8, 1, 'picker'),
       (9, 1, 'pedestrian'),
       (10, 1, 'planned'),
       (18, 1, 'not_started'),

       (12, 2, '35'),
       (13, 2, '1'),
       (14, 2, 'shop'),
       (15, 2, 'pedestrian'),
       (16, 2, 'Суперсборщик Ростислав'),

       (18, 3, 'closed')
;

INSERT INTO eats_logistics_performer_payouts.factor_decimal_values (factor_id, subject_id, value)
VALUES (11, 2, 0.0)
;

--- insert subjects relations
INSERT INTO eats_logistics_performer_payouts.subjects_subjects (subject_id, related_subject_id)
VALUES (1, 2);

-- insert coefficients
INSERT
INTO eats_logistics_performer_payouts.coefficients_values (country_id, region_id, pool, courier_type, coefficients)
VALUES ('35', '1', 'shop', 'picker', '{
  "fine_thresh_late": 10,
  "fine_thresh_early": 10,
  "max_missed_time": 10,
  "per_hour_guarantee": 300
}');
