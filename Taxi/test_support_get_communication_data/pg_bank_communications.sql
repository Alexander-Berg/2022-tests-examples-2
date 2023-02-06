INSERT INTO bank_communications.communications (
  communication_id,
  idempotency_token,
  bank_uid,
  created_at
)
VALUES (
  '7948e3a9-623c-4524-a390-9e4264d27a11',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da1',
  'buid1',
  '2022-02-01T20:28:58.838783+00:00'
), (
  '7948e3a9-623c-4524-a390-9e4264d27a22',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da2',
  'buid1',
  '2022-02-02T20:28:58.838783+00:00'
);

INSERT INTO bank_communications.yasms (
  yasms_id,
  communication_id,
  status,
  created_at,
  error_code,
  message_sent_id,
  phone_number,
  template_parameters
)
VALUES (
  '7948e3a9-623c-4524-a390-9e4264d27b11',
  '7948e3a9-623c-4524-a390-9e4264d27a22',
  'SENT',
  '2022-02-02T20:28:58.838783+00:00',
  NULL,
  'message_id',
  '+79990001122',
  '{}'
);

INSERT INTO bank_communications.push_notifications (
  notification_id,
  communication_id,
  bank_uid,
  status,
  subscription_id,
  uuid,
  notification_text,
  created_at,
  updated_at
)
VALUES (
         '7948e3a9-623c-4524-a390-9e4264d27b11',
         '7948e3a9-623c-4524-a390-9e4264d27a22',
         'buid1',
         'SENT',
         '7948e3a9-623c-4524-a390-9e4264d27a33',
         '7948e3a9-623c-4524-a390-9e4264d27a44',
         'text',
         '2022-02-02T20:28:58.838783+00:00',
         '2022-02-02T20:28:58.838783+00:00'
       );
