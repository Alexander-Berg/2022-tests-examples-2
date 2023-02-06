INSERT INTO iiko_integration.orders
    (
        invoice_id, 
        restaurant_order_id,
        yandex_uid, 
        total_price,
        complement_amount,
        discount,
        version,
        payment_method_type,
        payment_method_id,
        items,
        changelog,        
        id, idempotency_token, status, restaurant_id, expected_cashback_percentage,  currency)
VALUES
    ( 
        'invoice_charge', -- invoice_id
        'restaurant_charge', -- restaurant_order_id
        '123456789',
        250,            -- total_price
        NULL,           -- complement_amount
        25,             -- discount
        2,              -- version
        'card',
        'card-123',
        --      prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
        ARRAY[
                ('01',  NULL,   'Hamburger',       2,      50,     150,     100,     0,     0,   30,   20,   1,     NULL),
                ('02',  NULL,   'Cola',            0.5,    250,    125,     100,     25,    20,  10,   10,   2,     NULL),
                ('03',  NULL,   'French fries',    0,      100,    0,       0,       0,     0,   0,    10,   3,     NULL),
                ('04',  NULL,   'Air',             1,      0,      0,       0,       0,     0,   0,    0,    4,     NULL)
        ]::ORDER_ITEM[],
        ARRAY[
            (
                'charge', 1,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,     0,     0,   25,   20,   1,     NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,     25,    20,  10,   10,   2,     NULL),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,      0,     0,   0,    0,    3,     NULL),
                    ('04', NULL, 'Air',             1,      0,      0,      0,       0,     0,   0,    0,    4,     NULL)
                ]::ORDER_ITEM[],
                300, -- amount_difference
                'processing', -- status
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                'charge_1',
                NULL, -- admin info
                NULL
            ),
            (
                'refund', 2,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       2,      50,     150,     100,     0,     0,   30,   20,   1,    NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,     100,     25,    20,  10,   10,   2,    NULL),
                    ('03', NULL, 'French fries',    0,      100,    0,       0,       0,     0,   0,    10,   3,    NULL),
                    ('04', NULL, 'Air',             1,      0,      0,       0,       0,     0,   0,    0,    4,    NULL)
                 ]::ORDER_ITEM[],
                -50,
                'pending',
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                NULL,
                ('TAXITICKET-1', 'startrack', 'reason_code', 'operator_logn'),
                NULL
            )
        ]::ORDER_CHANGE_EVENT[],
        '01', '01', ('PAYMENT_CONFIRMED','CLEARED','2020-08-20 20:00:00+0'::timestamptz,'2020-08-20 20:00:00+0'::timestamptz), 'restaurant01', 0, 'RUB'
    ),
    ( 
        'invoice_refund', -- invoice_id
        'restaurant_refund', -- restaurant_order_id
        '123456789',
        250,                -- total_price
        NULL,               -- complement_amount
        0,                  -- discount
        2,                  -- version
        'card',
        'card-123',
       ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,     0,     0,   25,   20,   1,     NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,     25,    20,  10,   10,   2,     NULL),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,      0,     0,   0,    0,    3,     NULL),
                    ('04', NULL, 'Air',             1,      0,      0,      0,       0,     0,   0,    0,    4,     NULL)
        ]::ORDER_ITEM[],
        ARRAY[
            (
                'charge', 1,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,     0,     0,   25,   20,   1,     NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,     25,    20,  10,   10,   2,     NULL),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,      0,     0,   0,    0,    3,     NULL),
                    ('04', NULL, 'Air',             1,      0,      0,      0,       0,     0,   0,    0,    4,     NULL)
                ]::ORDER_ITEM[],
                300, -- amount_difference
                'done', -- status
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                'charge_1',
                NULL, -- admin info
                NULL
            ),
            (
                'refund', 2,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       2,      50,     100,     100,     0,     0,   25,   20,   1,    NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,     100,     25,    20,  10,   10,   2,    NULL),
                    ('03', NULL, 'French fries',    0,      100,    0,       0,       0,     0,   0,    0,   3,    NULL),
                    ('04', NULL, 'Air',             1,      0,      0,       0,       0,     0,   0,    0,    4,    NULL)
                 ]::ORDER_ITEM[],
                -50,
                'processing',
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                'refund_2',
                ('TAXITICKET-1', 'startrack', 'reason_code', 'operator_logn'),
                NULL
            )
        ]::ORDER_CHANGE_EVENT[],
        '02', '02', ('PAYMENT_CONFIRMED','REFUNDING','2020-08-20 20:00:00+0'::timestamptz,'2020-08-20 20:00:00+0'::timestamptz), 'restaurant01', 0, 'RUB'
    ),
    (
        'invoice_charge_complement', -- invoice_id
        'restaurant_charge_complement', -- restaurant_order_id
        '123456789',
        250,            -- total_price
        149,            -- complement_amount
        25,             -- discount
        2,              -- version
        'card',
        'card-123',
        --      prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
        ARRAY[
                ('01',  NULL,   'Hamburger',       2,      50,     150,     100,     0,     0,   30,   20,   1,     99),
                ('02',  NULL,   'Cola',            0.5,    250,    125,     100,     25,    20,  10,   10,   2,     50),
                ('03',  NULL,   'French fries',    0,      100,    0,       0,       0,     0,   0,    10,   3,     0),
                ('04',  NULL,   'Air',             1,      0,      0,       0,       0,     0,   0,    0,    4,     0)
        ]::ORDER_ITEM[],
        ARRAY[
            (
                'charge', 1,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,     0,     0,   25,   20,   1,     149),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,     25,    20,  10,   10,   2,     50),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,      0,     0,   0,    0,    3,     0),
                    ('04', NULL, 'Air',             1,      0,      0,      0,       0,     0,   0,    0,    4,     0)
                ]::ORDER_ITEM[],
                300, -- amount_difference
                'processing', -- status
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                'charge_1',
                NULL, -- admin info
                199
            ),
            (
                'refund', 2,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       2,      50,     150,     100,     0,     0,   30,   20,   1,    99),
                    ('02', NULL, 'Cola',            0.5,    250,    125,     100,     25,    20,  10,   10,   2,    50),
                    ('03', NULL, 'French fries',    0,      100,    0,       0,       0,     0,   0,    10,   3,    0),
                    ('04', NULL, 'Air',             1,      0,      0,       0,       0,     0,   0,    0,    4,    0)
                 ]::ORDER_ITEM[],
                -50,
                'pending',
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                NULL,
                ('TAXITICKET-1', 'startrack', 'reason_code', 'operator_logn'),
                -50
            )
        ]::ORDER_CHANGE_EVENT[],
        '01.1', '01.1', ('PAYMENT_CONFIRMED','CLEARED','2020-08-20 20:00:00+0'::timestamptz,'2020-08-20 20:00:00+0'::timestamptz), 'restaurant01', 0, 'RUB'
    ),
    (
        'invoice_refund_complement', -- invoice_id
        'restaurant_refund_complement', -- restaurant_order_id
        '123456789',
        250,                -- total_price
        149,                -- complement_amount
        0,                  -- discount
        2,                  -- version
        'card',
        'card-123',
       ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,     0,     0,   25,   20,   1,     99),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,     25,    20,  10,   10,   2,     50),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,      0,     0,   0,    0,    3,     0),
                    ('04', NULL, 'Air',             1,      0,      0,      0,       0,     0,   0,    0,    4,     0)
        ]::ORDER_ITEM[],
        ARRAY[
            (
                'charge', 1,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,     0,     0,   25,   20,   1,     149),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,     25,    20,  10,   10,   2,     50),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,      0,     0,   0,    0,    3,     0),
                    ('04', NULL, 'Air',             1,      0,      0,      0,       0,     0,   0,    0,    4,     0)
                ]::ORDER_ITEM[],
                300, -- amount_difference
                'done', -- status
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                'charge_1',
                NULL, -- admin info
                199
            ),
            (
                'refund', 2,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       2,      50,     150,     100,     0,     0,   30,   20,   1,    99),
                    ('02', NULL, 'Cola',            0.5,    250,    125,     100,     25,    20,  10,   10,   2,    50),
                    ('03', NULL, 'French fries',    0,      100,    0,       0,       0,     0,   0,    10,   3,    0),
                    ('04', NULL, 'Air',             1,      0,      0,       0,       0,     0,   0,    0,    4,    0)
                 ]::ORDER_ITEM[],
                -50,
                'processing',
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                'refund_2',
                ('TAXITICKET-1', 'startrack', 'reason_code', 'operator_logn'),
                -50
            )
        ]::ORDER_CHANGE_EVENT[],
        '02.1', '02.1', ('PAYMENT_CONFIRMED','REFUNDING','2020-08-20 20:00:00+0'::timestamptz,'2020-08-20 20:00:00+0'::timestamptz), 'restaurant01', 0, 'RUB'
    ),
    ( 
        'invoice_refunded', -- invoice_id
        'restaurant_refunded', -- restaurant_order_id
        '123456789',
        250,                -- total_price
        NULL,               -- complement_amount
        0,                  -- discount
        2,                  -- version
        'card',
        'card-123',
       ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,     0,     0,   25,   20,   1,     NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,     25,    20,  10,   10,   2,     NULL),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,      0,     0,   0,    0,    3,     NULL),
                    ('04', NULL, 'Air',             1,      0,      0,      0,       0,     0,   0,    0,    4,     NULL)
        ]::ORDER_ITEM[],
        ARRAY[
            (
                'charge', 1,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       3,      50,     150,    150,     0,     0,   25,   20,   1,     NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,    100,     25,    20,  10,   10,   2,     NULL),
                    ('03', NULL, 'French_fries',    0.5,    100,    50,     50,      0,     0,   0,    0,    3,     NULL),
                    ('04', NULL, 'Air',             1,      0,      0,      0,       0,     0,   0,    0,    4,     NULL)
                ]::ORDER_ITEM[],
                300, -- amount_difference
                'done', -- status
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                'charge_1',
                NULL, -- admin info
                NULL -- complement_difference
            ),
            (
                'refund', 2,
            --  prd_id, prnt_id, name,          quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complement_amount
                ARRAY[
                    ('01', NULL, 'Hamburger',       2,      50,     150,     100,     0,     0,   30,   20,   1,    NULL),
                    ('02', NULL, 'Cola',            0.5,    250,    125,     100,     25,    20,  10,   10,   2,    NULL),
                    ('03', NULL, 'French fries',    0,      100,    0,       0,       0,     0,   0,    10,   3,    NULL),
                    ('04', NULL, 'Air',             1,      0,      0,       0,       0,     0,   0,    0,    4,    NULL)
                 ]::ORDER_ITEM[],
                -50,
                'done',
                '2020-04-04 20:00:00'::timestamptz,
                '2020-04-04 20:00:00'::timestamptz,
                'refund_2',
                ('TAXITICKET-1', 'startrack', 'reason_code', 'operator_logn'),
                NULL
            )
        ]::ORDER_CHANGE_EVENT[],        
        '03', '03', ('PAYMENT_CONFIRMED','CLEARED','2020-08-20 20:00:00+0'::timestamptz,'2020-08-20 20:00:00+0'::timestamptz), 'restaurant01', 0, 'RUB'
    )
;
