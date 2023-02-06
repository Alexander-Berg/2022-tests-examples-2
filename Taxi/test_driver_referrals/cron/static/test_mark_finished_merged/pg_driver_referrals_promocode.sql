INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at, reward_reason, current_step)
VALUES ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL, NULL, 0),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-19 13:00:00', NULL, 0);


INSERT INTO daily_stats (id, park_id, driver_id, date,
                         rides_total, rides_accounted, is_frauder)
    -- p1_d1 has stats, not yet finished (fraud orders)
VALUES ('ds1', 'p2', 'd2', '2019-04-19', 3, 3, false);
