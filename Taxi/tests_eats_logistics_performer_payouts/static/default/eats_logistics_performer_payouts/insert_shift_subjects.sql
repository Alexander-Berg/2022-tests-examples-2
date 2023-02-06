-- insert_all_factors.sql is assumed to have been run before!

-- subject for performer

INSERT INTO eats_logistics_performer_payouts.subjects(id,
                                                      external_id,
                                                      subject_type_id,
                                                      created_at,
                                                      updated_at)
VALUES
-- driver
(1001, '37_667a89f3', 5, '2020-06-17 10:00:00+03', '2020-06-20 09:55:00+03'),
-- performer
(1002, '254654', 1, '2020-06-17 10:00:00+03', '2020-06-20 09:55:00+03'),
-- order
(1003, '220203-321935', 8, '2020-06-20 09:55:00+03', '2020-06-20 09:55:00+03'),
(1004, '220203-190863', 8, '2020-06-20 09:55:00+03', '2020-06-20 09:55:00+03'),
-- shift
(2000, 'shift-2000', 2, '2020-06-17 10:00:00+03', '2020-06-20 09:55:00+03'),
(2001, 'shift-2001', 2, '2020-06-20 10:00:00+03', '2020-06-20 11:57:00+03'),
(2002, 'shift-2002', 2, '2020-06-20 11:55:00+03', '2020-06-20 13:00:00+03'),
(2003, 'shift-2003', 2, '2020-06-20 13:40:00+03', '2020-06-20 15:00:00+03');

INSERT INTO eats_logistics_performer_payouts.subjects_subjects(subject_id, related_subject_id)
VALUES (1001, 1002),
       (1002, 1001),

       (1003, 1002),
       (1002, 1003),
       (1004, 1002),
       (1002, 1004),

       (2000, 1002),
       (1002, 2000),
       (2001, 1002),
       (1002, 2001),
       (2002, 1002),
       (1002, 2002),
       (2003, 1002),
       (1002, 2003)
;

-- 'package_accepted_at' factor for order

WITH factor AS (
    SELECT id
    FROM eats_logistics_performer_payouts.factors
    WHERE subject_type_id = 8
      AND name = 'package_accepted_at'
)
INSERT
INTO eats_logistics_performer_payouts.factor_datetime_values
    (subject_id, factor_id, value)
SELECT subject_id,
       id AS factor_id,
       value::TIMESTAMPTZ
FROM (VALUES (1003, '2020-06-20 10:28:00+03'),
             (1004, '2020-06-20 10:35:00+03')
     ) AS v (subject_id, value)
         CROSS JOIN
     factor;

-- 'package_ready_at' factor for order:

WITH factor AS (
    SELECT id
    FROM eats_logistics_performer_payouts.factors
    WHERE subject_type_id = 8
      AND name = 'package_ready_at'
)
INSERT
INTO eats_logistics_performer_payouts.factor_datetime_values
    (subject_id, factor_id, value)
SELECT subject_id,
       id AS factor_id,
       value::TIMESTAMPTZ
FROM (VALUES (1003, '2020-06-20 10:42:00+03'),
             (1004, '2020-06-20 10:47:00+03')) AS v (subject_id, value)
         CROSS JOIN
     factor;

-- 'package_given_at' factor for order:

WITH factor AS (
    SELECT id
    FROM eats_logistics_performer_payouts.factors
    WHERE subject_type_id = 8
      AND name = 'package_given_at'
)
INSERT
INTO eats_logistics_performer_payouts.factor_datetime_values
    (subject_id, factor_id, value)
SELECT subject_id,
       id AS factor_id,
       value::TIMESTAMPTZ
FROM (VALUES (1003, '2020-06-20 10:46:00+03'),
             (1004, '2020-06-20 10:49:00+03')) AS v (subject_id, value)
         CROSS JOIN
     factor;

-- 'actual_start_at' factors for shifts:

WITH factor AS (
    SELECT id
    FROM eats_logistics_performer_payouts.factors
    WHERE subject_type_id = 2
      AND name = 'actual_start_at'
)
INSERT
INTO eats_logistics_performer_payouts.factor_datetime_values
    (subject_id, factor_id, value)
SELECT subject_id,
       id AS factor_id,
       value::TIMESTAMPTZ
FROM (VALUES (2000, '2020-06-20 08:00:00+03'),
             (2001, '2020-06-20 10:00:00+03'),
             (2002, '2020-06-20 12:00:00+03'),
             (2003, '2020-06-20 14:00:00+03')) AS v (subject_id, value)
         CROSS JOIN
     factor;

-- 'planned_start_at' factors for shifts:

WITH factor AS (
    SELECT id
    FROM eats_logistics_performer_payouts.factors
    WHERE subject_type_id = 2
      AND name = 'planned_start_at'
)
INSERT
INTO eats_logistics_performer_payouts.factor_datetime_values
    (subject_id, factor_id, value)
SELECT subject_id,
       id AS factor_id,
       value::TIMESTAMPTZ
FROM (VALUES (2000, '2020-06-20 08:00:00+03'),
             (2001, '2020-06-20 10:00:00+03'),
             (2002, '2020-06-20 12:00:00+03'),
             (2003, '2020-06-20 14:00:00+03')) AS v (subject_id, value)
         CROSS JOIN
     factor;

-- 'planned_end_at' factors for shifts:

WITH factor AS (
    SELECT id
    FROM eats_logistics_performer_payouts.factors
    WHERE subject_type_id = 2
      AND name = 'planned_end_at'
)
INSERT
INTO eats_logistics_performer_payouts.factor_datetime_values
    (subject_id, factor_id, value)
SELECT subject_id,
       id AS factor_id,
       value::TIMESTAMPTZ
FROM (VALUES (2000, '2020-06-20 10:00:00+03'),
             (2001, '2020-06-20 12:00:00+03'),
             (2002, '2020-06-20 14:00:00+03'),
             (2003, '2020-06-20 16:00:00+03')) AS v (subject_id, value)
         CROSS JOIN
     factor;

-- 'actual_end_at' factors for shifts:

WITH factor AS (
    SELECT id
    FROM eats_logistics_performer_payouts.factors
    WHERE subject_type_id = 2
      AND name = 'actual_end_at'
)
INSERT
INTO eats_logistics_performer_payouts.factor_datetime_values
    (subject_id, factor_id, value)
SELECT subject_id,
       id AS factor_id,
       value::TIMESTAMPTZ
FROM (VALUES (2000, '2020-06-20 10:00:00+03'),
             (2001, '2020-06-20 12:00:00+03'),
             (2002, '2020-06-20 14:00:00+03'),
             (2003, '2020-06-20 16:00:00+03')) AS v (subject_id, value)
         CROSS JOIN
     factor;
