INSERT INTO forwardings.forwardings
(
  id,
  external_ref_id,
  gateway_id,
  consumer_id,
  state,
  created_at,
  expires_at,
  src_type,
  dst_type,
  caller_phone,
  callee_phone,
  nonce,
  call_location,
  region_id
)
VALUES
(
  'forwarding_id_1',
  '',
  'gateway_id_1',
  0,
  'created',
  CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
  CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
  'passenger',
  'passenger',
  '',
  '',
  'nonce_1',
  (0.0, 0.0),
  NULL
),
(
  'forwarding_id_2',
  '',
  'gateway_id_2',
  0,
  'created',
  CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
  CURRENT_TIMESTAMP AT TIME ZONE 'UTC',
  'passenger',
  'passenger',
  '',
  '',
  'nonce_2',
  (0.0, 0.0),
  1
);
