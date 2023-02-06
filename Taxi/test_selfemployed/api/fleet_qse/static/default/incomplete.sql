INSERT INTO se.nalogru_phone_bindings
    (phone_pd_id, status)
VALUES
    ('PHONE_PD_ID', 'IN_PROGRESS');
INSERT INTO se.quasi_profile_forms
    (park_id, contractor_profile_id, phone_pd_id, is_phone_verified, is_accepted, requested_at)
VALUES
    ('park_id', 'incomplete', 'PHONE_PD_ID', TRUE, FALSE, '2021-08-01+03:00');
