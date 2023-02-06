INSERT INTO settings
VALUES ('{
  "display_tab": true,
  "enable_stats_job": true,
  "generate_new_promocodes": true,
  "enable_payments_job": true,
  "enable_mapreduce_job": true,
  "enable_antifraud_job": true,
  "enable_notifications_job": true,
  "cities": [
    "Москва",
    "Тверь",
    "Санкт-Петербург",
    "Минск",
    "Рига"
  ]
}'::jsonb);

INSERT INTO rules (
    id, start_time, end_time, orders_provider, referrer_orders_providers, tariff_zones, taxirate_ticket,
    currency, referrer_bonus, referree_days, referree_rides, author, created_at
)
VALUES (
    '12e25ed671efab_0', '2019-01-01', '2019-10-01', NULL, NULL, ARRAY ['moscow', 'kaluga'], 'TAXIRATE-1',
    'RUB', 500, 21, 50, 'andresokol', '2019-01-01'
);

INSERT INTO referral_profiles (
    id, park_id, driver_id, promocode, invite_promocode, status, rule_id, started_rule_at, created_at
)
VALUES
    ('r0', 'p0', 'd0', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL, '2019-04-04'),
    ('r1', 'p1', 'd1', NULL, 'ПРОМОКОД1', 'in_progress', '12e25ed671efab_0', '2019-04-04', '2019-04-04');


INSERT INTO notifications (
    notification_id, notification_name, notification_kwargs,
    notification_status, referrer_park_id, referrer_driver_id,
    referral_park_id, referral_driver_id, task_date
)
VALUES (
    'notification_0'
    , 'create_new_account'
    , '{}'::jsonb
    , 'created'
    , 'p1'
    , 'd1'
    , NULL
    , NULL
    , NULL
);
