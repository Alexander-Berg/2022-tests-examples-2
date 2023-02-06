INSERT INTO referral.campaigns 
(id, campaign_name, extra_check, tanker_prefix, brand_name, service)
VALUES 
  (0, 'common_taxi', NULL, NULL, 'default_brand', 'taxi'),
  (1, 'grocery_referral', NULL, NULL, 'default_brand', 'grocery')
;

INSERT INTO referral.creator_configs 
(id, campaign_id, zone_name, country, reward_series, success_activations_limit, enabled)
VALUES 
  (1, 0, 'moscow', NULL, 'referral', 50, TRUE),
  (2, 1, NULL, 'rus', 'referral', 100, TRUE)
;

INSERT INTO referral.promocodes
(id, yandex_uid, campaign_id, promocode, country, config_id, phone_id)
VALUES
('00000000000000000000000000000000', '123456789', 0, 'basic_ok_referral', 'rus', 1, NULL),
('00000000000000000000000000000001', '123456799', 0, 'bad_country_referral', 'non_existent', 1, NULL),
('00000000000000000000000000000002', '123456800', 1, 'grocery_ok_referral', 'rus', 2, NULL)
;
