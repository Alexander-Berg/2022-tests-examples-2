INSERT INTO hiring_taxiparks_gambling_salesforce.hiring_conditions (
    sf_id,
    sf_name,
    is_acquisition,
    is_deleted,
    rev,
    offers_rent,
    accepts_private_vehicles,
    hiring_territories,
    weight_rent,
    weight_private,
    extra
) VALUES
(
    'a_lease_park',
    'Lease Park',
    TRUE,
    FALSE,
    1,
    TRUE,
    FALSE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "a_lease_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": false,
        "is_paid_acquisition_rent__c": false 
      }
    '::jsonb
),
(
    'b_private_park',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    TRUE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "b_private_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": false,
        "is_paid_acquisition_rent__c": false 
      }
    '::jsonb
),
(
    'c_lease_and_private_park',
    'Private Park',
    TRUE,
    FALSE,
    1,
    TRUE,
    TRUE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "c_lease_and_private_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": false,
        "is_paid_acquisition_rent__c": false 
      }
    '::jsonb
),
(
    'd_none_park',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    FALSE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "d_none_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": false,
        "is_paid_acquisition_rent__c": false 
      }
    '::jsonb
),
(
    'e_selfreg_park',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    FALSE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "e_selfreg_park",
        "SelfRegistration__c": true,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": false,
        "is_paid_acquisition_rent__c": false 
      }
    '::jsonb
),
(
    'e_commercial_private_park',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    FALSE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "f_commercial_private_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": true,
        "is_paid_acquisition_rent__c": false 
      }
    '::jsonb
),
(
    'g_commercial_rent_park',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    FALSE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "g_commercial_rent_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": false,
        "is_paid_acquisition_rent__c": true 
      }
    '::jsonb
),
(
    'h_merge_phone_address_park_a',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    FALSE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "h_merge_phone_address_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": false,
        "is_paid_acquisition_rent__c": false 
      }
    '::jsonb
),
(
    'h_merge_phone_address_park_b',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    FALSE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "h_merge_phone_address_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "other_phone",
        "Address__c": "other_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": false,
        "is_paid_acquisition_rent__c": false 
      }
    '::jsonb
),
(
    'i_merge_email_park_a',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    FALSE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "i_merge_email_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": false,
        "is_paid_acquisition_rent__c": false 
      }
    '::jsonb
),
(
    'i_merge_email_park_b',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    FALSE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "i_merge_email_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "other_mail",
        "is_paid_acquisition_private__c": false,
        "is_paid_acquisition_rent__c": false 
      }
    '::jsonb
),
(
    'j_merge_bools_park_a',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    FALSE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "j_merge_bools_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": false,
        "is_paid_acquisition_rent__c": true 
      }
    '::jsonb
),
(
    'j_merge_bools_park_b',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    FALSE,
    NULL,
    1,
    1,
    '
      {
        "db_id__c": "j_merge_bools_park",
        "SelfRegistration__c": false,
        "DispatchPhone__c": "some_phone",
        "Address__c": "some_address",
        "Email__c": "some_mail",
        "is_paid_acquisition_private__c": true,
        "is_paid_acquisition_rent__c": false 
      }
    '::jsonb
)
;
