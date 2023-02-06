INSERT INTO iiko_integration.orders
    (
        id, idempotency_token, invoice_id, restaurant_id, version, expected_cashback_percentage, status, total_price, complement_amount, discount, currency,
        items, changelog, status_history, restaurant_order_id,
        payment_method_type, payment_method_id, yandex_uid, personal_email_id
    )
VALUES
    (
        '01', '01', 'invoice_01', 'restaurant01', 3, 30, ('PAYMENT_CONFIRMED', 'CLEARED', '2020-04-04 20:00:00+3'::timestamptz, '2020-04-04 20:00:00+3'::timestamptz), 170, 50, 5, 'RUB',

        --  prd_id, prnt_id, name,           quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement
        ARRAY[
            ('01', NULL,     'Hamburger',    3,      50,       150,     150,      0,   0,     25,  20,    1,      50),
            ('02', NULL,     'Cola',         0.1,    250,      25.0,    20.0,     5.0, 20,    0,   0,     2,      NULL),
            ('03', NULL,     'French_fries', 0,      100,      0,       0,        0,   0,     0,   0,     3,      0)
        ]::ORDER_ITEM[],
         ARRAY[
            (
                'charge', 1,
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,    0,  0,  25, 20, 1,     50),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,    25, 20, 0,  0,  2,     NULL),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,     0,  0,  0,  0,  3,     50)
                ]::ORDER_ITEM[],
                300,
                'done',
                '2020-04-04 20:00:00+3'::timestamptz,
                '2020-04-04 20:00:00+3'::timestamptz,
                'charge_1',
                NULL,
                100
            ),
            (
                'refund', 2,
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,    0,  0,  25, 20, 1,     50),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,    25, 20, 0,  0,  2,     NULL),
                    ('03', NULL, 'French_fries',    0,      100,    0,      0,      0,  0,  0,  0,  3,     0)
                ]::ORDER_ITEM[],
                -50,
                'processing',
                '2020-04-04 20:00:00+3'::timestamptz,
                '2020-04-04 20:00:00+3'::timestamptz,
                'refund_2',
                -- ticket, ticket_type, reason_code, operator_login
                ('TAXITICKET-1', 'startrack', 'reason_code_1', 'login'),
                -50
            ),
            (
                'refund', 3,
                ARRAY[
                        ('01', NULL, 'Hamburger',       3,      50,     150,    150,    0,  0,  25, 20, 1,     50),
                        ('02', NULL, 'Cola',            0.1,    250,    25.0,   20.0,   5.0, 20, 0, 0,  2,     NULL),
                        ('03', NULL, 'French_fries',    0,      100,    0,      0,      0,  0,  0,  0,  3,     0)
                ]::ORDER_ITEM[],
                -80,
                'pending',
                '2020-04-04 20:00:00+3'::timestamptz,
                '2020-04-04 20:00:00+3'::timestamptz,
                NULL,
                ('CHATTERBOX-2', 'chatterbox', 'unknown_reason_code', 'login'),
                0
            )
        ]::ORDER_CHANGE_EVENT[],
        ARRAY[('PENDING', 'INIT', '2020-04-04 20:00:00+3'::timestamptz, '2020-04-04 20:00:00+3'::timestamptz)]::ORDER_STATUS[],
        'iiko_1',
        NULL, NULL, NULL, 'a1s2d3f4_email'
    ),
    (
        '02', '02', NULL, 'restaurant01', 1, 50, ('PENDING', 'INIT', '2020-04-04 20:00:00+3'::timestamptz, '2020-04-04 20:00:00+3'::timestamptz), 200, NULL, 20, 'RUB',
        ARRAY[]::ORDER_ITEM[],
        ARRAY[]::ORDER_CHANGE_EVENT[],
        NULL,
        'iiko_2',
        NULL, NULL, NULL, NULL
    ),
    (
        '03', '03', NULL, 'restaurant01', 1, 50, ('PAYMENT_CONFIRMED', 'CLEARED', '2020-04-04 20:00:00+3'::timestamptz, '2020-04-04 20:00:00+3'::timestamptz), 200, NULL, 20, 'RUB',
        ARRAY[]::ORDER_ITEM[],
        ARRAY[]::ORDER_CHANGE_EVENT[],
        NULL,
        'iiko_3',
        'card', 'card-x523dcaee05744ea75a8eeda7', '4041153212', NULL
    );

INSERT INTO iiko_integration.receipts
    (document_id, order_version, order_id, type, sum, url)
VALUES
    ('document_1', 1, '01', 'payment', 300, 'https://taxi-iiko-integration.s3.yandex.net/document_1'),
    ('document_2', 2, '01', 'refund',  50,  'https://taxi-iiko-integration.s3.yandex.net/document_2'),
    ('document_3', 3, '01', 'refund',  80,  'https://taxi-iiko-integration.s3.yandex.net/document_3');
