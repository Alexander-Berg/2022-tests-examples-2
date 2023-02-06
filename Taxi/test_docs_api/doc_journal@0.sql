INSERT INTO bd_testsuite_00.doc_journal
(
    doc_id,
    account_id,
    amount,
    event_at,
    reason,
    journal_entry_id,
    details
)
VALUES
(
    10000,
    10000,
    '123.0',
    '2018-09-10 10:07:52.019582'::timestamp,
    '',
    NULL,
    NULL
),
(
    20000,
    10000,
    '123.0',
    '2018-09-10 10:07:52'::timestamp,
    '',
    NULL,
    '{"a": 1}'
);
