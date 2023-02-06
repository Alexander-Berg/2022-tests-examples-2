INSERT INTO eats_performer_subventions.performer_subvention_order_goals
(goal_type, source, performer_id, starts_at, finishes_at, timezone, status, target_orders_count, actual_orders_count, money_to_pay, currency,  performer_group,
 last_checked_at, created_at, updated_at)
VALUES ('dxgy', 'yt_dxgy', '1', '2022-02-01 00:00:00', '2022-02-07 00:00:00', 'Europe/Moscow', 'in_progress', 34, 0, 9217, 'rub', 'send', '2021-01-07 00:00:00',
        '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', 'yt_dxgy', '2', '2022-02-02 00:00:00', '2021-01-07 00:00:00', 'Europe/Moscow', 'finished', 66, 27, 8233, 'rub', 'not_send',
        '2022-01-07 00:00:00', '2022-01-01 00:00:00', '2021-01-01 00:00:00'),
       ('dxgy', 'yt_dxgy', '3', '2022-02-03 00:00:00', '2021-01-07 00:00:00', 'Europe/Moscow', 'failed', 97, 15, 6793, 'rub', 'not_send', '2021-01-07 00:00:00',
        '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', 'yt_dxgy', '4', '2022-02-04 00:00:00', '2021-02-09 00:00:00', 'Asia/Yekaterinburg', 'in_progress', 97, 0, 6795, 'rub', 'send', '2021-01-07 00:00:00',
        '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', 'yt_dxgy', '5', '2022-02-05 00:00:00', '2021-02-08 00:00:00', 'Europe/Moscow', 'in_progress', 98, 15, 6796, 'rub', 'send', '2021-01-07 00:00:00',
        '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', 'yt_dxgy', '6', '2021-01-05 00:00:00', '2021-01-08 00:00:00', 'Europe/Moscow', 'finished', 98, 100, 6796, 'rub', 'send', '2021-01-07 00:00:00',
        '2021-01-01 00:00:00', '2021-01-01 00:00:00'),
       ('retention', 'yt_dxgy', '7', '2022-02-01 00:00:00', '2022-02-07 00:00:00', 'Europe/Moscow', 'in_progress', 34, 0, 9217, 'rub', 'retention', '2021-01-07 00:00:00',
        '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('retention', 'yt_dxgy', '8', '2021-01-05 00:00:00', '2021-01-08 00:00:00', 'Europe/Moscow', 'finished', 98, 100, 7000, 'rub', 'retention', '2021-01-07 00:00:00',
        '2021-01-01 00:00:00', '2021-01-01 00:00:00')
        ;

-- scheduled notifications
INSERT INTO eats_performer_subventions.performer_subvention_notifications
    (goal_type, goal_id, type, status, runs_at, created_at, updated_at)
VALUES ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '1'),
        'welcome', 'created', '2022-01-01 12:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '1'),
        'check_state', 'created', '2022-01-01 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '1'),
        'finalize', 'created', '2022-01-02 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '2'),
        'welcome', 'created', '2022-01-01 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '2'),
        'check_state', 'created', '2022-01-01 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '3'),
        'welcome', 'created', '2022-01-01 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '3'),
        'check_state', 'created', '2022-01-01 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '4'),
        'welcome', 'created', '2022-01-02 12:00:00+05:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '4'),
        'check_state', 'created', '2022-01-03 00:00:00+05:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '5'),
        'welcome', 'created', '2022-01-01 15:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '5'),
        'check_state', 'created', '2022-01-01 16:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '6'),
        'finalize', 'created', '2021-01-08 16:00:00+00:00', '2021-01-01 00:00:00', '2021-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '7'),
        'welcome', 'created', '2022-01-01 12:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '8'),
        'finalize', 'created', '2021-01-08 16:00:00+00:00', '2021-01-01 00:00:00', '2021-01-01 00:00:00')
       ;
