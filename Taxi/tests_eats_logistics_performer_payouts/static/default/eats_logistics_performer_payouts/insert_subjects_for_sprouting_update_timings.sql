INSERT INTO eats_logistics_performer_payouts.subjects (external_id, subject_type_id, updated_at)
VALUES ('1', 3, NOW()),
       ('2', 4, '3000-11-22'::date);

INSERT INTO eats_logistics_performer_payouts.subjects_subjects (subject_id, related_subject_id)
VALUES (1, 2);
