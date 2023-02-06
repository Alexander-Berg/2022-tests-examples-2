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

INSERT INTO rules (id, start_time, end_time, tariff_zones, taxirate_ticket, currency,
                   referrer_bonus, referree_days, referree_rides, author, tariff_classes)
VALUES ('12e25ed671efab_1', '2019-04-20 09:00:00', '2019-12-01 12:00:00',
        ARRAY ['moscow', 'kaluga'], 'TAXIRATE-2', 'RUB', 5000, 14, 2, 'andresokol', ARRAY['econom']),

       ('12e25ed671efab_3', '2019-04-20 00:00:00', '2019-04-20 13:00:00',
        ARRAY ['riga'], 'TAXIRATE-3', 'EUR', 25, 1, 4, 'andresokol', NULL);

INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at)
VALUES ('r0', 'p0', 'd0', 'ПРОМОКОД1', 'ПРОМОКОД2', 'in_progress', '12e25ed671efab_1', '2019-04-20 01:00:00'),
       ('r1', 'p1', 'd1', 'ПРОМОКОД2', 'ПРОМОКОД1', 'in_progress', '12e25ed671efab_3', '2019-04-19 13:00:00');


INSERT INTO synced_orders (order_id, park_id, driver_id, nearest_zone, created_at, tariff_class, orders_provider)
VALUES ('o1', 'p0', 'd0', 'moscow', '2019-04-20 00:01:00', 'econom', 'taxi'), -- before rule started
       ('o2', 'p0', 'd0', 'moscow', '2019-04-20 01:01:00', 'econom', 'taxi'), -- OK
       ('o3', 'p0', 'd0', 'kaluga', '2019-04-20 01:40:00', 'comfort', 'taxi'), -- tariff not matched
       ('o4', 'p0', 'd0', 'troick', '2019-04-20 02:40:00', 'econom', 'taxi'), -- outside zones

       ('o5', 'p1', 'd1', 'riga', '2019-04-20 01:40:00', NULL, 'taxi'),   -- OK
       ('o6', 'p1', 'd1', 'riga', '2019-04-20 14:40:00', NULL, 'taxi');   -- after rule ended

INSERT INTO daily_stats (id, park_id, driver_id, date, rides_total, rides_accounted, is_frauder)
VALUES ('i1', 'p1', 'd1', '2019-04-20', 0, 1, NULL); -- should be updated
