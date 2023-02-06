INSERT INTO eats_performer_subventions.performer_subvention_order_goals
(goal_type, source, performer_id, unique_driver_id, starts_at, finishes_at, timezone, status, target_orders_count, actual_orders_count, money_to_pay, currency,  performer_group,
 last_checked_at, created_at, updated_at)
VALUES ('dxgy', 'yt_dxgy', '1', 'unique-1', '2022-02-01T00:00:00+03:00', '2022-02-07T23:59:59+03:00', 'Europe/Moscow', 'in_progress', 34, 0, 9217, 'rub', 'send', NULL,
        '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('daily_goal', 'yt_dxgy', '2', 'unique-2', '2022-02-02T00:00:00+03:00', '2022-02-07T23:59:59+03:00', 'Europe/London', 'in_progress', 10, 0, 1000, 'rub', 'not_send',
        '2022-01-07 00:00:00', '2022-01-01 00:00:00', '2022-01-01T03:00:00+03:00')
