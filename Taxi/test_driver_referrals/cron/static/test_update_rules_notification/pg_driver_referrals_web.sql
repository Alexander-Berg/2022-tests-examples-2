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
VALUES
(
    '12e25ed671efab_1', '2019-01-01 10:10', '2019-02-01', NULL, ARRAY ['taxi'], ARRAY ['moscow', 'kaluga'], 'TAXIRATE-1',
    'RUB', 500, 21, 50, 'andresokol', '2019-01-01'
),
(
    '12e25ed671efab_2', '2019-03-13  10:10', '2019-03-25', NULL, ARRAY ['eda', 'taxi'], ARRAY ['moscow', 'togliatti'], 'TAXIRATE-1',
    'RUB', 500, 21, 50, 'andresokol', '2019-01-01'
),
(
    '12e25ed671efab_4', '2019-03-12  10:10', '2019-03-25', NULL, ARRAY ['taxi'], ARRAY ['moscow', 'togliatti'], 'TAXIRATE-1',
    'RUB', 500, 21, 50, 'andresokol', '2019-01-01'
),
(
    '12e25ed671efab_3', '2019-04-01 10:10', '2019-05-01', NULL, ARRAY ['taxi'], ARRAY ['togliatti', 'kazan'], 'TAXIRATE-1',
    'RUB', 500, 21, 50, 'andresokol', '2019-01-01'
);

INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at, created_at)
VALUES ('r1', 'p0', 'd1', 'ПРОМОКОД1', 'ПРОМОКОД2', 'in_progress', '12e25ed671efab_1', '2019-02-20 01:00:00', '2019-02-20 01:00:00'),
       ('r2', 'p0', 'd2', 'ПРОМОКОД3', 'ПРОМОКОД32', 'in_progress', '12e25ed671efab_2', '2019-02-21 01:00:00', '2019-02-21 01:00:00'),
       ('r3', 'p0', 'd3', 'ПРОМОКОД4', 'ПРОМОКОД42', 'in_progress', '12e25ed671efab_3', '2019-02-18 01:00:00', '2019-02-18 01:00:00'),
       ('r4', 'p0', 'd4', 'ПРОМОКОД5', 'ПРОМОКОД52', 'in_progress', '12e25ed671efab_4', '2019-02-20 01:00:00', '2019-02-17 01:00:00'),
       ('r5', 'p0', 'd7', 'ПРОМОКОД6', 'ПРОМОКОД62', 'in_progress', '12e25ed671efab_5', '2019-02-20 01:00:00', '2019-02-17 01:00:00'),
       ('r6', 'p1', 'd5', 'ПРОМОКОД7', 'ПРОМОКОД72', 'in_progress', '12e25ed671efab_6', '2019-02-19 13:00:00', '2019-04-20 01:00:00');


INSERT INTO cache_referral_profiles(
    cache_id, park_id, driver_id, park_modified_at,
    driver_orders_provider, geo_tariff_zone)
VALUES  ('1', 'p0', 'd1', '2019-03-14 10:10:00+00:00', 'taxi', 'togliatti'),
        ('2', 'p0', 'd6', '2019-03-14 10:10:00+00:00', 'taxi', 'togliatti'),
        ('3', 'p0', 'd2', '2019-02-10 10:10:00+00:00', 'taxi', 'togliatti'),
        ('4', 'p1', 'd5', '2019-03-13 10:10:00+00:00', 'taxi', 'moscow'),
        ('5', 'p0', 'd7', '2019-03-13 10:10:00+00:00', 'eda', 'togliatti');
