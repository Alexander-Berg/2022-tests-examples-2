INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at, reward_reason, current_step)
VALUES ('r1', 'p1', 'd1', 'ПРОМОКОД1', NULL, 'completed', NULL, NULL, NULL, 0),
       ('r2', 'p2', 'd2', NULL, 'ПРОМОКОД1', 'awaiting_promocode', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_other_park', 0),
       ('r5', 'p5', 'd5', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_other_park', 0),
       ('r6', 'p6', 'd6', NULL, 'ПРОМОКОД1', 'awaiting_promocode', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_selfemployed', 0),
       ('r7', 'p7', 'd7', NULL, 'ПРОМОКОД1', 'in_progress', 'rule_with_steps', '2019-04-17 13:00:00',
        'invited_selfemployed', 0);

INSERT INTO referral_profiles (id, park_id, driver_id, promocode, invite_promocode,
                               status, rule_id, started_rule_at)
VALUES ('r3', 'p3', 'd3', 'ПРОМОКОД2', NULL, 'completed', NULL, '2019-04-20 12:00:00'),
       ('r4', 'p4', 'd4', NULL, 'ПРОМОКОД2', 'awaiting_payment', '12e25ed671efab_3', '2019-04-20 12:00:00');

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
