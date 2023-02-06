INSERT INTO piecework.calculation_rule (
    calculation_rule_id,
    start_date,
    stop_date,
    repeat,
    countries,
    logins,
    status,
    description,
    rule_type,
    payment_draft_ids,
    tariff_type
) VALUES (
    'some_rule_id',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['rus', 'blr'],
    NULL,
    'success',
    'OK',
    'regular',
    '{"rus": 123}'::JSONB,
    'support-taxi'

), (
    'dismissal_rule_id',
    '2021-01-01'::DATE,
    '2021-01-12'::DATE,
    False,
    ARRAY['rus'],
    NULL,
    'success',
    '',
    'dismissal',
    '{"rus": 123}'::JSONB,
    'call-taxi-unified'
);

INSERT INTO piecework.payment(
  payment_id, tariff_type, calculation_rule_id, start_date,
  stop_date, country, login, branch, daytime_cost, night_cost,
  holidays_daytime_cost, holidays_night_cost,
  total_cost, min_hour_cost, workshifts_duration,
  plan_workshifts_duration, csat_ratio, min_csat_ratio, qa_ratio, min_qa_ratio,
  rating_factor, high_benefit_percentage, low_benefit_percentage, benefit_factor,
  extra_workshift_benefits, benefits, extra_costs, branch_benefit_conditions,
  correction
) VALUES (
  'result_id_1', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'rus', 'ivanov', 'general',
  10.0, 5.0, 8.0, 1.0, 23.0, 1.0, 10.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
  0.0, 0.5, 0.0, 11.0,
  ('[{"source": "tracker", "daytime_bo": "10.0", "night_bo": "15.0", ' ||
   '"holidays_daytime_bo": "5.0", "holidays_night_bo": "0.0", ' ||
   '"total_bo": "20.0"}]')::JSONB,
  '{}'::JSONB,
  ('{"intermediate": {"daytime_bo": "3.0", "night_bo": "3.0", ' ||
   '"holidays_daytime_bo": "3.0", "holidays_night_bo": "3.0"},' ||
   '"final": {"daytime_bo": "2.0", "night_bo": "2.0", ' ||
   '"holidays_daytime_bo": "2.0", "holidays_night_bo": "2.0"}}')::JSONB
), (
  'result_id_2', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'rus', 'petrov', 'general',
  15.0, 7.0, 10.0, 0.0, 32.0, 1.0, 12.0, 12.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
  0.0, 0.5, 0.0, 16.0, NULL, '{}'::JSONB, NULL
), (
  'result_id_3', 'support-taxi', 'not_configured_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'blr', 'sidorov', 'general',
  15.0, 7.0, 10.0, 2.0, 34.0, 1.0, 15.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
  0.0, 0.5, 0.0, 16.0, NULL, '{}'::JSONB, NULL
), (
  'result_id_4', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'rus', 'smirnoff', 'general',
  0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, NULL, 0.0, NULL, 0.0, 0.0, 0.0, 0.0,
  0.0, 0.0, 0.0, NULL, '{}'::JSONB, '{"remove": true}'::JSONB
), (
  'result_id_5', 'call-taxi-unified', 'dismissal_rule_id', '2021-01-01'::DATE,
  '2021-01-12'::DATE, 'rus', 'sidorova', 'general',
  15.0, 7.0, 10.0, 2.0, 34.0, 1.0, 15.0, 15.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
  0.0, 0.5, 0.0, 16.0, NULL, '{}'::JSONB, NULL
), (
  'result_id_6', 'call-taxi-unified', 'dismissal_rule_id', '2021-01-01'::DATE,
  '2021-01-12'::DATE, 'rus', 'smirnova', 'general',
  0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, NULL, 0.0, NULL, 0.0, 0.0, 0.0, 0.0,
  0.0, 0.0, 0.0, NULL, '{}'::JSONB, NULL
);

INSERT INTO piecework.payment_draft (
  payment_draft_id, tariff_type, calculation_rule_id, country, start_date,
  stop_date, status, approvals_id, created
) VALUES (
  'wrong_draft_id', 'support-taxi', 'some_rule_id', 'rus', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'need_approval', NULL, '2020-01-01 00:00:00'
), (
  'uuid', 'support-taxi', 'some_rule_id', 'rus', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'need_approval', 123, '2020-01-01 01:00:00'
), (
  'dismissal_uuid', 'call-taxi-unified', 'dismissal_rule_id', 'rus',
  '2020-01-01'::DATE, '2020-01-12'::DATE, 'need_approval', 123,
  '2021-01-01 01:00:00'
);

INSERT INTO piecework.dismissal_nsz_days(
    id, login, number_nsz_days, term_date, calculation_rule_id
) VALUES
    ('d1', 'sidorova', 5, '2021-01-16', 'dismissal_rule_id'),
    ('d2', 'smirnova', 6, '2021-01-17', 'dismissal_rule_id');
