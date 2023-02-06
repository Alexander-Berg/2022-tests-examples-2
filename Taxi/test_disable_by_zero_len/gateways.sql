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
)
;
