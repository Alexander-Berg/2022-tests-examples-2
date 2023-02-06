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
    "Калуга"
  ]
}'::jsonb);

INSERT INTO rules (id, start_time, end_time, orders_provider,
                   tariff_zones, taxirate_ticket, currency,
                   referrer_bonus, referree_days, referree_rides, author,
                   referrer_orders_providers, created_at)
VALUES ('rule1', '2021-12-10', '2021-12-20', 'eda',
        ARRAY ['moscow'], 'TAXIRATE-1', 'RUB',
        501, 11, 21, 'rndr', ARRAY['eda'], '2021-12-28 00:00:01'),
       ('rule2', '2021-12-10', '2021-12-20', 'eda',
        ARRAY ['kaluga'], 'TAXIRATE-2', 'RUB',
        502, 12, 22, 'rndr', ARRAY['eda'], '2021-12-28 00:00:02');

INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at)
VALUES ('r11', 'p11', 'd11', 'ПРОМОКОД2', NULL, 'completed', NULL, NULL),
       ('r12', 'p12', 'd12', NULL, 'ПРОМОКОД2', 'waiting_for_rule', NULL, NULL);
