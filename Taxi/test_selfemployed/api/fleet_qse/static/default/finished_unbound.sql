INSERT INTO se.nalogru_phone_bindings
    (phone_pd_id, inn_pd_id, status)
VALUES
    ('PHONE_PD_ID', 'INN_PD_ID', 'FAILED');
INSERT INTO se.quasi_profile_forms
(park_id, contractor_profile_id,
 phone_pd_id, is_phone_verified,
 is_accepted, requested_at)
VALUES
    ('park_id', 'finished_unbound',
     'PHONE_PD_ID', TRUE,
     TRUE, '2021-08-01+03:00');
INSERT INTO se.finished_profiles
    (park_id, contractor_profile_id, phone_pd_id, inn_pd_id, do_send_receipts)
VALUES
    ('park_id', 'finished_unbound', 'PHONE_PD_ID', 'INN_PD_ID', FALSE);
