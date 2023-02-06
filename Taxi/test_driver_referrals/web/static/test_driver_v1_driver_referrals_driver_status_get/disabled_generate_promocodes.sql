INSERT INTO settings
VALUES ('{
  "display_tab": true,
  "enable_stats_job": false,
  "generate_new_promocodes": false,
  "enable_payments_job": false,
  "enable_mapreduce_job": false,
  "enable_antifraud_job": false,
  "cities": [
    "Москва",
    "Тверь",
    "Санкт-Петербург"
  ]
}'::jsonb);


INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at)
VALUES ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL);
