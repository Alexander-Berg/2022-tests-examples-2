INSERT INTO bank_authorization.tracks (
  id,
  idempotency_token,
  buid,
  operation_type,
  created_at
)
VALUES (
  'ccccb408-af20-4a4a-908b-e92cd5971794',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da7',
  'buid1',
  'start_session',
  '2021-06-12T11:50:00.0Z'
),(
  'ccccb408-af20-4a4a-908b-e92cd5971795',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da8',
  'buid2',
  'start_session',
  '2021-06-13T11:50:00.0Z'
);

INSERT INTO bank_authorization.codes (
  track_id,
  code_hmac,
  key_id,
  idempotency_token,
  buid,
  created_at
)
VALUES (
  'ccccb408-af20-4a4a-908b-e92cd5971795',
  '702a66ec4fd40d57920526e8a7958cc0bb960285',
  'key_1',
  'idempotency_token1',
  'buid2',
  '2021-06-13T13:55:00Z'
),
(
  'ccccb408-af20-4a4a-908b-e92cd5971795',
  '702a66ec4fd40d57920526e8a7958cc0bb960285',
  'key_1',
  'idempotency_token2',
  'buid2',
  '2021-06-13T13:55:00Z'
),
(
  'ccccb408-af20-4a4a-908b-e92cd5971795',
  '23a163139ee5d9dfba62adb61c1c6f61f0dbd4b0',
  'key_1',
  'idempotency_token3',
  'buid2',
  '2021-06-13T11:55:00Z'
),
(
  'ccccb408-af20-4a4a-908b-e92cd5971795',
  '23a163139ee5d9dfba62adb61c1c6f61f0dbd4b0',
  'key_not_found',
  'idempotency_token4',
  'buid2',
  '2021-06-13T11:55:00Z'
),
(
  'ccccb408-af20-4a4a-908b-e92cd5971795',
  '68436b85c210bac3a88b35d067fd27f375238c51',
  'key_2',
  'idempotency_token5',
  'buid2',
  '2021-06-13T11:55:00Z'
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
), (
  'ccccb408-af20-4a4a-908b-e92cd5971797',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0db0',
  'a41a2ef0-2140-4037-85b5-ebaa12e34224',
  'faster_payments_default_bank',
  '2021-06-13T11:50:00.0Z'
);

INSERT INTO bank_authorization.codes (
  track_id,
  code_hmac,
  key_id,
  idempotency_token,
  buid,
  created_at
)
VALUES (
  'ccccb408-af20-4a4a-908b-e92cd5971797',
  'e47140c9-2843-4004-b8f2-4f6e2af06172',
  'key_1',
  'fps_idempotency_token1',
  'a41a2ef0-2140-4037-85b5-ebaa12e34224',
  '2021-06-13T13:55:00Z'
),
(
  'ccccb408-af20-4a4a-908b-e92cd5971797',
  'e47140c9-2843-4004-b8f2-4f6e2af06172',
  'key_1',
  'fps_idempotency_token2',
  'a41a2ef0-2140-4037-85b5-ebaa12e34224',
  '2021-06-13T13:55:00Z'
),
(
  'ccccb408-af20-4a4a-908b-e92cd5971797',
  'e47140c9-2843-4004-b8f2-4f6e2af06172',
  'key_1',
  'fps_idempotency_token3',
  'a41a2ef0-2140-4037-85b5-ebaa12e34224',
  '2021-06-13T11:55:00Z'
);
