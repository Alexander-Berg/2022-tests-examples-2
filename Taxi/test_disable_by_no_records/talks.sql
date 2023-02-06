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
  10,
  'forwarding_id_1',
  '',
  null::boolean,
  null
),
(
  'talk_2',
  '2019-03-20 09:40:00'::timestamp AT TIME ZONE 'UTC',
  10,
  'forwarding_id_2',
  '',
  null::boolean,
  null
),
(
  'talk_3',
  '2019-03-20 09:40:00'::timestamp AT TIME ZONE 'UTC',
  10,
  'forwarding_id_3',
  '',
  null::boolean,
  null
),
(
  'talk_4',
  '2019-03-20 09:40:00'::timestamp AT TIME ZONE 'UTC',
  10,
  'forwarding_id_4',
  '',
  null::boolean,
  '4'  -- already downloaded
),
(
  'talk_5',
  '2019-03-20 08:40:00'::timestamp AT TIME ZONE 'UTC',  -- to early to check
  10,
  'forwarding_id_5',
  '',
  null::boolean,
  null
),
(
  'talk_zero_length',
  '2019-03-20 09:40:00'::timestamp AT TIME ZONE 'UTC',
  0, -- don't check zero length talks
  'forwarding_id_5',
  '',
  null::boolean,
  null
);
