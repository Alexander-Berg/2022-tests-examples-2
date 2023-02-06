CREATE SCHEMA IF NOT EXISTS "taxi_cdm_piecework";
DROP TABLE IF EXISTS taxi_cdm_piecework.fct_operator_shift_act;
CREATE TABLE taxi_cdm_piecework.fct_operator_shift_act
(
    utc_shift_started_dttm TIMESTAMP WITH TIME ZONE NOT NULL,
    staff_login VARCHAR NOT NULL
);

INSERT INTO taxi_cdm_piecework.fct_operator_shift_act VALUES
    ('2021-01-16 00:00:00', 'ivanov'),
    ('2021-01-14 22:00:00', 'ivanov'),
    ('2021-01-15 00:00:00', 'petrov'),
    ('2021-01-16 21:00:00', 'petrov'),
    ('2021-01-14 20:00:00', 'petrov'),
    ('2021-01-14 00:00:00', 'bsidorov'),
    ('2021-01-15 00:00:00', 'bsidorov'),
    ('2021-01-16 00:00:00', 'bsidorov'),
    ('2021-01-19 00:00:00', 'bsidorov'),
    ('2021-01-15 00:00:00', 'popov'),
    ('2021-01-20 00:00:00', 'popov'),
    ('2021-01-14 23:00:00', 'by_ivanov'),
    ('2021-01-16 22:00:00', 'by_ivanov'),
    ('2021-01-17 21:00:00', 'by_petrov');

DROP TABLE IF EXISTS taxi_cdm_piecework.dim_operator_profile_hist;
CREATE TABLE taxi_cdm_piecework.dim_operator_profile_hist(
    staff_login VARCHAR NOT NULL,
    timezone VARCHAR,
    payment_period_start_dt DATE,
    utc_valid_from_dttm TIMESTAMP,
    utc_valid_to_dttm TIMESTAMP
);

INSERT INTO taxi_cdm_piecework.dim_operator_profile_hist VALUES
    ('ivanov', null, '2021-01-01', '2021-01-01T00:00:00Z', 'infinity'),
    ('petrov', 'Europe/Moscow', '2021-01-01', '2021-01-01T00:00:00Z', 'infinity'),
    ('petrov', 'Europe/Moscow', '2021-01-16', '2021-01-01T00:00:00Z', 'infinity'),
    ('bsidorov', 'Europe/Moscow', '2021-01-01', '2021-01-01T00:00:00Z', 'infinity'),
    ('popov', 'Europe/Moscow', '2021-01-01', '2021-01-01T00:00:00Z', 'infinity'),
    ('by_ivanov', 'Europe/Kaliningrad', '2021-01-01', '2021-01-01T00:00:00Z', 'infinity'),
    ('by_petrov', 'Europe/Kaliningrad', '2021-01-01', '2021-01-01T00:00:00Z', 'infinity');

INSERT INTO piecework.calculation_rule (
    calculation_rule_id,
    tariff_type,
    start_date,
    stop_date,
    repeat,
    countries,
    logins,
    status,
    rule_type
) VALUES (
    'cargo_rule_id',
    'cargo-callcenter',
    '2021-01-01'::DATE,
    '2021-01-13'::DATE,
    False,
    ARRAY['ru'],
    ARRAY['asmirnoff'],
    'waiting_agent',
    'dismissal'
), (
    'unified_rule_id',
    'call-taxi-unified',
    '2021-01-01'::DATE,
    '2021-01-13'::DATE,
    False,
    ARRAY['ru'],
    ARRAY['bsidorov'],
    'waiting_agent',
    'dismissal'
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
    'cargo-callcenter',
    '2021-01-01'::DATE,
    '2021-01-13'::DATE,
    'ru',
    'asmirnoff',
    'general',
    '2021-01-10 00:00:00',
    '2021-01-13 00:00:00'
), (
    'employee2',
    'call-taxi-unified',
    '2021-01-01'::DATE,
    '2021-01-13'::DATE,
    'ru',
    'bsidorov',
    'general',
    '2021-01-10 00:00:00',
    '2021-01-13 00:00:00'
);

INSERT INTO piecework.dismissal_nsz_days(
    id, login, number_nsz_days, term_date, calculation_rule_id, updated
) VALUES
    ('d1', 'asmirnoff', 4, '2021-01-16', 'cargo_rule_id', '2021-01-13 00:00:00'),
    ('d2', 'bsidorov', 5, '2021-01-17', 'unified_rule_id', '2021-01-13 00:00:00');
