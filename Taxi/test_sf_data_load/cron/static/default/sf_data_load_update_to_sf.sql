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
    1
),
(
    'B2BCallsFromSfCti',
    'manager_number',
    'SrcNumber__c',
    'b2b-cc-sf-cti',
    'CALLIDFROTESTING12345',
    '868482',
    1
),
(
    'B2BCallsFromSfCti',
    'cc_sf_cti_call_id',
    'ExternalId__c',
    'b2b-cc-sf-cti',
    'CALLIDFROTESTING12345',
    'CALLIDFROTESTING12345',
    1
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
 'CALLIDFROTESTING12345',
 '0031q00000qKdfEAAS',
 '0051q000006GytfAAC'
 )
