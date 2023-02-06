INSERT INTO se_income.entries
(id, park_id, contractor_id,
 agreement_id, sub_account, doc_ref, event_at,
 inn_pd_id, is_own_park, do_send_receipt,
 status, amount, order_id, reverse_entry_id,
 receipt_id, receipt_url)
VALUES
    (1, 'p1', 'c1',  -- processed as FROM_INDIVIDUAL
     'agreement1', 'subaccount1', 101, '2022-02-02T02:02+02',
     'inn1_pd_id', TRUE, TRUE,
     'NEW', '1.815', 'order1', NULL,
     NULL, NULL),
    (2, 'p2', 'c2',  -- skipped
     'agreement2', 'subaccount2', 102, '2022-02-02T02:02+02',
     'inn2_pd_id', FALSE, FALSE,
     'PROCESSED', '1.815', 'order2', NULL,
     NULL, NULL),
    (5, 'p5', 'c5',  -- skipped in config
     'agreement5', 'subaccount5', 105, '2022-02-02T02:02+02',
     'inn5_pd_id', TRUE, TRUE,
     'NEW', '1.815', 'order5', NULL,
     NULL, NULL),
    (6, 'p6', 'c6',  -- duplicate
     'agreement6', 'subaccount6', 106, '2022-02-02T02:02+02',
     'inn6_pd_id', TRUE, TRUE,
     'NEW', '1.815', 'order6', NULL,
     NULL, NULL),
    (8, 'p8', 'c8',  -- REQUEST_VALIDATION_ERROR with YEAR and THRESHOLD
     'agreement8', 'subaccount8', 108, '2022-02-02T02:02+02',
     'inn8_pd_id', TRUE, TRUE,
     'NEW', '1.815', 'order8', NULL,
     NULL, NULL);
