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
)
VALUES
(
 'B2BCallsFromSfCti','external_phone','DstNumber__c', 'b2b-cc-sf-cti', 'a', 'a', 10
),
(
 'B2BCallsFromSfCti','cc_sf_cti_call_id','ExternalId__c', 'b2b-cc-sf-cti', 'a', 'a', 11
),
(
 'sf|b2b|Contact','Id','WhoId', 'concat_id_contact_and_task', 'a', 'a', 0
),
(
 'B2BCallsFromSfCti','manager_number','SrcNumber__c', 'b2b-cc-sf-cti', 'a', 'a', 2
),
(
 'sf|b2b|User','Id','OwnerId', 'concat_id_manager_and_task', 'a', 'a', 9
);
