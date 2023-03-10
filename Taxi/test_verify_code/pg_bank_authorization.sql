INSERT INTO bank_authorization.tracks (
  id,
  idempotency_token,
  buid,
  operation_type,
  created_at,
  antifraud_context_id
)
VALUES (
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da1',
  'buid1',
  'start_session',
  '2021-06-12T11:50:00.0Z',
  'antifraud_context_id'
),(
  '7948e3a9-623c-4524-a390-9e4264d27a66',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da2',
  'buid2',
  'start_session',
  '2021-06-13T11:50:00.0Z',
  'antifraud_context_id'
),(
  '7948e3a9-623c-4524-a390-9e4264d27a55',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da3',
  'buid3',
  'start_session',
  '2021-06-13T11:50:00.0Z',
  'antifraud_context_id'
),(
  '7948e3a9-623c-4524-a390-9e4264d27a44',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da4',
  'buid4',
  'start_session',
  '2021-06-13T11:50:00.0Z',
  'antifraud_context_id'
),(
  '7948e3a9-623c-4524-a390-9e4264d27a33',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da5',
  'buid5',
  'start_session',
  '2021-06-13T11:50:00.0Z',
  'antifraud_context_id'
),(
  '7948e3a9-623c-4524-a390-9e4264d27a22',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da6',
  'buid6',
  'start_session',
  '2021-06-13T11:50:00.0Z',
  'antifraud_context_id'
);

INSERT INTO bank_authorization.tracks (
  id,
  idempotency_token,
  buid,
  operation_type,
  created_at
)
VALUES (
  'ccccb408-af20-4a4a-908b-e92cd5971796',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da9',
  'a41a2ef0-2140-4037-85b5-ebaa12e34224',
  'faster_payments_default_bank',
  '2021-06-13T11:50:00.0Z'
);

INSERT INTO bank_authorization.codes (
  id,
  track_id,
  code_hmac,
  key_id,
  idempotency_token,
  buid,
  created_at
)
VALUES (
  '7948e3a9-623c-4524-a390-9e4264d27b77',
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '702a66ec4fd40d57920526e8a7958cc0bb960285',
  'key_1',
  'idempotency_token1',
  'buid1',
  '2021-06-13T13:55:00Z'
),
(
  '7948e3a9-623c-4524-a390-9e4264d27b66',
  '7948e3a9-623c-4524-a390-9e4264d27a66',
  '702a66ec4fd40d57920526e8a7958cc0bb960285',
  'key_1',
  'idempotency_token2',
  'buid2',
  '2021-06-13T13:55:00Z'
),
(
  '7948e3a9-623c-4524-a390-9e4264d27b55',
  '7948e3a9-623c-4524-a390-9e4264d27a55',
  '23a163139ee5d9dfba62adb61c1c6f61f0dbd4b0',
  'key_1',
  'idempotency_token3',
  'buid3',
  '2021-06-13T13:55:00Z'
),
(
  '7948e3a9-623c-4524-a390-9e4264d27b44',
  '7948e3a9-623c-4524-a390-9e4264d27a44',
  '23a163139ee5d9dfba62adb61c1c6f61f0dbd4b0',
  'key_not_found',
  'idempotency_token4',
  'buid4',
  '2021-06-13T13:55:00Z'
),
(
  '7948e3a9-623c-4524-a390-9e4264d27b33',
  '7948e3a9-623c-4524-a390-9e4264d27a33',
  '68436b85c210bac3a88b35d067fd27f375238c51',
  'key_2',
  'idempotency_token5',
  'buid5',
  '2021-06-13T13:55:00Z'
),
(
  '7948e3a9-623c-4524-a390-9e4264d27b22',
  '7948e3a9-623c-4524-a390-9e4264d27a22',
  '702a66ec4fd40d57920526e8a7958cc0bb960285',
  'key_1',
  'idempotency_token6',
  'buid6',
  '2021-06-13T13:40:00Z'
);


INSERT INTO bank_authorization.codes (
  id,
  track_id,
  code_hmac,
  key_id,
  idempotency_token,
  buid,
  created_at,
  request_id
)
VALUES (
  'ccccb408-af20-4a4a-908b-e92cd5971796',
  'ccccb408-af20-4a4a-908b-e92cd5971796',
  'code_hmac',
  'key_1',
  'fps_idempotency_token',
  'a41a2ef0-2140-4037-85b5-ebaa12e34224',
  '2021-06-13T13:59:00Z',
  'e47140c9-2843-4004-b8f2-4f6e2af06172'
);
