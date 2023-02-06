INSERT INTO bank_userinfo.buids (
  bank_uid,
  yandex_uid,
  phone_id,
  status
)
VALUES (
  '7948e3a9-623c-4524-a390-9e4264d27a77',
  '024e7db5-9bd6-4f45-a1cd-2a442e15bde1',
  '024e7db5-9bd6-4f45-a1cd-2a442e15bdf1',
  'FINAL'
);

INSERT INTO bank_userinfo.buids_history (
  bank_uid,
  yandex_uid,
  phone_id,
  status,
  operation_type,
  operation_at
)
SELECT
  bank_uid,
  yandex_uid,
  phone_id,
  status,
  operation_type,
  operation_at
FROM bank_userinfo.buids
WHERE bank_uid = '7948e3a9-623c-4524-a390-9e4264d27a77';

UPDATE bank_userinfo.buids
SET status='BLOCKED'
WHERE bank_uid = '7948e3a9-623c-4524-a390-9e4264d27a77';

INSERT INTO bank_userinfo.buids_history (
  bank_uid,
  yandex_uid,
  phone_id,
  status,
  operation_type,
  operation_at
)
SELECT
  bank_uid,
  yandex_uid,
  phone_id,
  status,
  operation_type,
  operation_at
FROM bank_userinfo.buids
WHERE bank_uid = '7948e3a9-623c-4524-a390-9e4264d27a77';
