INSERT INTO se.nalogru_phone_bindings 
    (phone_pd_id, inn_pd_id, status,
     exceeded_legal_income_year, exceeded_reported_income_year, updated_at)
VALUES ('phone1_pd_id', 'inn1_pd_id', 'COMPLETED', null, 2021, '2021-11-01+00'),
       ('phone2_pd_id', 'inn2_pd_id', 'COMPLETED', 2021, null, '2021-11-02+00');

INSERT INTO se.finished_profiles
(park_id, contractor_profile_id, phone_pd_id, inn_pd_id, do_send_receipts, is_own_park, updated_at)
VALUES ('dbid1', 'uuid1', 'phone1_pd_id', 'inn1_pd_id', FALSE, FALSE, '2021-11-01+00'),
       ('dbid2', 'uuid2', 'phone2_pd_id', 'inn2_pd_id', TRUE, TRUE, '2021-11-02+00'),
       ('dbid3', 'uuid3', 'phone2_pd_id', 'inn2_pd_id', FALSE, FALSE, '2021-11-03+00');
