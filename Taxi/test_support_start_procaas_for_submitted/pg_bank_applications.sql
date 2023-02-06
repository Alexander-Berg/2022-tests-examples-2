INSERT INTO bank_applications.applications (
  application_id,
  user_id_type,
  user_id,
  type,
  status,
  reason,
  additional_params,
  submitted_form,
  multiple_success_status_allowed,
  initiator,
  operation_type,
  operation_at
) VALUES (
  '11111111-1111-1111-1111-111111111111',
  'BUID',
  '11111111-1111-1111-1111-111111111113',
  'SIMPLIFIED_IDENTIFICATION',
  'SUCCESS',
  NULL,
  '{"param": "value"}'::jsonb,
  '{"phone_id": "1"}'::jsonb,
  FALSE,
  '{"initiator_type": "SUPPORT", "initiator_id": 1234}'::jsonb,
  'INSERT',
  '2022-02-01T20:28:58.838783+00:00'
), (
  '22222222-1111-1111-1111-111111111111',
  'BUID',
  '22222222-1111-1111-1111-111111111112',
  'SIMPLIFIED_IDENTIFICATION',
  'SUCCESS',
  NULL,
  NULL,
  NULL,
  FALSE,
  '{"initiator_type": "BUID", "initiator_id": "67754336-d4d1-43c1-aadb-cabd06674ea6"}'::jsonb,
  'UPDATE',
  '2022-02-02T20:28:58.838783+00:00'
), (
  '33333333-1111-1111-1111-111111111111',
  'BUID',
  '67754336-d4d1-43c1-aadb-cabd06674ea6',
  'SIMPLIFIED_IDENTIFICATION',
  'FAILED',
  'error',
  NULL,
  NULL,
  FALSE,
  '{"initiator_type": "BUID", "initiator_id": "67754336-d4d1-43c1-aadb-cabd06674ea6"}'::jsonb,
  'UPDATE',
  '2022-02-02T20:28:58.838783+00:00'
), (
  '44444444-1111-1111-1111-111111111111',
  'UID',
  '44444444-1111-1111-1111-111111111113',
  'SIMPLIFIED_IDENTIFICATION',
  'SUCCESS',
  NULL,
  NULL,
  NULL,
  FALSE,
  '{"initiator_type": "SUPPORT", "initiator_id": 1234}'::jsonb,
  'UPDATE',
  '2022-02-01T20:28:58.838783+00:00'
);
INSERT INTO bank_applications.simplified_identification (
  application_id,
  submit_idempotency_token,
  status,
  operation_type,
  agreement_version,
  user_id_type,
  user_id,
  initiator
) VALUES (
  '11111111-1111-1111-1111-111111111111',
  '11111111-1111-1111-1111-111111111112',
  'SUBMITTED',
  'INSERT',
  0,
  'BUID',
  '11111111-1111-1111-1111-111111111113',
  '{"initiator_type": "BUID", "initiator_id": "67754336-d4d1-43c1-aadb-cabd06674ea6"}'::jsonb
), (
  '22222222-1111-1111-1111-111111111111',
  '22222222-1111-1111-1111-111111111112',
  'CREATED',
  'INSERT',
  0,
  'BUID',
  '22222222-1111-1111-1111-111111111113',
  '{"initiator_type": "BUID", "initiator_id": "67754336-d4d1-43c1-aadb-cabd06674ea6"}'::jsonb
), (
  '33333333-1111-1111-1111-111111111111',
  NULL,
  'SUBMITTED',
  'INSERT',
  0,
  'BUID',
  '33333333-1111-1111-1111-111111111113',
  '{"initiator_type": "BUID", "initiator_id": "67754336-d4d1-43c1-aadb-cabd06674ea6"}'::jsonb
);
