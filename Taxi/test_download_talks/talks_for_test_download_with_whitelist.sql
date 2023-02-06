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
  'key1',
  CURRENT_TIMESTAMP - INTERVAL '20 minute',
  10,
  'forwarding_id_1',
  '',
  null::boolean,
  null
),
(
  'key2',
  CURRENT_TIMESTAMP - INTERVAL '20 minute',
  10,
  'forwarding_id_2',
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
),
(
  'key3',
  CURRENT_TIMESTAMP - INTERVAL '20 minute',
  10,
  'forwarding_id_3',
  '',
  null::boolean,
  null
),
(
  'key4',
  CURRENT_TIMESTAMP - INTERVAL '20 minute',
  10,
  'forwarding_id_4',
  '',
  null::boolean,
  null
);
