INSERT INTO limits.limits (ref, currency, label, account_id, context, notifications)
VALUES
(
    'tumbling_eats',
    'RUB',
    'moscow',
    'budget/tumbling_eats',
    '{"tickets":["TAXIRATE-1"],"approvers":[]}',
    '[{"data":{"discount_id":"some_value","hierarchy":"another_value"},"kind":"stq","queue":"eats_restapp_promo_finish_on_limit"}]'
);

INSERT INTO limits.windows (limit_ref, type, size, value, threshold, label, start, ticket, last_notified_wid)
VALUES
    ('tumbling_eats', 'tumbling', 315360000, 10000, 100, 'Недельный', '2022-01-01T00:00:00+03:00', null, null);
