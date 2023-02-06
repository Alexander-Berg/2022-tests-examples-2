INSERT INTO voice_gateways.voice_gateways
(id, info.host, info.ignore_certificate,
 settings.weight, settings.disabled, settings.name, settings.idle_expires_in,
 token)
VALUES
(
 'gateway_id_1',
 '$mockserver/test.com', TRUE,
 10, FALSE, 'gateway_name_1', 100,
 'gateway_token_1'
),
(
  'gateway_id_2',
  '$mockserver/test.com', TRUE,
  10, FALSE, 'gateway_name_2', 100,
  'gateway_token_2'
),
(
  'gateway_id_3',
  '$mockserver/test.com', TRUE,
  10, TRUE, 'gateway_name_3', 100,
  'gateway_token_3'
);
