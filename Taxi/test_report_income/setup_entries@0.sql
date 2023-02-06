INSERT INTO se_income.entries
(id, park_id, contractor_id,
 agreement_id, sub_account, doc_ref, event_at,
 inn_pd_id, is_own_park, do_send_receipt,
 status, amount, order_id, reverse_entry_id,
 receipt_id, receipt_url)
VALUES
    (3, 'p3', 'c3',  -- processed as FROM_LEGAL_ENTITY order ownpark-se
     'agreement3', 'subaccount3', 103, '2022-02-02T02:02+02',
     'inn3_pd_id', TRUE, TRUE,
     'NEW', '1.815', 'order3', NULL,
     NULL, NULL),
    (4, 'p4', 'c4',  -- processed as FROM_LEGAL_ENTITY subvention quasi-se
     'agreement4', 'subaccount4', 104, '2022-02-02T02:02+02',
     'inn4_pd_id', FALSE, TRUE,
     'NEW', '1.815', 'order4', NULL,
     NULL, NULL),
    (7, 'p7', 'c7',  -- TAXPAYER_UNREGISTERED
     'agreement7', 'subaccount7', 107, '2022-02-02T02:02+02',
     'inn7_pd_id', TRUE, TRUE,
     'NEW', '1.815', 'order7', NULL,
     NULL, NULL),
    (9, 'p9', 'c9',  -- TAXPAYER_UNBOUND
     'agreement9', 'subaccount9', 109, '2022-02-02T02:02+02',
     'inn9_pd_id', TRUE, TRUE,
     'NEW', '1.815', 'order9', NULL,
     NULL, NULL),
    (10, 'p10', 'c10',  -- PERMISSION_NOT_GRANTED
     'agreement10', 'subaccount10', 110, '2022-02-02T02:02+02',
     'inn10_pd_id', TRUE, TRUE,
     'NEW', '1.815', 'order10', NULL,
     NULL, NULL),
    (11, 'p11', 'c11',  -- REQUEST_VALIDATION_ERROR
     'agreement11', 'subaccount11', 111, '2022-02-02T02:02+02',
     'inn11_pd_id', TRUE, TRUE,
     'NEW', '1.815', 'order11', NULL,
     NULL, NULL),
    (12, 'p12', 'c12',  -- TAXPAYER_UNBOUND but already known
     'agreement12', 'subaccount12', 121, '2022-02-02T02:02+02',
     'inn12_pd_id', TRUE, TRUE,
     'NEW', '1.815', 'order12', NULL,
     NULL, NULL);
