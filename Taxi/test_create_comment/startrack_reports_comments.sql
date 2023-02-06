insert into
    startrack_reports.comments
(
    pk,
    ticket,
    locale,
    audit_action_id,
    comment_data,
    summonees
)
values
(
    1,
    'TAXIRATE-35',
    'ru',
    '',
    '{"action": "drafts.commissions_create", "action_time": "action_time", "login": "ydemidenko", "data": {"current": {"enabled": true}, "new": {"enabled": false}}}',
    '{"ydemidenko"}'
),
(
    2,
    'TAXIRATE-35',
    'ru',
    '559134566c090a24c5a123f4',
    '{}',
    '{"ydemidenko"}'
),
(
    3,
    'TAXIRATE-35',
    'ru',
    '',
    '{"action": "test_action", "login": "test_login", "data": {"current": {"test_key": 3}, "new": {"test_key": 5}}}',
    '{"test_login"}'
);
