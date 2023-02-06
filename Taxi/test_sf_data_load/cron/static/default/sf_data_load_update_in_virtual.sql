DELETE FROM sf_data_load.loading_fields;

INSERT INTO sf_data_load.loading_fields
(
    source_class_name,
    source_field,
    sf_api_field_name,
    lookup_alias,
    source_key,
    data_value,
    retries_count
) VALUES
(
    'B2BCallsFromSfCti',
    'external_phone',
    'DstNumber__c',
    'b2b-cc-sf-cti',
    'ID2',
    '+7928348868282',
    1
),
(
    'B2BCallsFromSfCti',
    'manager_number',
    'SrcNumber__c',
    'b2b-cc-sf-cti',
    'ID2',
    '868482',
    1
),
(
    'B2BCallsFromSfCti',
    'cc_sf_cti_call_id',
    'ExternalId__c',
    'b2b-cc-sf-cti',
    'ID2',
    'ID2',
    1
),
(
    'sf|b2b|Contact',
    'Id',
    'WhoId',
    'concat_id_contact_and_task',
    '+7928348868282',
    'NEWIDFORCONTACT',
    0
);

DROP TABLE IF EXISTS sf_data_load.sf_b2b_task;

CREATE TABLE IF NOT EXISTS sf_data_load.sf_b2b_task
(
    "Id" varchar primary key ,
    "ExternalId__c" varchar,
    "DstNumber__c" varchar,
    "SrcNumber__c" varchar,
    "WhoId" varchar,
    "OwnerId" varchar
);

INSERT INTO sf_data_load.sf_b2b_task
("Id", "DstNumber__c", "SrcNumber__c", "ExternalId__c", "WhoId", "OwnerId")
VALUES
('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
 '+7928348868282',
 '868482',
 'ID1',
 '0031q00000qKdfEAAS',
 '0051q000006GytfAAC'
 ),
('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab',
 '+7928348868282',
 '868482',
 'ID2',
 NULL,
 '0051q000006GytfAAC'
 );

DROP TABLE IF EXISTS sf_data_load.sf_b2b_contact;

CREATE TABLE IF NOT EXISTS sf_data_load.sf_b2b_contact
(
    "Id" varchar primary key,
    "Phone" varchar
);

INSERT INTO sf_data_load.sf_b2b_contact
("Id", "Phone")
VALUES
('0037S000002dnWsQAI', null),
('NEWIDFORCONTACT', '+7928348868282')
