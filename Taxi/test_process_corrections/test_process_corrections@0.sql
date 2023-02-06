INSERT INTO receipts
    (id, park_id, driver_id, receipt_type, inn, status, total, is_corp,
     receipt_at, receipt_at_tstz, checkout_at, checkout_at_tstz, created_at, modified_at, fns_id, fns_url)
VALUES  ('subv_processed_1_1', 'p1', 'd1', 'subvention', 'inn1', 'processed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt1', 'tt//link'),
        ('subv_processed_1_2', 'p1', 'd1', 'subvention', 'inn1', 'processed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt2', 'tt//link'),
        ('subv_processed_1_3', 'p1', 'd1', 'subvention', 'inn1', 'processed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt3', 'tt//link'),
        ('subv_processed_1_4', 'p1', 'd1', 'subvention', 'inn1', 'processed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt4', 'tt//link'),

        ('subv_processed_2', 'p2', 'd2', 'subvention', 'inn2', 'processed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt', 'tt//link'),
        ('subv_processed_3', 'p3', 'd3', 'subvention', 'inn3', 'processed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt', 'tt//link'),
        ('subv_processed_4', 'p4', 'd4', 'subvention', 'inn4', 'processed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt', 'tt//link'),
        ('subv_processed_5', 'p5', 'd5', 'subvention', 'inn5', 'processed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt', 'tt//link'),
        ('subv_processed_7', 'p7', 'd7', 'subvention', 'inn7', 'processed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt', 'tt//link'),
        ('subv_processed_8', 'p8', 'd8', 'subvention', 'inn8', 'processed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt', 'tt//link'),

        ('subv_failed_1', 'p1', 'd1', 'subvention', 'inn1', 'failed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('subv_failed_wont_fix_1', 'p1', 'd1', 'subvention', 'inn1', 'failed_wont_fix', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('subv_missing_inn_1', 'p1', 'd1', 'subvention', 'inn1', 'missing_inn', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('subv_delayed_1', 'p1', 'd1', 'subvention', 'inn1', 'delayed', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('subv_new_1', 'p1', 'd1', 'subvention', 'inn1', 'new', 2.6, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),

        -- testing behaviour for cancelled and dismissed subventions
        ('subv_cancelled_1', 'p1', 'd1', 'subvention', 'inn1', 'cancelled', 2.5, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt', 'tt//link'),
        ('subv_cancelled_2', 'p1', 'd1', 'subvention', 'inn1', 'cancelled', 2.6, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt', 'tt//link'),
        ('subv_cancelled_2_new', 'p1', 'd1', 'subvention', 'inn1', 'new', 3.6, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt', 'tt//link'),
        ('subv_cancelled_3', 'p1', 'd1', 'subvention', 'inn1', 'cancelled', 2.65, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), 'tt', 'tt//link'),
        ('subv_dismissed_1', 'p1', 'd1', 'subvention', 'inn1', 'dismissed', 2.7, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('subv_dismissed_2', 'p1', 'd1', 'subvention', 'inn1', 'dismissed', 2.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('subv_dismissed_2_new', 'p1', 'd1', 'subvention', 'inn1', 'new', 3.8, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('subv_dismissed_3', 'p1', 'd1', 'subvention', 'inn1', 'dismissed', 2.85, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL),
        ('outdated_1', 'p1', 'd1', 'subvention', 'inn1', 'outdated', 2.85, false,
        NOW(), NOW(), NOW(), NOW(), NOW(), NOW(), NULL, NULL);


INSERT INTO corrections
        (reverse_id, new_id, park_id, driver_id, status, total,
        receipt_at, receipt_at_tstz, checkout_at, checkout_at_tstz, created_at, modified_at)
VALUES
        -- reverted
        ('subv_processed_1_1', 'subv_processed_1_1_new', 'p1', 'd1', 'new', 3.0, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_1_2', NULL, 'p1', 'd1', 'new', 0.0, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_1_3', 'subv_processed_1_3_new', 'p1', 'd1', 'delayed', 3.1, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_1_4', NULL, 'p1', 'd1', 'delayed', 0.0, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),

        -- delayed trying to cancel
        ('subv_processed_2', 'subv_processed_2_delayed', 'p2', 'd2', 'new', 3.2, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_3', 'subv_processed_3_delayed', 'p3', 'd3', 'new', 3.3, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_7', 'subv_processed_7_delayed', 'p7', 'd7', 'new', 3.7, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_8', 'subv_processed_8_delayed', 'p8', 'd8', 'new', 3.8, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),

        -- failed trying to cancel
        ('subv_processed_4', 'subv_processed_4_failed', 'p4', 'd4', 'new', 3.4, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_5', 'subv_processed_5_failed', 'p5', 'd5', 'new', 3.5, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_6', 'subv_processed_6_failed', 'p6', 'd6', 'new', 3.6, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),

        -- failed before cancel
        ('subv_failed_1', 'subv_failed_1_new', 'p1', 'd1', 'new', 4.0, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_failed_wont_fix_1', 'subv_failed_wont_fix_1_new', 'p1', 'd1', 'new', 4.1, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_missing_inn_1', 'subv_missing_inn_1_new', 'p1', 'd1', 'new', 4.2, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),

        -- ignored because not processed by fns yet
        ('subv_new_1', 'subv_corr_14', 'p1', 'd1', 'new', 4.4, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        -- must become delayed because fns processing delayed
        ('subv_delayed_1', 'subv_corr_13', 'p1', 'd1', 'new', 4.3, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),

        -- ignored because already corrected
        ('subv_ignored_1', 'subv_corr_15', 'p1', 'd1', 'processed', 4.5, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_ignored_2', 'subv_corr_16', 'p1', 'd1', 'failed', 4.6, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),

        -- trying to correct delayed corrections, must be delayed
        ('subv_processed_2_delayed', 'subv_processed_2_delayed_1', 'p2', 'd2', 'new', 5.2, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_3_delayed', 'subv_processed_3_delayed_1', 'p3', 'd3', 'new', 5.3, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_7_delayed', 'subv_processed_7_delayed_1', 'p7', 'd7', 'new', 5.7, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_8_delayed', 'subv_processed_8_delayed_1', 'p8', 'd8', 'new', 5.8, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),

        -- trying to correct previously processed corrections, must be ignored because receipt is not processed yet
        ('subv_processed_1_1_new', 'subv_processed_1_1_new_new', 'p1', 'd1', 'new', 6.1, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_1_3_new', 'subv_processed_1_3_new_new', 'p1', 'd1', 'new', 6.3, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),

        -- trying to correct previously failed after cancel correcitons, must be failed
        ('subv_processed_4_failed', 'subv_processed_4_failed_1', 'p4', 'd4', 'new', 7.4, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_5_failed', 'subv_processed_5_failed_1', 'p5', 'd5', 'new', 7.5, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_processed_6_failed', 'subv_processed_6_failed_1', 'p6', 'd6', 'new', 7.6, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),

        -- trying to correct newly added receipts after dissmission, must be ignored
        ('subv_failed_1_new', 'subv_failed_1_new_1', 'p1', 'd1', 'new', 8.2, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_failed_wont_fix_1_new', 'subv_failed_wont_fix_1_new_1', 'p1', 'd1', 'new', 8.3, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        -- but this one must be missing inn
        ('subv_missing_inn_1_new', 'subv_missing_inn_1_new_1', 'p1', 'd1', 'new', 8.4, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),

       -- testing behaviour for cancelled and dismissed subventions
        ('subv_cancelled_1', 'subv_cancelled_1_new', 'p1', 'd1', 'new', 3.5, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_cancelled_2', 'subv_cancelled_2_new', 'p1', 'd1', 'new', 3.6, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_cancelled_3', NULL, 'p1', 'd1', 'new', 0.0, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_dismissed_1', 'subv_dismissed_1_new', 'p1', 'd1', 'new', 3.7, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_dismissed_2', 'subv_dismissed_2_new', 'p1', 'd1', 'new', 3.8, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('subv_dismissed_3', NULL, 'p1', 'd1', 'new', 0.0, NOW(), NOW(), NOW(), NOW(), NOW(), NOW()),
        ('outdated_1', NULL, 'p1', 'd1', 'new', 0.0, NOW(), NOW(), NOW(), NOW(), NOW(), NOW());
