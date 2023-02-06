INSERT INTO bank_communications.push_subscriptions (
  subscription_id,
  bank_uid,
  xiva_subscription_id,
  uuid,
  device_id,
  locale,
  status,
  created_at,
  updated_at
)
VALUES (
  '7948e3a9-623c-4524-a390-9e4264d27a01',
  '7948e3a9-623c-4524-a390-9e4264d27a11',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da1',
  'uuid1',
  'deviceid1',
  'ru',
  'ACTIVE',
  '2022-02-01T20:28:58.838783+00:00',
  '2022-02-02T20:28:58.838783+00:00'
), (
  '7948e3a9-623c-4524-a390-9e4264d27a02',
  '7948e3a9-623c-4524-a390-9e4264d27a12',
  '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da2',
  'uuid2',
  'deviceid2',
  'ru',
  'ACTIVE',
  '2022-02-01T20:28:58.838783+00:00',
  '2022-02-02T20:28:58.838783+00:00'
);

INSERT INTO bank_communications.masked_buids (
  bank_uid,
  masked_buid
)
VALUES (
  '7948e3a9-623c-4524-a390-9e4264d27a12',
  '11111111-1111-1111-1111-111111111111'
);

