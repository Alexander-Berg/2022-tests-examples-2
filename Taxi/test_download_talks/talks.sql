INSERT INTO forwardings.talks
(
  id,
  created_at,
  length,
  forwarding_id,
  caller_phone,
  voip_succeeded,
  s3_key
)
VALUES
(
  '3965F307FC39B1E8C2462119E7672A0F',
  CURRENT_TIMESTAMP - INTERVAL '20 minute',
  10,
  'forwarding_id_1',
  '',
  null::boolean,
  null
),
(
  'too_fresh_talk',
  CURRENT_TIMESTAMP,
  10,
  'forwarding_id_1',
  '',
  null::boolean,
  null
);
