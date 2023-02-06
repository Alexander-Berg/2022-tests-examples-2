INSERT INTO referral.campaigns 
(id, campaign_name, extra_check, tanker_prefix, brand_name, series_template, status, service)
VALUES 
  (0, 'test_campaign', NULL, NULL, 'yataxi', 'custom', 'enabled', 'taxi')
;

INSERT INTO referral.creator_configs 
(id, campaign_id, zone_name, country, reward_series, success_activations_limit, enabled)
VALUES 
  (1, 0, 'moscow', NULL, 'tst_crtr_s', 50, TRUE),
  (2, 0, 'moscow', NULL, 'non_existent', 50, TRUE)
;

INSERT INTO referral.consumer_configs 
(campaign_id, zones, country, series_id, duration_days, is_enabled)
VALUES 
  (0, '{"moscow"}', 'rus', 'tst_cnsm_s', 10, TRUE)
;

INSERT INTO referral.promocodes
(yandex_uid, promocode, country, config_id, phone_id)
VALUES
  ('creator_yandex_uid', 'test_referral_promocode', 'rus', 1, NULL),
  ('existing_completion_uid', 'existing_completion_promocode', 'rus', 1, NULL),
  ('already_rewarded_uid', 'already_rewarded_promocode', 'rus', 1, NULL),
  ('exceeded_limit_uid', 'exceeded_limit_promocode', 'rus', 1, NULL),
  ('series_do_not_exist_uid', 'series_do_not_exist_promocode', 'rus', 2, NULL)
;

INSERT INTO referral.referral_completions
(
  yandex_uid,
  order_id,
  reward_token,
  series_id,
  promocode_id
)
VALUES
(
  'ok_acceptor_yandex_uid',
  'ok_order_id',
  NULL,
  NULL,
  (SELECT id from referral.promocodes WHERE promocode = 'test_referral_promocode')
),
(
  'existing_completion_uid',
  'existing_completion_order',
  'existing_reward_token',
  'exst_series',
  (SELECT id from referral.promocodes WHERE promocode = 'existing_completion_promocode')
),
(
  'already_rewarded_uid',
  'first_rewarded_order_for_alredy_rewarded',
  'some_token',
  NULL,
  (SELECT id from referral.promocodes WHERE promocode = 'already_rewarded_promocode')
),
(
  'already_rewarded_uid',
  'already_rewarded_order',
  NULL,
  NULL,
  (SELECT id from referral.promocodes WHERE promocode = 'already_rewarded_promocode')
),
(
  'series_do_not_exist_acceptor_uid',
  'series_do_not_exist_order',
  NULL,
  NULL,
  (SELECT id from referral.promocodes WHERE promocode = 'series_do_not_exist_promocode')
)
;
