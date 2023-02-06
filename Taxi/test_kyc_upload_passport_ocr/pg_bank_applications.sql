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
   '22222222-1111-1111-1111-111111111111',
   'UID',
   '100000',
   'type',
   TRUE,
   '{"kyc_application_status": "KYC_UPLOAD_PHOTOS"}'::jsonb,
   '{}'::jsonb
);
