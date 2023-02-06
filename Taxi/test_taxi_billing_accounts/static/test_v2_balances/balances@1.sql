INSERT INTO ba_testsuite_06.entity(external_id, kind, created)
VALUES
(
    'unique_driver_id/5b4f48a941e102a72fefe30e',
    'driver',
    '2018-06-01T00:00:00'
);

INSERT INTO ba_testsuite_06.account
(
    id,
    entity_external_id,
    agreement_id,
    currency,
    sub_account,
    opened,
    expired
)
VALUES
(
    31310006,
    'unique_driver_id/5b4f48a941e102a72fefe30e',
    'ag-rule-autotest',
    'XXX',
    'autofill',
    '2018-08-09 17:00:54.048523',
    '2019-01-01 00:00:00'
);

INSERT INTO ba_testsuite_06.journal
(
    id,
    account_id,
    amount,
    doc_ref,
    event_at,
    created
)
SELECT
    (v.n + 1)*10000 + 6 as id,
    31310006 as account_id,
    v.n  + 1 as amount,
    v.n::text as doc_ref,
    '2018-08-20 00:00:00'::timestamp + v.n * interval '19 sec' as event_at,
    '2018-08-20 00:00:00'::timestamp + v.n * interval '19 sec' + interval '1 sec' as created
 FROM (SELECT generate_series(0, 3000) n) v
;
