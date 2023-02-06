INSERT INTO limits.limits (ref, currency, label, account_id, context)
VALUES
    ('tumbling', 'RUB', 'moscow', 'budget/tumbling', '{"tickets":["TAXIRATE-1"],"approvers":[]}'),
    ('sliding', 'RUB', 'moscow', 'budget/sliding', '{"tickets":["RUPRICING-1"],"approvers":["me"], "tags":["test_component"]}'),
    ('test_comment', 'RUB', 'moscow', 'budget/test_comment', '{"tickets":["FPRICING-1"],"approvers":["you"], "tags":[]}'),
    ('test_notified', 'RUB', 'moscow', 'budget/test_notified', '{"tickets":["TAXIRATE-13"],"approvers":[]}'),
    ('8811c56a-1f84-11eb-8086-5366a7d74448', 'RUB', 'moscow', 'budget/8811c56a-1f84-11eb-8086-5366a7d74448', '{"tickets":["TAXIRATE-13"],"approvers":[], "tags":[]}'),
    ('account_id', 'RUB', 'moscow', 'some_account_id', '{"tickets":["TAXIRATE-1"],"approvers":[]}')
;
