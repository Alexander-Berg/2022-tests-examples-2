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
VALUES ('r0', 'p0', 'd0', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL),
       ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'in_progress', '12e25ed671efab_3', NULL),

       -- driver p3_d3 has 1 ride during gap in rules, NO RULE ASSIGNED
       ('r3', 'p3', 'd3', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL),

       -- driver p4_d4 has 1 ride outside any zone, NO RULE ASSIGNED
       ('r4', 'p4', 'd4', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL),

       -- driver p5_d5 has no rides TODAY, NO RULE ASSIGNED
       ('r5', 'p5', 'd5', NULL, 'ПРОМОКОД1', 'waiting_for_rule', NULL, NULL);


INSERT INTO rules (id, start_time, end_time, tariff_zones, taxirate_ticket, currency,
                   referrer_bonus, referree_days, referree_rides, author)
VALUES ('12e25ed671efab_0', '2019-04-20 12:00:00', '2019-10-01 12:00:00',
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-1', 'RUB', 500, 21, 1, 'andresokol'),
       ('12e25ed671efab_1', '2019-04-20 09:00:00', '2019-12-01 12:00:00',
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-2', 'RUB', 5000, 14, 2, 'andresokol'),
       ('12e25ed671efab_2', '2018-01-01 12:00:00', '2018-02-01 12:00:00',
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-2', 'RUB', 5000, 14, 3, 'andresokol'),

       -- gap in riga from 04:00 to 12:00
       ('12e25ed671efab_3', '2019-04-20 00:00:00', '2019-04-20 04:00:00',
        ARRAY ['riga'], 'TAXIRATE-3', 'EUR', 25, 2, 4, 'andresokol'),
       ('12e25ed671efab_4', '2019-04-20 12:00:00', '2019-10-01 12:00:00',
        ARRAY ['riga'], 'TAXIRATE-3', 'EUR', 25, 2, 5, 'andresokol');


INSERT INTO daily_stats (id, park_id, driver_id, date,
                         rides_total, rides_accounted, is_frauder)
VALUES ('ds1', 'p1', 'd1', '2019-04-20', 1, 1, NULL),
       ('ds2', 'p2', 'd2', '2019-04-19', 1, 1, NULL),
       ('ds3', 'p3', 'd3', '2019-04-20', 1, 1, false),
       ('ds4', 'p4', 'd4', '2019-04-20', 1, 1, NULL),
       ('ds5', 'p4', 'd4', '2019-04-19', 1, 1, true),
       ('ds6', 'p4', 'd4', '2019-04-18', 1, 1, true);
