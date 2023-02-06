INSERT INTO bank_applications.applications (
  application_id,
  user_id_type,
  user_id,
  type,
  multiple_success_status_allowed,
  additional_params,
  initiator
)
VALUES (
   '11111111-1111-1111-1111-111111111111',
   'UID',
   '100000',
   'type',
   TRUE,
   '{"kyc_application_status": "KYC_UPLOAD_PHOTOS"}'::jsonb,
   '{}'::jsonb
),
(
   '11111111-1111-1111-1111-222222222222',
   'UID',
   '100000',
   'type',
   TRUE,
   '{"additional_info": {}, "kyc_application_status": "KYC_UPLOAD_PHOTOS"}',
   '{}'::jsonb
),
(
   '11111111-1111-1111-1111-333333333333',
   'UID',
   '100000',
   'type',
   TRUE,
   '{"kyc_application_status": "KYC_FINAL"}'::jsonb,
   '{}'::jsonb
),
(
   '11111111-1111-1111-1111-444444444444',
   'UID',
   '100000',
   'type',
   TRUE,
   '{}'::jsonb,
   '{}'::jsonb
),
(
   '11111111-1111-1111-1111-555555555555',
   'UID',
   '100000',
   'type',
   TRUE,
   '{"kyc_application_status": "KYC_ABC"}'::jsonb,
   '{}'::jsonb
);
