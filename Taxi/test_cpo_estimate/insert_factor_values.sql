-- performer & driver_profile subject
INSERT
INTO eats_logistics_performer_payouts.subjects
    ( id, external_id, subject_type_id, created_at, updated_at )
VALUES (1, 'aafd0000', 1, '2021-03-11 15:00:30+03', '2021-05-10 15:00:30+03'),

    (101, 'ffa8111122223333000000000000_00ccca05111122220000000000000000', 5,
        '2021-03-11 15:00:30+03', '2021-05-10 15:00:30+03');

-- relations
INSERT
INTO eats_logistics_performer_payouts.subjects_subjects
    ( subject_id, related_subject_id )
VALUES (1, 101), (101, 1);

-- string factors for performer subject
WITH factor AS (
    SELECT id AS factor_id, name
    FROM eats_logistics_performer_payouts.factors
    WHERE subject_type_id = 1
)
INSERT
INTO eats_logistics_performer_payouts.factor_string_values
    ( subject_id, factor_id, value )
SELECT subject_id, factor_id, value
FROM (
    VALUES ('country_id', 1, '35'),
        ('eats_region_id', 1, '11'),
        ('pool', 1, 'eda'),
        ('transport_type', 1, 'pedestrian')
    ) AS v (name, subject_id, value)
    JOIN factor ON v.name = factor.name;
