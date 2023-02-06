INSERT INTO piecework.branch_reserve (
    branch_reserve_id, tariff_type, country, branch, period_limit, initial_offset,
    weekends_weight
) VALUES
('existing_reserve_id', 'support-taxi', 'ru', 'existing_branch', 500, 0, 0),
('ru_default_reserve_id', 'support-taxi', 'ru', '__default__', 1500, 100, 0.3),
('by_default_reserve_id', 'support-taxi', 'by', '__default__', 1000, 200, 0.2),
('other_reserve_id', 'support-taxi', 'ru', 'other_branch', 1500, 100, 0.3),
('reserve1', 'cargo-callcenter', 'ru', '__default__', 100, 10, 0.0),
('reserve2', 'cargo-callcenter', 'ru', 'general', 150, 11, 0.1),
('reserve3', 'cargo-callcenter', 'by', '__default__', 200, 50, 0.0),
('reserve4', 'call-taxi', 'ru', '__default__', 50, 0, 0.2),
('reserve5', 'call-taxi', 'ru', 'eats', 200, 20, 0.3);

INSERT INTO piecework.agent_employee(
    agent_employee_id, tariff_type, start_date, stop_date, login,
    country, branch
) VALUES (
    'ivanov_id', 'cargo-callcenter', '2020-01-01', '2020-01-16', 'ivanov',
    'ru', 'old'
), (
    'popov_id', 'support-taxi', '2020-01-01', '2020-01-16', 'popov', 'ru',
    'other_branch'
), (
    'stahanov_id', 'cargo-callcenter', '2022-01-16', '2020-02-01', 'stahanov',
    'ru', 'cargo_branch'
), (
    'kotov_id', 'support-taxi', '2022-01-16', '2020-02-01', 'kotov',
    'by', 'other_branch'
), (
    'smirnov_id', 'cargo-callcenter', '2022-01-16', '2020-02-01', 'smirnov',
    'by', 'general'
), (
    'old_login_id', 'cargo-callcenter', '2022-01-16', '2020-02-01',
    'old_login', 'by', 'general'
);

INSERT INTO piecework.calculation_rule(
    calculation_rule_id, start_date, stop_date, repeat, countries, logins,
    status, tariff_type, rule_type
) VALUES (
  'old_rule_id', '2021-12-16', '2022-01-01', True, ARRAY['by'], NULL,
  'success', 'cargo-callcenter', 'regular'
), (
  'some_rule_id', '2022-01-01', '2022-01-16', True, ARRAY['ru'], NULL,
  'success', 'cargo-callcenter', 'regular'
), (
  'eats_rule_id', '2022-01-01', '2022-01-16', True, ARRAY['ru'], NULL,
  'success', 'call-taxi', 'regular'
), (
  'new_rule_id', '2022-01-16', '2022-02-01', True, ARRAY['ru'], NULL,
  'success', 'cargo-callcenter', 'regular'
);

INSERT INTO piecework.payment(
  payment_id, tariff_type, calculation_rule_id, start_date,
  stop_date, country, login, branch, daytime_cost, night_cost,
  holidays_daytime_cost, holidays_night_cost, total_cost, created
) VALUES (
  'result_id_0', 'cargo-callcenter', 'old_rule_id', '2021-12-16',
  '2022-01-01', 'by', 'ivanov', 'old',
  0, 0, 0, 1, 1, '2022-01-01T00:00:00'
), (
  'result_id_1', 'cargo-callcenter', 'some_rule_id', '2022-01-01',
  '2022-01-16', 'ru', 'ivanov', 'general',
  15.0, 7.0, 10.0, 0.0, 32.0, '2022-01-16T00:00:00'
), (
  'result_id_2', 'cargo-callcenter', 'some_rule_id', '2022-01-01',
  '2022-01-16', 'ru', 'petrov', 'urgent',
  1.0, 2.0, 3.0, 4.0, 10.0, '2022-01-16T00:00:00'
), (
  'result_id_3', 'call-taxi', 'eats_rule_id', '2022-01-01',
  '2022-01-16', 'ru', 'petrov', 'eats',
  1.0, 2.0, 3.0, 4.0, 10.0, '2022-01-15T00:00:00'
), (
  'result_id_4', 'cargo-callcenter', 'new_rule_id', '2022-01-16',
  '2022-02-01', 'ru', 'ivanov', 'new',
  5.0, 17.0, 3.0, 0.0, 25.0, '2022-02-01T00:00:00'
), (
  'result_id_5', 'cargo-callcenter', 'new_rule_id', '2022-01-16',
  '2022-02-01', 'ru', 'stahanov', 'new',
  5.0, 17.0, 3.0, 0.0, 25.0, '2022-02-01T00:00:00'
), (
  'result_id_6', 'cargo-callcenter', 'new_rule_id', '2022-01-16',
  '2022-02-01', 'by', 'smirnov', 'new',
  5.0, 17.0, 3.0, 0.0, 25.0, '2022-02-01T00:00:00'
);

