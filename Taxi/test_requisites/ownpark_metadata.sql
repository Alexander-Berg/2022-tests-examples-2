INSERT INTO se.ownpark_profile_forms_contractor
    (phone_pd_id, initial_park_id, initial_contractor_id)
 VALUES
    ('PHONE_PD_ID', 'passport', 'puid1');
INSERT INTO se.ownpark_profile_forms_common
    (phone_pd_id, external_id, state, initial_park_id, initial_contractor_id,
     created_park_id, created_contractor_id)
 VALUES
    ('PHONE_PD_ID', 'external_id', 'FINISHED', 'passport', 'puid1',
     'newparkid', 'newcontractorid');
INSERT INTO se.finished_ownpark_profile_metadata
    (phone_pd_id, external_id,
     salesforce_account_id, salesforce_requisites_case_id,
     initial_park_id, initial_contractor_id,
     created_park_id, created_contractor_id)
 VALUES
    ('PHONE_PD_ID', 'external_id',
     'AccountId', 'salesforce_requisites_case_id',
     'passport', 'puid1',
     'newparkid', 'newcontractorid');
INSERT INTO se.nalogru_phone_bindings
    (phone_pd_id, status, inn_pd_id)
 VALUES
    ('PHONE_PD_ID', 'COMPLETED', 'INN_PD_ID');
INSERT INTO se.finished_profiles
    (park_id,
     contractor_profile_id, phone_pd_id,
     inn_pd_id, do_send_receipts,
     is_own_park)
 VALUES
    ('newparkid',
     'newcontractorid', 'PHONE_PD_ID',
     'INN_PD_ID', true,
     true);
