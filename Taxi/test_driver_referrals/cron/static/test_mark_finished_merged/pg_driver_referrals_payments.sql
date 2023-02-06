INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at, reward_reason, current_step)
VALUES ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL, NULL, 0),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-19 13:00:00', NULL, 0),
       ('r4', 'p4', 'd4', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-17 13:00:00', NULL, 0),
       ('r6', 'p6', 'd6', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_other_park', 0);

--INSERT INTO rules (id, start_time, end_time, tariff_zones, taxirate_ticket, currency,
--                   referrer_bonus, referree_days, referree_rides, author, steps)
--VALUES ('r1', '2019-04-01 00:00:00', '2019-10-01 12:00:00',
--        ARRAY ['riga'], 'TAXIRATE-3', 'EUR', 25, 2, 2, 'andresokol', ARRAY['{}'::jsonb]);


INSERT INTO daily_stats (id, park_id, driver_id, date,
                         rides_total, rides_accounted, is_frauder)
    -- p1_d1 has stats, not yet finished (fraud orders)
VALUES ('ds1', 'p1', 'd1', '2019-04-19', 1, 1, false),
       ('ds2', 'p1', 'd1', '2019-04-18', 9, 9, true),

       -- p2_d2 has started y-day, but already done
       ('ds3', 'p2', 'd2', '2019-04-19', 5, 5, false),

       -- p3_d3 should fail, no orders

       -- p4_d4 has finished just in time
       ('ds4', 'p4', 'd4', '2019-04-19', 1, 1, false),
       ('ds5', 'p4', 'd4', '2019-04-18', 1, 1, false),

        -- p6_d6 has finished just in time
       ('ds8', 'p6', 'd6', '2019-04-19', 1, 1, false),
       ('ds9', 'p6', 'd6', '2019-04-18', 2, 2, false);