INSERT INTO piecework.workshift(
    workshift_id, tariff_type, start_date, stop_date, login, start_dt, stop_dt
) VALUES (
    'shift1', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'ivanov',
    '2022-01-01T08:00:00', '2022-01-01T20:00:00'
), (
    'shift2', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'ivanov',
    '2022-01-02T08:00:00', '2022-01-02T20:00:00'
), (
    'shift3', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'ivanov',
    '2022-01-05T08:00:00', '2022-01-05T20:00:00'
), (
    'shift4', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'ivanov',
    '2022-01-06T08:00:00', '2022-01-06T20:00:00'
), (
    'shift5', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'ivanov',
    '2022-01-09T08:00:00', '2022-01-09T20:00:00'
), (
    'shift6', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'ivanov',
    '2022-01-10T08:00:00', '2022-01-10T20:00:00'
), (
    'shift7', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'ivanov',
    '2022-01-10T08:00:00', '2022-01-13T20:00:00'
), (
    'shift8', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'ivanov',
    '2022-01-10T08:00:00', '2022-01-14T20:00:00'
), (
    'shift9', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'petrov',
    '2022-01-01T20:00:00', '2022-01-02T08:00:00'
), (
    'shift10', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'petrov',
    '2022-01-03T20:00:00', '2022-01-04T08:00:00'
), (
    'shift11', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'petrov',
    '2022-01-07T20:00:00', '2022-01-08T08:00:00'
), (
    'shift12', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'petrov',
    '2022-01-09T20:00:00', '2022-01-10T08:00:00'
), (
    'shift13', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'petrov',
    '2022-01-13T20:00:00', '2022-01-14T08:00:00'
), (
    'shift14', 'cargo-callcenter', '2022-01-01', '2022-01-16', 'petrov',
    '2022-01-15T20:00:00', '2022-01-15T21:00:00'
), (
    'shift15', 'cargo-callcenter', '2021-12-16', '2022-01-01', 'ivanov',
    '2021-12-16T08:00:00', '2021-12-16T20:00:00'
), (
    'shift16', 'cargo-callcenter', '2021-12-16', '2022-01-01', 'ivanov',
    '2021-12-17T08:00:00', '2021-12-17T20:00:00'
), (
    'shift17', 'cargo-callcenter', '2021-12-16', '2022-01-01', 'ivanov',
    '2021-12-24T08:00:00', '2021-12-24T20:00:00'
), (
    'shift18', 'cargo-callcenter', '2021-12-16', '2022-01-01', 'ivanov',
    '2021-12-25T08:00:00', '2021-12-25T20:00:00'
), (
    'shift19', 'cargo-callcenter', '2021-12-16', '2022-01-01', 'ivanov',
    '2021-12-28T08:00:00', '2021-12-28T20:00:00'
), (
    'shift20', 'cargo-callcenter', '2021-12-16', '2022-01-01', 'ivanov',
    '2021-12-29T08:00:00', '2021-12-29T20:00:00'
), (
    'shift21', 'call-taxi', '2022-01-01', '2022-01-16', 'petrov',
    '2022-01-01T20:00:00', '2022-01-02T08:00:00'
), (
    'shift22', 'call-taxi', '2022-01-01', '2022-01-16', 'petrov',
    '2022-01-03T20:00:00', '2022-01-04T08:00:00'
), (
    'shift23', 'call-taxi', '2022-01-01', '2022-01-16', 'petrov',
    '2022-01-13T20:00:00', '2022-01-14T08:00:00'
), (
    'shift24', 'call-taxi', '2022-01-01', '2022-01-16', 'petrov',
    '2022-01-15T20:00:00', '2022-01-15T21:00:00'
), (
    'shift25', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'ivanov',
    '2022-01-16T08:00:00', '2022-01-16T20:00:00'
), (
    'shift26', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'ivanov',
    '2022-01-17T08:00:00', '2022-01-17T20:00:00'
), (
    'shift27', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'ivanov',
    '2022-01-24T08:00:00', '2022-01-24T20:00:00'
), (
    'shift28', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'ivanov',
    '2022-01-25T08:00:00', '2022-01-25T20:00:00'
), (
    'shift29', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'ivanov',
    '2022-01-28T08:00:00', '2022-01-28T20:00:00'
), (
    'shift30', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'ivanov',
    '2022-01-29T08:00:00', '2022-01-29T20:00:00'
), (
    'shift31', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-16T08:00:00', '2022-01-16T20:00:00'
), (
    'shift32', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-17T08:00:00', '2022-01-17T20:00:00'
), (
    'shift33', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-18T08:00:00', '2022-01-18T20:00:00'
), (
    'shift34', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-19T08:00:00', '2022-01-19T20:00:00'
), (
    'shift35', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-20T08:00:00', '2022-01-20T20:00:00'
), (
    'shift36', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-21T08:00:00', '2022-01-21T20:00:00'
), (
    'shift37', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-22T08:00:00', '2022-01-22T20:00:00'
), (
    'shift38', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-23T08:00:00', '2022-01-23T20:00:00'
), (
    'shift39', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-24T08:00:00', '2022-01-24T20:00:00'
), (
    'shift40', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-25T08:00:00', '2022-01-25T20:00:00'
), (
    'shift41', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-26T08:00:00', '2022-01-26T20:00:00'
), (
    'shift42', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-27T08:00:00', '2022-01-27T20:00:00'
), (
    'shift43', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-28T08:00:00', '2022-01-28T20:00:00'
), (
    'shift44', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-29T08:00:00', '2022-01-29T20:00:00'
), (
    'shift45', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-30T08:00:00', '2022-01-30T20:00:00'
), (
    'shift46', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'stahanov',
    '2022-01-31T08:00:00', '2022-01-31T20:00:00'
), (
    'shift47', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'smirnov',
    '2022-01-16T08:00:00', '2022-01-16T20:00:00'
), (
    'shift48', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'smirnov',
    '2022-01-17T08:00:00', '2022-01-17T20:00:00'
), (
    'shift49', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'smirnov',
    '2022-01-24T08:00:00', '2022-01-24T20:00:00'
), (
    'shift50', 'cargo-callcenter', '2022-01-16', '2022-02-01', 'smirnov',
    '2022-01-25T08:00:00', '2022-01-25T20:00:00'
);
