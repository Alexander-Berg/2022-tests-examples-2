INSERT INTO receipts
    (id, park_id, driver_id, receipt_type, inn, status, total, is_corp,
     receipt_at, receipt_at_tstz, checkout_at, checkout_at_tstz, created_at, modified_at, fns_id, fns_url)
VALUES  ('order1', 'p1', 'd1', 'order', 'inn1', 'new', 1.1, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order2', 'p1', 'd1', 'order', 'inn1', 'new', 1.2, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),

        ('subv1', 'p1', 'd1', 'subvention', 'inn1', 'new', 1.3, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('subv2', 'p1', 'd1', 'subvention', 'inn1', 'new', 1.40243, true,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),

        ('order3', 'p1', 'd1', 'order', 'inn1', 'new', 1.5125, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order4', 'p1', 'd1', 'order', 'inn1', 'new', 1.6125, true,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order5', 'p1', 'd1', 'INVALID', 'inn1', 'new', 1.9, true,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),

        ('order_old', 'p1', 'd1', 'order', 'inn1', 'processed', 1.7, true,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt', 'tt//link'),

        ('order_negative', 'p1', 'd1', 'order', 'inn1', 'new', -2, true,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),

        ('order_failed_1', 'p2', 'd2', 'order', 'inn2', 'new', 1.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order_failed_2', 'p3', 'd3', 'order', 'inn3', 'new', 1.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order_failed_3', 'p4', 'd4', 'order', 'inn4', 'new', 1.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order_failed_4', 'p5', 'd5', 'order', 'inn5', 'new', 1.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order_failed_5', 'p7', 'd7', 'order', 'inn7', 'new', 1.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order_failed_6', 'p8', 'd8', 'order', 'inn8', 'new', 1.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order_duplicate_1', 'p6', 'd6', 'order', 'inn_d1', 'new', 1.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order_duplicate_2', 'p6', 'd6', 'order', 'inn_d2', 'new', 1.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order_duplicate_3', 'p6', 'd6', 'order', 'inn_d3', 'new', 1.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('order_duplicate_4', 'p6', 'd6', 'order', 'inn_d4', 'new', 1.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),

        ('order_income_excess', 'p9', 'd9', 'order', 'inn9', 'new', 1.2, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL);
