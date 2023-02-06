INSERT INTO iiko_integration.orders
    (id,  status, invoice_id, restaurant_order_id, user_id, yandex_uid, locale, idempotency_token, restaurant_id, expected_cashback_percentage, total_price, discount, currency, changelog ,items, status_history)
VALUES
    ('01',     ('PENDING', 'INIT', now(), now()),                   'eda_01',   'iiko_01',          NULL,            NULL,            NULL,   '01', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING','INIT', now(), now())]::ORDER_STATUS[]),
    ('03',     ('CANCELED', 'INIT', now(), now()),                  'eda_03',   'iiko_03',          NULL,            NULL,            NULL,   '03', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('CANCELED', 'INIT', now(), now())]::ORDER_STATUS[]),
    ('04',     ('CLOSED', 'INIT', now(), now()),                    'eda_04',   'iiko_04',          NULL,            NULL,            NULL,   '04', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('CLOSED', 'INIT', now(), now())]::ORDER_STATUS[]),
    ('05',     ('PENDING', 'HOLDING', now(), now()),                'eda_05',   'iiko_05',          NULL,            NULL,            NULL,   '05', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING','HOLDING', now(), now())]::ORDER_STATUS[]),
    ('05.1',   ('CLOSED', 'HOLDING', now(), now()),                 'eda_05.1', 'iiko_05.1',        NULL,            NULL,            NULL,   '051','restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING','HOLDING', now(), now())]::ORDER_STATUS[]),
    ('05.2',   ('CANCELED', 'HOLDING', now(), now()),               'eda_05.2', 'iiko_05.2',        NULL,            NULL,            NULL,   '052','restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING','HOLDING', now(), now())]::ORDER_STATUS[]),
    ('06',     ('WAITING_FOR_CONFIRMATION', 'HELD', now(), now()),  'eda_06',   'iiko_06',          NULL,            NULL,            NULL,   '06', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('WAITING_FOR_CONFIRMATION', 'HELD', now(), now())]::ORDER_STATUS[]),
    ('07',     ('PAYMENT_CONFIRMED', 'HELD', now(), now()),         'eda_07',   'iiko_07',          NULL,            NULL,            NULL,   '07', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PAYMENT_CONFIRMED', 'HELD', now(), now())]::ORDER_STATUS[]),
    ('07.1',   ('CLOSED', 'HELD', now(), now()),                    'eda_07.1', 'iiko_07.1',        NULL,            NULL,            NULL,   '071','restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PAYMENT_CONFIRMED', 'HELD', now(), now())]::ORDER_STATUS[]),
    ('07.2',   ('CANCELED', 'HELD', now(), now()),                  'eda_07.2', 'iiko_07.2',        NULL,            NULL,            NULL,   '072','restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PAYMENT_CONFIRMED', 'HELD', now(), now())]::ORDER_STATUS[]),
    ('08',     ('PENDING', 'HOLD_FAILED', now(), now()),            'eda_08',   'iiko_08',          NULL,            NULL,            NULL,   '08', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING', 'HOLD_FAILED', now(), now())]::ORDER_STATUS[]),
    ('08.1',   ('CLOSED', 'HOLD_FAILED', now(), now()),             'eda_08.1', 'iiko_08.1',        NULL,            NULL,            NULL,   '081','restaurant01', 0,        100, 0, 'RUB', ARRAY[]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING', 'HOLD_FAILED', now(), now())]::ORDER_STATUS[]),
    ('08.2',   ('CANCELED', 'HOLD_FAILED', now(), now()),           'eda_08.2', 'iiko_08.2',        NULL,            NULL,            NULL,   '082','restaurant01', 0,        100, 0, 'RUB', ARRAY[]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING', 'HOLD_FAILED', now(), now())]::ORDER_STATUS[]),
    ('09',     ('PAYMENT_CONFIRMED', 'CLEARING', now(), now()),     'eda_09',   'iiko_09',          NULL,            NULL,            NULL,   '09', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PAYMENT_CONFIRMED', 'CLEARING', now(), now())]::ORDER_STATUS[]),
    ('09.1',   ('CLOSED', 'CLEARING', now(), now()),                'eda_09.1', 'iiko_09.1',        NULL,            NULL,            NULL,   '091','restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PAYMENT_CONFIRMED', 'CLEARING', now(), now())]::ORDER_STATUS[]),
    ('09.2',   ('CANCELED', 'CLEARING', now(), now()),              'eda_09.2', 'iiko_09.2',        NULL,            NULL,            NULL,   '092','restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PAYMENT_CONFIRMED', 'CLEARING', now(), now())]::ORDER_STATUS[]),
    ('10',     ('PAYMENT_CONFIRMED', 'CLEARED', now(), now()),      'eda_10',   'iiko_10',          NULL,            NULL,            NULL,   '10', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PAYMENT_CONFIRMED', 'CLEARED', now(), now())]::ORDER_STATUS[]),
    ('10.1',   ('CLOSED', 'CLEARED', now(), now()),                 'eda_10.1', 'iiko_10.1',        NULL,            NULL,            NULL,   '101','restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PAYMENT_CONFIRMED', 'CLEARED', now(), now())]::ORDER_STATUS[]),
    ('10.2',   ('CANCELED', 'CLEARED', now(), now()),               'eda_10.2', 'iiko_10.2',        NULL,            NULL,            NULL,   '102','restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PAYMENT_CONFIRMED', 'CLEARED', now(), now())]::ORDER_STATUS[]),
    ('42',     ('PAYMENT_CONFIRMED', 'REFUNDING', now(), now()),    'eda_42',   'iiko_42',          NULL,            NULL,            NULL,   '42', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL), ('refund',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PAYMENT_CONFIRMED', 'REFUNDING', now(), now())]::ORDER_STATUS[]),

    ('11',   ('PENDING', 'INIT', now(), now()),                     NULL,   'iiko_11', 'old_user_11', 'old_yandex_11', 'old_locale_11',   '11', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING', 'INIT', now(), now())]::ORDER_STATUS[]),
    ('11.1', ('PENDING', 'HOLDING', now(), now()),                  'eda_11.1', 'iiko_11.1', 'old_user_11', 'old_yandex_11', 'old_locale_11', '11.1', 'restaurant01', 0,      100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING', 'HOLDING', now(), now())]::ORDER_STATUS[]),
    ('21.1', ('PENDING', 'HOLDING', now(), now()),                  'eda_21.1', 'iiko_21.1',          NULL,            NULL,            NULL, '21.1', 'restaurant01', 0,      100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING', 'HOLDING', now(), now())]::ORDER_STATUS[]),
    ('12',   ('CANCELED', 'INIT', now(), now()),                    NULL,   'iiko_12', 'old_user_12', 'old_yandex_12', 'old_locale_12',   '12', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('CANCELED', 'INIT', now(), now())]::ORDER_STATUS[]),
    ('13',   ('PENDING', 'HOLDING', now(), now()),                  'eda_13',   'iiko_13',     'user_13',            NULL,            NULL,   '13', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING', 'HOLDING', now(), now())]::ORDER_STATUS[]),
    ('14',   ('PENDING', 'HOLDING', now(), now()),                  'eda_14',   'iiko_14',     'user_14',            NULL,            'ru',   '14', 'restaurant01', 0,        100, 0, 'RUB', ARRAY[('charge',1, ARRAY[]::ORDER_ITEM[], 100, 'processing', now(), now(), '1', NULL, NULL)]::ORDER_CHANGE_EVENT[], ARRAY[]::ORDER_ITEM[], ARRAY[('PENDING', 'HOLDING', now(), now())]::ORDER_STATUS[]),

    (
        '21',   ('PENDING', 'INIT', now(), now()),                     NULL,       'iiko_21',          NULL,            NULL,            NULL,   '21', 'restaurant01', 0,
        300, 25, 'RUB',
        ARRAY[]::ORDER_CHANGE_EVENT[],
        --  prd_id, prnt_id, name,     quanty, per_unit, wth_dsc, for_cstm, dsc, dsc_%, vat, vat_%, itm_id, complements
        ARRAY[
            ('01', NULL, 'Hamburger',       3,      50,     150,    150,    0,  0,      25, 20,     1,     NULL),
            ('02', NULL, 'Cola',            0.5,    250,    125,    100,    25, 20,     0,  0,      2,     NULL),
            ('03', NULL, 'French_fries',    0.5,    100,    50,     50,     0,  0,      0,  0,      3,     NULL)
        ]::ORDER_ITEM[],
        ARRAY[('PENDING', 'INIT', now(), now())]::ORDER_STATUS[]
    )
;