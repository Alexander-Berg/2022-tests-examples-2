INSERT INTO limits.limits (REF, currency, label, account_id, context)
VALUES
    ('discount_c0de', 'RUB', 'moscow', 'budget/discount_c0de', '{"tickets":["TAXIRATE-1"],"approvers":[]}')
;

INSERT INTO limits.windows (limit_ref, TYPE, SIZE, value, threshold, label, START, ticket, last_notified_wid)
VALUES
    ('discount_c0de', 'tumbling', 604800, 10000, 100, 'Недельный', '2000-01-01T18:00:00.000000+00:00', NULL, NULL)
;
