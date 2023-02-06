INSERT INTO receipts
    (id, park_id, driver_id, receipt_type, inn, status, total, is_corp,
     receipt_at, receipt_at_tstz, checkout_at, checkout_at_tstz, created_at, modified_at, fns_id, fns_url)
VALUES ('order1', 'p1', 'd1', 'order', 'inn1', 'new', 1.1, false,
        '2020-01-02 00:00', '2020-01-02 00:00 +03', NOW(), NOW(), NOW(), NOW(), NULL, NULL),
       ('order2', 'p1', 'd1', 'order', 'inn1', 'new', 1.2, false,
        '2020-01-01 00:00', '2020-01-02 00:00 +03', NOW(), NOW(), NOW(), NOW(), NULL, NULL);
