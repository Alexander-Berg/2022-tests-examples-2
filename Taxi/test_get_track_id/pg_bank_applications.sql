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
  '7948e3a9-623c-4524-a390-9e4264d27a01',
  'UID',
  '100001',
  'type',
  TRUE,
  '{"track_id":"track_id"}'::jsonb,
  '{}'::jsonb
),
(
   '7948e3a9-623c-4524-a390-9e4264d27a02',
   'UID',
   '100001',
   'type',
   TRUE,
   '{}'::jsonb,
   '{}'::jsonb
);
