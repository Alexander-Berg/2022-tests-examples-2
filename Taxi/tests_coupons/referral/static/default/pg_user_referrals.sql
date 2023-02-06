INSERT INTO referral.campaigns 
(id, campaign_name, extra_check, tanker_prefix, brand_name, series_template, status, service)
VALUES 
  (0, 'common_taxi',          NULL,               NULL            ,  'yataxi',  'custom', 'enabled', 'taxi'),
  (1, 'light_business',       'business_account', 'light_business',  'yataxi',  'custom', 'by_experiment', 'taxi'),
  (2, 'common_yango',         NULL,               NULL            ,  'yango' ,  'custom', 'enabled', 'taxi'),
  (3, 'light_business_yango', 'business_account', 'light_business',  'yango' ,  'custom', 'by_experiment', 'taxi'),
  (4, 'common_uber',          NULL,               NULL            ,  'yauber',  'brand',  'by_experiment', 'taxi'),
  (5, 'common_go',            NULL,               NULL            ,  'yataxi',  'custom', 'by_experiment', 'taxi'),
  (6, 'grocery_referral', NULL, NULL, 'yangodeli', 'custom', 'enabled', 'grocery')
;

ALTER SEQUENCE referral.campaigns_id_seq RESTART WITH 10;

INSERT INTO referral.creator_configs 
(id, campaign_id, zone_name, country, reward_series, success_activations_limit, enabled)
VALUES 
  (1, 0, 'moscow', NULL, 'referral', 50, TRUE),
  (2, 0, 'moscow_percent_promocode', NULL, 'seriespercentreferral', 50, TRUE),
  (3, 0, 'moscow_no_percent_promocode', NULL, 'referral', 50, TRUE),
  (4, 0, 'moscow_ppt_promocode', NULL, 'seriespptreferral', 50, TRUE),
  (5, 1, 'moscow_business', NULL, 'referral', 50, TRUE),
  (8, 0, 'spb', NULL, 'referral', 50, TRUE),
  (9, 1, 'spb', NULL, 'referral', 50, TRUE),
  (10, 0, 'houston', NULL, 'referral', 50, TRUE),
  (11, 2, 'helsinki', NULL, 'referral', 50, TRUE),
  (12, 2, 'moscow', NULL, 'referral', 50, TRUE),
  (13, 3, 'moscow', NULL, 'referral', 50, TRUE),
  (14, 2, 'spb', NULL, 'referral', 50, TRUE),
  (15, 4, 'moscow', NULL, 'referral', 50, TRUE),
  (16, 1, 'moscow', NULL, 'referral', 50, TRUE),
  (17, 0, 'houston', NULL, 'referral', 100, FALSE),
  (18, 5, 'samara', NULL, 'referral', 100, TRUE),
  (19, 5, NULL, 'rus', 'referral', 100, TRUE),
  (20, 3, 'chicago', NULL, 'referral', 50, TRUE)
;

ALTER SEQUENCE referral.creator_configs_id_seq RESTART WITH 25;

-- Temp sync zones with zone_name and status with enabled
WITH update_data AS(
    SELECT
      id,
      (CASE WHEN zone_name IS NULL THEN NULL ELSE array_agg(zone_name) END) as zones,
      (CASE WHEN enabled THEN 'for_new_users' ELSE 'for_old_users' END) as status
    FROM referral.creator_configs
    GROUP BY id)
UPDATE referral.creator_configs c
    SET
      zones = d.zones,
      status = d.status::referral.creator_config_status
    FROM update_data d
    WHERE c.id = d.id;

INSERT INTO referral.consumer_configs 
(campaign_id, zones, country, series_id, duration_days, is_enabled)
VALUES 
  (0, '{"moscow"}', 'rus', 'referral', 10, TRUE),
  (0, '{"moscow"}', 'rus', 'msk_referral_series', 10, FALSE),
  (0, '{"moscow"}', 'rus', 'seriespercentreferral', 31, FALSE),
  (0, '{"moscow_percent_promocode"}', 'rus', 'seriespercentreferral', 10, TRUE),
  (4, '{"spb"}', 'rus', 'seriespercentreferral', 10, TRUE),
  (2, '{"moscow"}', 'rus', 'referral', 10, TRUE),
  (3, '{"chicago","houston"}', 'rus', 'referral', 10, TRUE),
  (5, '{"moscow_ppt_promocode"}', 'rus', 'referral', 10, TRUE),
  (0, NULL, 'rus', 'referral', 10, TRUE)
;
