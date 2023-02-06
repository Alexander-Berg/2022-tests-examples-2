INSERT INTO settings
VALUES
( '{
  "display_tab": true,
  "enable_stats_job": true,
  "generate_new_promocodes": true,
  "enable_payments_job": true,
  "enable_mapreduce_job": true,
  "enable_antifraud_job": true,
  "cities": [
    "Москва",
    "Тверь",
    "Санкт-Петербург",
    "Рига"
  ]
}'::jsonb);


INSERT INTO referral_profiles (
    id, park_id, driver_id, promocode, invite_promocode, status, rule_id, started_rule_at
)
VALUES
    ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL),
    ('r2', 'p2', 'd2', 'ПРОМОКОД2', 'ПРОМОКОД1', 'completed', NULL, NULL);


INSERT INTO couriers (
    id, courier_id, history_courier_id, park_id, driver_id, invite_promocode, created_at
)
VALUES
    ('c1', 1, NULL, NULL, NULL, 'ПРОМОКОД1', '2019-01-01 00:00:00Z'),
    ('c2', 2, NULL, 'p2', 'd2', 'ПРОМОКОД1', '2019-01-01 00:00:00Z');
