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
       ('dxgy', 'yt_dxgy', '5', '2022-02-05 00:00:00', '2022-02-08 00:00:00', 'Europe/Moscow', 'in_progress', 98, 15, 6796, 'rub', 'send', '2021-01-07 00:00:00',
        '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dxgy', 'yt_dxgy', '6', '2021-01-05 00:00:00', '2021-01-08 00:00:00', 'Europe/Moscow', 'finished', 98, 100, 6796, 'rub', 'send', '2021-01-07 00:00:00',
        '2021-01-01 00:00:00', '2021-01-01 00:00:00'),
       ('daily_goal', 'yt_dxgy', '7', '2022-01-05 00:00:00', '2022-02-08 00:00:00', 'Europe/Moscow', 'in_progress', 10, 5, 6796, 'rub', 'daily', '2021-01-07 00:00:00',
        '2021-01-01 00:00:00', '2021-01-01 00:00:00')
        ;

-- scheduled notifications
INSERT INTO eats_performer_subventions.performer_subvention_notifications
    (id, goal_type, goal_id, type, status, runs_at, created_at, updated_at)
VALUES ('999029c4-291b-4c5e-a88e-803bed1444ac', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '1'),
        'welcome', 'created', '2022-01-01 12:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('066b9a98-4c9c-4e8a-a6cc-d7a469249c49', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '1'),
        'check_state', 'created', '2022-01-01 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('cf64f3f0-b543-432b-9377-ca757c2cc5b3', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '1'),
        'finalize', 'created', '2022-01-02 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('88300a7d-bbbd-4c8d-a067-9e90d91d71ac', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '2'),
        'welcome', 'cancelled', '2022-01-01 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('6b23ad17-9eda-4e48-b843-945e259ea218', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '2'),
        'check_state', 'created', '2022-01-01 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('8cef9f46-4aaf-4a45-91e5-f94dc83c8ec5', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '3'),
        'welcome', 'created', '2022-01-01 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('dbcb7610-9e9f-43c8-9613-c6bf5c4a921c', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '3'),
        'check_state', 'created', '2022-01-01 00:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('ff8fa509-4d02-4084-aa54-6bfdefbbb572', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '4'),
        'welcome', 'created', '2022-01-02 12:00:00+05:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('a58d3547-7078-4836-a36e-73c9c6f15509', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '4'),
        'check_state', 'created', '2022-01-03 00:00:00+05:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('19094206-eaf7-4f27-9e68-4f56a45ed10f', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '5'),
        'welcome', 'created', '2022-01-01 15:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('db7c792e-e842-4de8-8a17-c56d2f51f90a', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '5'),
        'check_state', 'created', '2022-01-01 16:00:00+00:00', '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('2acff7c1-f719-4130-bc5c-624499485ebc', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '6'),
        'finalize', 'created', '2021-01-08 16:00:00+00:00', '2021-01-01 00:00:00', '2021-01-01 00:00:00'),
       ('11111111-1111-1111-1111-111111111111', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '7'),
        'welcome', 'created', '2021-01-08 16:00:00+00:00', '2021-01-01 00:00:00', '2021-01-01 00:00:00'),
       ('22111111-1111-1111-1111-111111111122', 'dxgy', (SELECT id FROM eats_performer_subventions.performer_subvention_order_goals where performer_id = '7'),
        'finalize', 'created', '2021-01-08 16:00:00+00:00', '2021-01-01 00:00:00', '2021-01-01 00:00:00')
       ;
