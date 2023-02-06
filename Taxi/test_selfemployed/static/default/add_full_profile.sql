INSERT INTO se.nalogru_phone_bindings
(phone_pd_id, inn_pd_id, status)
VALUES ('PHONE_PD_ID_1', 'INN_PD_ID_1', 'COMPLETED')
ON CONFLICT DO NOTHING;

INSERT INTO se.finished_profiles
(park_id, contractor_profile_id, phone_pd_id, inn_pd_id, do_send_receipts, is_own_park)
VALUES ('p1', 'd1', 'PHONE_PD_ID_1', 'INN_PD_ID_1', TRUE, FALSE)
ON CONFLICT DO NOTHING;
