INSERT INTO bd_testsuite_04.doc_journal
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
    20004,
    10000,
    '123.0',
    '2018-09-10 10:07:52.019582'::timestamp,
    'test',
    NULL,
    NULL
),
(
    30004,
    10000,
    '123.0',
    '2018-09-10 10:07:52.019582'::timestamp,
    'test',
    NULL,
    NULL
);

INSERT INTO bd_testsuite_07.doc_journal
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
    10007,
    10000,
    '123.0',
    '2018-09-10 10:07:52.019582'::timestamp,
    'test',
    10000,
    NULL
),
(
    10007,
    20000,
    '123.0',
    '2018-09-10 10:07:52.019582'::timestamp,
    'test',
    NULL,
    NULL
);
