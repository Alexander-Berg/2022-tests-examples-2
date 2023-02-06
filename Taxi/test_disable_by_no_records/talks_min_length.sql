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
  'talk_1',
  '2019-03-20 09:40:00'::timestamp AT TIME ZONE 'UTC',
  20,
  'forwarding_id_1',
  '',
  null::boolean,
  null
),
(
  'talk_2',
  '2019-03-20 09:40:00'::timestamp AT TIME ZONE 'UTC',
  2,
  'forwarding_id_2',
  '',
  null::boolean,
  null
);
