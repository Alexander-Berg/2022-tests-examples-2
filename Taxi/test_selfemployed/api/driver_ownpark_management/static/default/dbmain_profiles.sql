INSERT INTO profiles
    (id, from_park_id, from_driver_id, salesforce_account_id,
     park_id, driver_id, inn, phone,
     created_at, modified_at)
VALUES
    ('se_d_1', 'parkid', 'contractorid', 'AccountId',
     'newparkid', 'newcontractorid', '000000', '79000000000',
     NOW(), NOW());
