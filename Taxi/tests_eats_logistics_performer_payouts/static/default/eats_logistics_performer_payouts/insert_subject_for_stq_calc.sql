-- insert performers
INSERT INTO eats_logistics_performer_payouts.performers (id, external_id)
VALUES (1, '1')
;

-- insert subjects
INSERT INTO eats_logistics_performer_payouts.subjects (id,
                                                       external_id,
                                                       subject_type_id,
                                                       performer_id)
VALUES (1, '1', 2, 0), -- shift, not calculated
       (2, '1', 1, 0), -- performer
       (3, '2', 2, 0), -- shift, calculated
       (4, '3', 2, 0), -- shift, calculated
       (5, '4', 2, 0) -- shift, calculated
;

--- insert factors
INSERT INTO eats_logistics_performer_payouts.factors (id, name, type, subject_type_id)
VALUES (1, 'actual_end_at', 'datetime', 2),
       (2, 'planned_end_at', 'datetime', 2),
       (3, 'actual_start_at', 'datetime', 2),
       (4, 'planned_start_at', 'datetime', 2),

       (5, 'fraud_on_start', 'integer', 2),
       (6, 'is_newbie', 'integer', 2),
       (21, 'recently_orders_completed', 'integer', 1),
       
       (17, 'missed_time', 'decimal', 2),
       (19, 'recently_km_passed', 'decimal', 1),
       (20, 'recently_hours_worked', 'decimal', 1),
       
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
VALUES (1, 1, '2019-04-10T21:00:13+00:00'),
       (2, 1, '2019-04-10T21:00:00+00:00'),
       (3, 1, '2019-04-10T12:00:45+00:00'),
       (4, 1, '2019-04-10T12:00:00+00:00'),
       
       (1, 3, '2019-04-09T20:28:13+00:00'),
       (2, 3, '2019-04-09T21:00:00+00:00'),
       (3, 3, '2019-04-09T12:27:45+00:00'),
       (4, 3, '2019-04-09T12:00:00+00:00'),
       
       (1, 4, '2019-04-04T20:28:13+00:00'),
       (2, 4, '2019-04-04T21:00:00+00:00'),
       (3, 4, '2019-04-02T12:27:45+00:00'),
       (4, 4, '2019-04-02T12:00:00+00:00'),
       
       (1, 5, '2019-02-10T20:28:13+00:00'),
       (2, 5, '2019-02-10T21:00:00+00:00'),
       (3, 5, '2019-02-10T12:27:45+00:00'),
       (4, 5, '2019-02-10T12:00:00+00:00')
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
       (18, 1, 'closed'),

       (12, 2, '35'),
       (13, 2, '1'),
       (14, 2, 'shop'),
       (15, 2, 'pedestrian'),
       (16, 2, 'Суперсборщик Ростислав')
;

INSERT INTO eats_logistics_performer_payouts.factor_decimal_values (factor_id, subject_id, value)
VALUES (11, 2, 0.0)
;

-- insert subjects relations
INSERT INTO eats_logistics_performer_payouts.subjects_subjects (subject_id, related_subject_id)
VALUES (1, 2),
       (2, 1),
       
       (3, 2),
       (2, 3),
       
       (4, 2),
       (2, 4),
       
       (5, 2),
       (2, 5);

-- insert calculation_results
INSERT INTO eats_logistics_performer_payouts.calculation_results (subject_id, meta)
VALUES (3, '{"actual_hours": 10.0, "number_of_orders": 5, "km_to_clients": 6.6, "km_to_rests": 3.43}'::JSONB),
       (4, '{"actual_hours": 10.0, "number_of_orders": 5, "km_to_clients": 6.6, "km_to_rests": 3.43}'::JSONB),
       (5, '{"actual_hours": 10.0, "number_of_orders": 5, "km_to_clients": 6.6, "km_to_rests": 3.43}'::JSONB);

-- insert coefficients
INSERT
INTO eats_logistics_performer_payouts.coefficients_values (country_id, region_id, pool, courier_type, coefficients)
VALUES ('35', '1', 'shop', 'picker', '{
  "fine_thresh_late": 10,
  "fine_thresh_early": 10,
  "max_missed_time": 10,
  "per_hour_guarantee": 300
}');
