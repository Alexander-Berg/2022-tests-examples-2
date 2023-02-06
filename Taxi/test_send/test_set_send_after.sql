-- 3 letters with the similar time for test1
-- 2 letters with the similar time for test2
-- 3 letters with the different time for test3
INSERT INTO sticker.mail_queue (
    body,
    idempotence_token,
    recipient,
    send_after
)
VALUES (
    '',
    '1',
    'test1',
    '2019-11-29 10:00:00'
),
(
    '',
    '2',
    'test1',
    '2019-11-29 10:00:01'
),
(
    '',
    '3',
    'test1',
    '2019-11-29 10:00:02'
),
(
    '',
    '4',
    'test2',
    '2019-11-29 10:00:00'
),
(
    '',
    '5',
    'test2',
    '2019-11-29 10:00:01'
),
(
    '',
    '6',
    'test3',
    '2019-11-29 10:00:00'
),
(
    '',
    '7',
    'test3',
    '2019-11-29 10:00:01'
),
(
    '',
    '8',
    'test3',
    '2019-11-29 10:05:00'
);
