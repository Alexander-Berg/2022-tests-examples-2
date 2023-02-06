INSERT INTO voice_gateways.voice_gateways
(id, info.host, info.ignore_certificate,
 settings.weight, settings.disabled, settings.name, settings.idle_expires_in,
 token, enabled_at)
VALUES
(
 'gateway_id_1',
 '$mockserver/test.com', TRUE,
 10, FALSE, 'gateway_name_1', 100,
 'gateway_token_1',
  CURRENT_TIMESTAMP - INTERVAL '2 hour'
),
(
  'gateway_id_2',
  '$mockserver/test.com', TRUE,
  10, FALSE, 'gateway_name_2', 100,
  'gateway_token_2',
  CURRENT_TIMESTAMP - INTERVAL '10 minute'
),
(
  'gateway_id_3',
  '$mockserver/test.com', TRUE,
  10, FALSE, 'gateway_name_3', 100,
  'gateway_token_3',
  CURRENT_TIMESTAMP - INTERVAL '2 hour'
),
(
  'gateway_id_4',
  '$mockserver/test.com', TRUE,
  10, TRUE, 'gateway_name_4', 100,
  'gateway_token_4',
  CURRENT_TIMESTAMP - INTERVAL '2 hour'
),
(
  'gateway_id_5',
  '$mockserver/test.com', TRUE,
  10, FALSE, 'gateway_name_5', 100,
  'gateway_token_5',
  null
);
