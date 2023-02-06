INSERT INTO bank_authorization.tracks (
  id,
  idempotency_token,
  buid,
  operation_type,
  created_at,
  updated_at
)
VALUES (
  '7948e3a9-623c-4524-a390-9e4264d27a11',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da1',
  'buid1',
  'start_session',
  '2022-02-01T20:28:58.838783+00:00',
  '2022-02-01T20:28:58.838783+00:00'
),(
  '7948e3a9-623c-4524-a390-9e4264d27a22',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da2',
  'buid1',
  'new_card',
  '2022-02-02T20:28:58.838783+00:00',
  '2022-02-02T20:28:58.838783+00:00'
);

INSERT INTO bank_authorization.codes (
  id,
  track_id,
  code_hmac,
  key_id,
  idempotency_token,
  buid,
  attempts_left,
  created_at,
  updated_at
)
VALUES (
  '7948e3a9-623c-4524-a390-9e4264d27b77',
  '7948e3a9-623c-4524-a390-9e4264d27a22',
  '702a66ec4fd40d57920526e8a7958cc0bb960285',
  'key_1',
  'idempotency_token1',
  'buid1',
  3,
  '2022-02-02T20:28:58.838783+00:00',
  '2022-02-02T20:28:58.838783+00:00'
), (
  '7948e3a9-623c-4524-a390-9e4264d27b88',
  '7948e3a9-623c-4524-a390-9e4264d27a22',
  '23a163139ee5d9dfba62adb61c1c6f61f0dbd4b0',
  'key_2',
  'idempotency_token2',
  'buid1',
  2,
  '2022-02-03T20:28:58.838783+00:00',
  '2022-02-03T20:30:58.838783+00:00'
);

INSERT INTO bank_authorization.attempts (
  id,
  code_id,
  attempted_hmac,
  key_id,
  buid,
  created_at,
  updated_at
)
VALUES (
  '97081435-272c-42d1-8950-fd74df92e651',
  '7948e3a9-623c-4524-a390-9e4264d27b88',
  '23a163139ee5d9dfba62adb61c1c6f61f0dbd4b0',
  'key_2',
  'buid1',
  '2022-02-03T20:30:58.838783+00:00',
  '2022-02-03T20:30:58.838783+00:00'
);
