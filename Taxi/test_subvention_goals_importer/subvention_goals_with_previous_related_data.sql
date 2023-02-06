INSERT INTO eats_performer_subventions.performer_subvention_order_goals
(source, source_cursor, performer_id, starts_at, finishes_at, timezone, status, target_orders_count, actual_orders_count, money_to_pay, currency,  performer_group,
 last_checked_at, created_at, updated_at)
VALUES ('yt_dxgy', NULL, '1', '2022-02-01T00:00:00+03:00', '2022-02-07T23:59:59+03:00', 'Europe/Moscow', 'in_progress', 34, 0, 9217, 'rub', 'send', NULL,
        '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('yt_dxgy', NULL, '2', '2022-02-02T00:00:00+03:00', '2022-01-07T23:59:59+03:00', 'Europe/Moscow', 'finished', 66, 0, 8233, 'rub', 'not_send',
        '2022-01-07 00:00:00', '2022-01-01 00:00:00', '2021-01-01 00:00:00'),
       ('yt_dxgy', '2022-12-20 01:00:00', '450', '2020-12-28T00:00:00+03:00', '2020-12-30T23:59:59+03:00', 'Europe/Moscow', 'failed', 97, 0, 6793, 'rub', 'not_send', '2021-01-07T00:00:00+03:00',
        '2022-01-01 00:00:00', '2022-01-01 00:00:00'),
       ('yt_dxgy', '2022-12-20 01:00:00', '540', '2022-12-28T00:00:00+03:00', '2022-12-30T23:59:59+03:00', 'Europe/Moscow', 'in_progress', 97, 0, 6795, 'rub', 'send', '2021-01-07T00:00:00+05:00',
        '2022-01-01 00:00:00', '2022-01-01 00:00:00');
