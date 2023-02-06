INSERT INTO referral.campaigns 
(id, campaign_name, extra_check, tanker_prefix, brand_name, series_template, status, service)
VALUES 
  (0, 'test_campaign', NULL, NULL, 'yataxi', 'custom', 'enabled', 'taxi'),
  (1, 'test_campaign1', NULL, NULL, 'yataxi', 'custom', 'enabled', 'taxi'),
  (2, 'test_campaign2', NULL, NULL, 'yataxi', 'custom', 'enabled', 'taxi')
;

INSERT INTO referral.creator_configs 
(id, campaign_id, zone_name, country, reward_series, success_activations_limit, enabled,
 rides_for_reward)
VALUES 
  (1, 0, 'moscow', NULL, 'referral', 50, TRUE, 1),
  (2, 1, 'moscow', NULL, 'referral', 50, TRUE, 2),
  (3, 2, 'moscow', NULL, 'referral', 50, TRUE, 3)
;

INSERT INTO referral.consumer_configs 
(campaign_id, zones, country, series_id, duration_days, is_enabled)
VALUES 
  (0, '{"moscow"}', 'rus', 'referral', 10, TRUE)
;

INSERT INTO referral.promocodes
(yandex_uid, promocode, country, config_id, phone_id)
VALUES
  ('creator_yandex_uid', 'test_coupon', 'rus', 1, NULL),
  ('creator_yandex_uid1', 'test_coupon1', 'rus', 2, NULL),
  ('creator_yandex_uid2', 'test_coupon2', 'rus', 3, NULL)
;
