INSERT INTO forwardings.talks
(
  id,
  created_at,
  length,
  forwarding_id,
  caller_phone,
  voip_succeeded
)
VALUES
(
  '3965F307FC39B1E8C2462119E7672A0F',
  CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
  10,
  'forwarding_id_1',
  '',
  null::boolean
);
