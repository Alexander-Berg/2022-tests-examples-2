INSERT INTO piecework.agent_employee (
    agent_employee_id,
    start_date,
    stop_date,
    country,
    login,
    branch,
    created,
    updated,
    tariff_type,
    rating_factor,
    timezone
) VALUES
(
    '1',
    '2022-2-16',
    '2022-3-1',
    'ru',
    'test_1',
    'b',
    NOW(),
    NOW(),
    'support-taxi',
    1,
    'Asia/Barnaul'
),
(
     '2',
     '2022-2-16',
     '2022-3-1',
     'ru',
     'test_2',
     'b',
     NOW(),
     NOW(),
     'support-taxi',
     1,
     'Asia/Irkutsk'
),
(
    '3',
    '2022-2-16',
    '2022-3-1',
    'ru',
    'test_3',
    'b',
    NOW(),
    NOW(),
    'support-taxi',
    1,
    NULL
),
(
    '4',
    '2022-2-16',
    '2022-3-1',
    'ru',
    'test_4',
    'b',
    NOW(),
    NOW(),
    'support-taxi',
    1,
    'Asia/Yekaterinburg'
),
(
    '5',
    '2022-2-16',
    '2022-3-1',
    'ru',
    'test_5',
    'b',
    NOW(),
    NOW(),
    'support-taxi',
    1,
    'Europe/Moscow'
);

INSERT INTO piecework.mapping_payday_uid_login(login, payday_uid) VALUES
    ('test_1', 'test_uid_1'),
    ('test_2', 'test_uid_2'),
    ('test_3', 'test_uid_3'),
    ('test_4', 'test_uid_4'),
    ('test_5', 'test_uid_5');

INSERT INTO piecework.payday_employee_loan (
    employee_id,
    company_id,
    date_time,
    loan_id,
    amount,
    paid_at,
    period,
    oebs_sent_status,
    updated
) VALUES
(
    'test_uid_1',
    '1',
    '2022-2-20 00:00:00',
    '1',
    15.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    'new',
    NOW()
),
(
    'test_uid_1',
    '11',
    '2022-1-31 16:59:00',
    '11',
    11.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    'sent',
    '2022-1-31 16:59:00'
),
(
    'test_uid_2',
    '2',
    '2022-2-15 23:00:00',
    '2',
    16.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    'new',
    NOW()
),
(
    'test_uid_2',
    '21',
    '2022-2-16 23:00:00',
    '21',
    18.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    'new',
    NOW()
),
(
    'test_uid_2',
    '211',
    '2022-2-28 15:59:00',
    '211',
    18.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    'new',
    NOW()
),
(
    'test_uid_3',
    '31',
    '2022-2-24 11:00:00',
    '31',
    16.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    'new',
    NOW()
),
(
    'test_uid_3',
    '3',
    '2022-2-24 15:00:00',
    '3',
    13.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    'new',
    NOW()
),
(
    'test_uid_4',
    '4',
    '2022-2-26 23:00:00',
    '4',
    12.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    'new',
    NOW()
),
(
    'test_uid_4',
    '4',
    '2022-1-26 23:00:00',
    '4_s',
    12.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    'sent',
    '2022-1-31 16:59:00'
),
(
    'test_uid_4',
    '4',
    '2022-2-24 23:00:00',
    '4_f',
    112.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    'failed',
    NOW()
),
(
    'test_uid_5',
    '5',
    '2022-1-31 20:59:00',
    '5',
    16.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    'failed',
    '2022-1-31 16:59:00'
);
