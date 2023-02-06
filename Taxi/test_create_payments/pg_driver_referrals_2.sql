INSERT INTO settings
VALUES ('{
  "display_tab": true,
  "enable_stats_job": true,
  "generate_new_promocodes": true,
  "enable_payments_job": true,
  "enable_mapreduce_job": true,
  "enable_antifraud_job": true,
  "cities": [
    "Москва",
    "Тверь",
    "Санкт-Петербург"
  ]
}'::jsonb);

INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at)
VALUES ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, '2019-04-20 12:00:00'),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'awaiting_payment', 'rule_with_steps', '2019-04-20 12:00:00');
