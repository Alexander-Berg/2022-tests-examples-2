INSERT INTO referral.campaigns 
(id, campaign_name, extra_check, tanker_prefix, brand_name, series_template, status, service)
VALUES 
  (0, 'common_taxi', NULL, NULL, 'yataxi', 'custom', 'enabled', 'taxi')
;

INSERT INTO referral.creator_configs 
(id, campaign_id, zone_name, country, reward_series, success_activations_limit, enabled)
VALUES 
  (1, 0, 'moscow', NULL, 'referral', 50, TRUE)
;

INSERT INTO referral.promocodes
(id, yandex_uid, promocode, country, config_id, phone_id)
VALUES
  ('00000000000000000000000000000000', '4034039654', 'referral0', 'rus', 1, '5db2815c7984b5db628dffdc')
;

INSERT INTO referral.consumer_configs 
(campaign_id, zones, country, series_id, duration_days, is_enabled)
VALUES 
  (0, '{"moscow"}', 'rus', 'referral', 10, TRUE);

INSERT INTO referral.promocode_activations
(id, promocode_id, yandex_uid, start, finish, series_id)
VALUES
(1, '00000000000000000000000000000000', '4034039654', '2010-01-01 00:00:00.000000+03', '2030-02-01 00:00:00.000000+03', 'referral');
