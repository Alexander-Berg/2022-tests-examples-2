INSERT INTO bd_testsuite_02.doc_journal
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
    10002,
    10000,
    '123.0',
    '2018-09-10 10:07:52.019582'::timestamp,
    'test',
    10000,
    NULL
),
(
    10002,
    20000,
    '123.0',
    '2018-09-10 10:07:52.019582'::timestamp,
    'test',
    NULL,
    NULL
),
(
    20002,
    10000,
    '123.0',
    '2018-09-10 10:07:52.019582'::timestamp,
    'test',
    NULL,
    NULL
),
(
    20002,
    20000,
    '123.0',
    '2018-09-10 10:07:52.019582'::timestamp,
    'test',
    NULL,
    '{"b": "c"}'
);
