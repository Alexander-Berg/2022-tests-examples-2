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
    'CALLIDFROTESTING12345',
    '+7928348868282',
    0
),
(
    'B2BCallsFromSfCti',
    'manager_number',
    'SrcNumber__c',
    'b2b-cc-sf-cti',
    'CALLIDFROTESTING12345',
    '868482',
    0
),
(
    'B2BCallsFromSfCti',
    'cc_sf_cti_call_id',
    'ExternalId__c',
    'b2b-cc-sf-cti',
    'CALLIDFROTESTING12345',
    'CALLIDFROTESTING12345',
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
("Id")
VALUES
('11111111'), ('22222222'), ('333333333');

DROP TABLE IF EXISTS sf_data_load.sf_b2b_user;

CREATE TABLE IF NOT EXISTS sf_data_load.sf_b2b_user
(
    "Id" varchar primary key ,
    "Extension" varchar
);

INSERT INTO sf_data_load.sf_b2b_user
("Id", "Extension")
VALUES
('0053X00000C0tQrQAJ', null),
('0053X00000CTJ3DQAX', '24083'),
('0051q000006GytfAAC', '868482');

DROP TABLE IF EXISTS sf_data_load.sf_b2b_contact;

CREATE TABLE IF NOT EXISTS sf_data_load.sf_b2b_contact
(
    "Id" varchar primary key,
    "Phone" varchar,
    "MobilePhone" varchar
);

INSERT INTO sf_data_load.sf_b2b_contact
("Id", "Phone", "MobilePhone")
VALUES
('0037S000002dnWsQAI', null, null),
('0037S000002dUf0QAE', '+972545344991', null),
('0031q00000qKdfEAAS', '+7928348868282', null)
