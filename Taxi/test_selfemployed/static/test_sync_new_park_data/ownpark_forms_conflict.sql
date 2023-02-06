INSERT INTO se.ownpark_profile_forms_contractor
    (initial_park_id, initial_contractor_id, phone_pd_id)
VALUES ('selfreg', 'selfregid1', 'PHONE_PD_ID1');

INSERT INTO se.ownpark_profile_forms_common
    (phone_pd_id, state, salesforce_account_id, external_id, inn_pd_id,
     initial_park_id, initial_contractor_id,
     created_park_id, created_contractor_id)
VALUES ('PHONE_PD_ID1', 'FILLED', 'sf_acc_id', 'external_id', 'INN_PD_ID1',
        'selfreg', 'selfregid1', NULL, NULL);

INSERT INTO se.nalogru_phone_bindings
    (phone_pd_id, inn_pd_id, status)
VALUES ('PHONE_PD_ID1', 'INN_PD_ID1', 'COMPLETED')
ON CONFLICT DO NOTHING;

INSERT INTO se.finished_ownpark_profile_metadata
    (phone_pd_id, salesforce_account_id, external_id,
     initial_park_id, initial_contractor_id, created_park_id, created_contractor_id)
VALUES ('PHONE_PD_ID1', 'sf_acc_id', 'external_id', 'selfreg', 'selfregid1', 'cp1', 'cd1');

INSERT INTO se.finished_profiles
    (phone_pd_id, inn_pd_id,
     do_send_receipts, is_own_park, park_id, contractor_profile_id)
VALUES ('PHONE_PD_ID1', 'INN_PD_ID1', true, true, 'cp1', 'cd1');
