INSERT INTO piecework.calculation_rule (
    calculation_rule_id,
    start_date,
    stop_date,
    repeat,
    countries,
    logins,
    payment_draft_ids,
    status
) VALUES (
    'periodic_rule_id',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['rus', 'blr'],
    NULL,
    NULL,
    'waiting_agent'
), (
    'rus_rule_id',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    False,
    ARRAY['rus', 'blr'],
    NULL,
    NULL,
    'waiting_agent'
), (
    'other_logins_rule_id',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    False,
    ARRAY['usa'],
    ARRAY['other', 'logins'],
    NULL,
    'waiting_agent'
), (
    'success_rule_id',
    '2019-12-16'::DATE,
    '2020-01-01'::DATE,
    False,
    ARRAY['rus'],
    NULL,
    '{"rus": 12345}'::JSONB,
    'success'
);
