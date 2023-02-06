INSERT INTO iiko_integration.orders
    (id, restaurant_order_id, version, invoice_id,  yandex_uid, idempotency_token, restaurant_id, expected_cashback_percentage, status, total_price, complement_amount, discount, currency, items, changelog, status_history)
VALUES
    ('order_pending',           '123', 1, NULL,                         NULL,   '01', 'restaurant01', 0, ('PENDING','INIT',now(),now()),                           100, NULL, 0, 'RUB', ARRAY[('01', NULL, 'Hamburger', 3, 50, 150, 150, 0, 0, 30, 20, 1, NULL)]::ORDER_ITEM[],  ARRAY[]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_STATUS[]),
    ('order_canceled',          '123', 1, 'invoice_canceled',           'uid',  '02', 'restaurant01', 0, ('CANCELED','INIT',now(),now()),            100, NULL, 0, 'RUB', ARRAY[('01', NULL, 'Hamburger', 3, 50, 150, 150, 0, 0, 30, 20, 1, NULL)]::ORDER_ITEM[],  ARRAY[]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_STATUS[]),
    ('order_closed',            '123', 1, 'invoice_closed',             'uid',  '03', 'restaurant01', 0, ('CLOSED','INIT',now(),now()),              100, NULL, 0, 'RUB', ARRAY[('01', NULL, 'Hamburger', 3, 50, 150, 150, 0, 0, 30, 20, 1, NULL)]::ORDER_ITEM[],  ARRAY[]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_STATUS[]),
    ('order_holding',           '123', 1, 'invoice_holding',            'uid',  '04', 'restaurant01', 0, ('PENDING','HOLDING',now(),now()),                           100, NULL, 0, 'RUB', ARRAY[('01', NULL, 'Hamburger', 3, 50, 150, 150, 0, 0, 30, 20, 1, NULL)]::ORDER_ITEM[],  ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_STATUS[]),
    ('order_held_and_waiting',  '123', 1, 'invoice_held_and_waiting',   'uid',  '05', 'restaurant01', 0, ('WAITING_FOR_CONFIRMATION','HELD',now(),now()), 100, NULL, 0, 'RUB', ARRAY[('01', NULL, 'Hamburger', 3, 50, 150, 150, 0, 0, 30, 20, 1, NULL)]::ORDER_ITEM[],  ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'done', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_STATUS[]),
    ('order_held_and_confirmed','123', 1, 'invoice_held_and_confirmed', 'uid',  '06', 'restaurant01', 0, ('PAYMENT_CONFIRMED','HELD',now(),now()),                100, NULL, 0, 'RUB', ARRAY[('01', NULL, 'Hamburger', 3, 50, 150, 150, 0, 0, 30, 20, 1, NULL)]::ORDER_ITEM[],  ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'done', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_STATUS[]),
    ('order_hold_failed',       '123', 1, 'invoice_hold_failed',        'uid',  '07', 'restaurant01', 0, ('PENDING','HOLD_FAILED',now(),now()),                      100, NULL, 0, 'RUB', ARRAY[('01', NULL, 'Hamburger', 3, 50, 150, 150, 0, 0, 30, 20, 1, NULL)]::ORDER_ITEM[],  ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'done', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_STATUS[]),
    ('order_clearing',          '123', 1, 'invoice_clearing',           'uid',  '08', 'restaurant01', 0, ('PAYMENT_CONFIRMED','CLEARING',now(),now()),                          100, NULL, 0, 'RUB', ARRAY[('01', NULL, 'Hamburger', 3, 50, 150, 150, 0, 0, 30, 20, 1, NULL)]::ORDER_ITEM[],  ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'done', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_STATUS[]),
    ('order_cleared',           '123', 1, 'invoice_cleared',            'uid',  '09', 'restaurant01', 0, ('PAYMENT_CONFIRMED','CLEARED',now(),now()),                           100, NULL, 0, 'RUB', ARRAY[('01', NULL, 'Hamburger', 3, 50, 150, 150, 0, 0, 30, 20, 1, NULL)]::ORDER_ITEM[],  ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'done', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_STATUS[]),
    ('order_refunding',         '123', 1, 'invoice_refunding',          'uid',  '10', 'restaurant01', 0, ('PAYMENT_CONFIRMED','REFUNDING',now(),now()),                         100, NULL, 0, 'RUB', ARRAY[('01', NULL, 'Hamburger', 3, 50, 150, 150, 0, 0, 30, 20, 1, NULL)]::ORDER_ITEM[],  ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'done', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_STATUS[]),


    (
        'order_4items_cleared',    '123', 1, 'invoice_4items_cleared',     'uid',  '11', 'restaurant01', 0, ('PAYMENT_CONFIRMED','CLEARED',now(),now()),
        300, NULL, 20, 'RUB',
        --  prd_id, prnt_id, name,       quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
        ARRAY[
            ('01', NULL, 'Hamburger',       3,      50,     150,    150,        0,  0,      25, 20,     1,      NULL),
            ('02', NULL, 'Cola',            0.5,    250,    125,    100,        25, 20,     0,  0,      2,      NULL),
            ('03', NULL, 'French_fries',    0.5,    100,    50,     50,         0,  0,      0,  0,      3,      NULL),
            ('04', NULL, 'Air',             1,      0,      0,      0,          0,  0,      0,  0,      4,      NULL)
        ]::ORDER_ITEM[],
        ARRAY[
            (
                'charge', 1,
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,        0,  0,      25, 20,     1,      NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,        25, 20,     0,  0,      2,      NULL),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,         0,  0,      0,  0,      3,      NULL),
                    ('04', NULL, 'Air',             1,      0,      0,      0,          0,  0,      0,  0,      4,      NULL)
                ]::ORDER_ITEM[],
                300,
                'done',
                NOW(),
                NOW(),
                'operation_id',
                NULL,
                NULL
            )
        ]::ORDER_CHANGE_EVENT[],
        ARRAY[]::ORDER_STATUS[]
    ),
    (
        'order_4items_cleared_composite',    '123', 1, 'invoice_4items_cleared_composite',     'uid',  '12', 'restaurant01', 0, ('PAYMENT_CONFIRMED','CLEARED',now(),now()),
        300, 199, 20, 'RUB',
        --  prd_id, prnt_id, name,       quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
        ARRAY[
            ('01', NULL, 'Hamburger',       3,      50,     150,    150,        0,  0,      25, 20,     1,      149),
            ('02', NULL, 'Cola',            0.5,    250,    125,    100,        25, 20,     0,  0,      2,      50),
            ('03', NULL, 'French_fries',    0.5,    100,    50,     50,         0,  0,      0,  0,      3,      0),
            ('04', NULL, 'Air',             1,      0,      0,      0,          0,  0,      0,  0,      4,      0)
        ]::ORDER_ITEM[],
        ARRAY[
            (
                'charge', 1,
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,        0,  0,      25, 20,     1,      149),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,        25, 20,     0,  0,      2,      50),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,         0,  0,      0,  0,      3,      0),
                    ('04', NULL, 'Air',             1,      0,      0,      0,          0,  0,      0,  0,      4,      0)
                ]::ORDER_ITEM[],
                300,
                'done',
                NOW(),
                NOW(),
                'operation_id',
                NULL,
                199
            )
        ]::ORDER_CHANGE_EVENT[],
        ARRAY[]::ORDER_STATUS[]
    ),
    (
        'order_4items_refunding',    '123', 2, 'invoice_4items_refunding',     'uid',  '13', 'restaurant01', 0, ('PAYMENT_CONFIRMED','REFUNDING',now(),now()),
        300, NULL, 20, 'RUB',
        --  prd_id, prnt_id, name,       quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
        ARRAY[
            ('01', NULL, 'Hamburger',       3,      50,     150,    150,        0,  0,      25, 20,     1,      NULL),
            ('02', NULL, 'Cola',            0.1,    250,    25.0,   20.0,       5.0, 20,    0, 0,       2,      NULL),
            ('03', NULL, 'French_fries',    0.5,    100,    50,     50,         0,  0,      0,  0,      3,      NULL),
            ('04', NULL, 'Air',             1,      0,      0,      0,          0,  0,      0,  0,      4,      NULL)
        ]::ORDER_ITEM[],
        ARRAY[
            (
                'charge', 1,
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,    0,  0,  25, 20, 1, NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,    25, 20, 0, 0, 2, NULL),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,     0,  0,  0,  0, 3, NULL),
                    ('04', NULL, 'Air',             1,      0,      0,      0,      0,  0,  0,  0,  4, NULL)
                ]::ORDER_ITEM[],
                300,
                'done',
                NOW(),
                NOW(),
                'operation_id',
                NULL,
                NULL
            ),
            (
                'refund', 2,
                ARRAY[
                        ('01', NULL, 'Hamburger',       3,      50,     150,    150,    0,  0,  25, 20, 1, NULL),
                        ('02', NULL, 'Cola',            0.1,    250,    25.0,   20.0,   5.0, 20, 0, 0, 2, NULL),
                        ('03', NULL, 'French_fries',    0.5,    100,    50,     50,     0,  0,  0,  0, 3, NULL),
                        ('04', NULL, 'Air',             1,      0,      0,      0,      0,  0,  0,  0,  4, NULL)
                ]::ORDER_ITEM[],
                220,
                'pending',
                NOW(),
                NOW(),
                'operation_id',
                NULL,
                NULL
            )
        ]::ORDER_CHANGE_EVENT[],
        ARRAY[]::ORDER_STATUS[]
    ),
    (
        'order_bad_items_cleared',    '123', 1, 'invoice_bad_items_cleared',     'uid',  '14', 'restaurant01', 0, ('PAYMENT_CONFIRMED','CLEARED',now(),now()),
        350, NULL, 20, 'RUB',
        ARRAY[
            ('01', NULL, 'Hamburger',       3,      50,     150,    150,    0,  0,  25, 20, 1, NULL),
            ('02', NULL, 'Cola',            0.5,    351,    125,    100,    25, 20, 0, 0, 2, NULL),
            ('03', NULL, 'French_fries',    0.5,    100,    50,     50,     0,  0,  0,  0, 3, NULL),
            ('04', NULL, 'Air',             1,      0,      0,      0,      0,  0,  0,  0,  4, NULL)
        ]::ORDER_ITEM[],       
        ARRAY[
            (
                'charge', 1,
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,    0,  0,  25, 20, 1, NULL),
                    ('02', NULL, 'Cola',            0.5,    351,    125,    100,    25, 20, 0, 0, 2, NULL),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,     0,  0,  0,  0, 3, NULL),
                    ('04', NULL, 'Air',             1,      0,      0,      0,      0,  0,  0,  0,  4, NULL)
                ]::ORDER_ITEM[],
                300,
                'done',
                NOW(),
                NOW(),
                'operation_id',
                NULL,
                NULL
            )
        ]::ORDER_CHANGE_EVENT[],
        ARRAY[]::ORDER_STATUS[]
    )
;
