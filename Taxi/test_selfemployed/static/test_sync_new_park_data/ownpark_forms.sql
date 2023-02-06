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
