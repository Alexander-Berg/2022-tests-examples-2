INSERT INTO piecework.calculation_rule (
    calculation_rule_id,
    tariff_type,
    start_date,
    stop_date,
    repeat,
    countries,
    logins,
    status
) VALUES (
    'unified_rule_id',
    'call-taxi-unified',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru'],
    null,
    'waiting_agent'
), (
    'logins_rule_id',
    'support-taxi',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru'],
    ARRAY['ivanov', 'petrov'],
    'waiting_agent'
), (
    'cargo_rule_id',
    'cargo-callcenter',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru'],
    null,
    'waiting_agent'
);

INSERT INTO piecework.agent_employee(
  agent_employee_id,
  tariff_type,
  start_date,
  stop_date,
  country,
  login,
  branch,
  created,
  updated
) VALUES (
    'employee1',
    'call-taxi-unified',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'ivanov',
    'first',
    '2020-01-10 00:00:00',
    '2020-01-10 00:00:00'
), (
    'employee2',
    'call-taxi-unified',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'petrov',
    'second',
    '2020-01-10 00:00:00',
    '2020-01-10 00:00:00'
), (
    'employee3',
    'call-taxi-unified',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'popov',
    'second',
    '2020-01-10 00:00:00',
    '2020-01-10 00:00:00'
), (
    'employee4',
    'cargo-callcenter',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'ivanov',
    'first',
    '2020-01-10 00:00:00',
    '2020-01-10 00:00:00'
), (
    'employee5',
    'cargo-callcenter',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'petrov',
    'second',
    '2020-01-10 00:00:00',
    '2020-01-10 00:00:00'
), (
    'employee6',
    'cargo-callcenter',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'popov',
    'second',
    '2020-01-10 00:00:00',
    '2020-01-10 00:00:00'
), (
    'employee7',
    'support-taxi',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'ivanov',
    'first',
    '2020-01-10 00:00:00',
    '2020-01-10 00:00:00'
), (
    'employee8',
    'support-taxi',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'petrov',
    'second',
    '2020-01-10 00:00:00',
    '2020-01-10 00:00:00'
), (
    'employee9',
    'support-taxi',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'wopov',
    'second',
    '2020-01-10 00:00:00',
    '2020-01-10 00:00:00'
);
