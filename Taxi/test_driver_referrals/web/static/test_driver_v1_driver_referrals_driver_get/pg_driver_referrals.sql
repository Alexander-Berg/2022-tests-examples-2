INSERT INTO
  rules (
    id,
    start_time,
    end_time,
    tariff_zones,
    taxirate_ticket,
    currency,
    referrer_bonus,
    referree_days,
    referree_rides,
    author,
    referrer_orders_providers
  )
VALUES
  (
    '12e25ed671efab_0',
    '2019-01-01',
    '2019-10-01',
    ARRAY [ 'moscow', 'kaluga' ],
    'TAXIRATE-1',
    'RUB',
    500,
    21,
    50,
    'andresokol',
    ARRAY ['taxi']
  ),
  (
    '12e25ed671efab_1',
    '2019-10-01',
    '2019-12-01',
    ARRAY [ 'moscow', 'kaluga' ],
    'TAXIRATE-2',
    'RUB',
    5000,
    14,
    100,
    'andresokol',
    ARRAY ['taxi']
  ),
  (
    '12e25ed671efab_2',
    '2019-01-01',
    '2019-10-01',
    ARRAY [ 'tula' ],
    'TAXIRATE-3',
    'RUB',
    5000,
    14,
    100,
    'andresokol',
    ARRAY ['taxi']
  ),
  (
    '12e25ed671efab_3',
    '2019-01-01',
    '2019-10-01',
    ARRAY [ 'riga' ],
    'TAXIRATE-4',
    'EUR',
    25,
    2,
    10,
    'andresokol',
    ARRAY ['taxi']
  );

INSERT INTO
  settings
VALUES
  (
    '{
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
}' :: jsonb
  );

INSERT INTO
  referral_profiles (
    id,
    park_id,
    driver_id,
    promocode,
    invite_promocode,
    status,
    rule_id,
    started_rule_at
  )
VALUES
  (
    'r1',
    'p1',
    'd1',
    'ПРОМОКОД1',
    NULL,
    'completed',
    NULL,
    NULL
  ),
  (
    'r2',
    'p2',
    'd2',
    NULL,
    'ПРОМОКОД1',
    'waiting_for_rule',
    NULL,
    NULL
  );

INSERT INTO couriers (
    id, courier_id, history_courier_id, park_id, driver_id, invite_promocode, created_at
)
VALUES
    ('c1', 2, NULL, 'p2', 'd2', 'ПРОМОКОД1', '2019-01-01 00:00:00Z');
