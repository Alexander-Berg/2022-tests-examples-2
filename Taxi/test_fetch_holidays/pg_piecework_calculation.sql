INSERT INTO piecework.calculation_rule (
    calculation_rule_id,
    start_date,
    stop_date,
    repeat,
    countries,
    logins,
    status
) VALUES (
    'periodic_rule_id',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['rus', 'blr'],
    NULL,
    'waiting_oebs'
);

INSERT INTO piecework.oebs_holiday(
  oebs_holiday_id,
  login,
  holiday_date
) VALUES (
  'new_year_1_id',
  'some_login',
  '2020-01-01'::DATE
),
(
  'new_year_2_id',
  'other_login',
  '2020-01-01'::DATE
);
