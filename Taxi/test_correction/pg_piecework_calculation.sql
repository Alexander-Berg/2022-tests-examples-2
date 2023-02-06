INSERT INTO piecework.calculation_rule (
    calculation_rule_id,
    tariff_type,
    start_date,
    stop_date,
    repeat,
    countries,
    logins,
    status,
    description,
    payment_draft_ids
) VALUES (
    'some_rule_id',
    'support-taxi',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['rus'],
    NULL,
    'success',
    'OK',
    '{"rus": 123}'::JSONB
), (
    'call_taxi_rule_id',
    'call-taxi',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru'],
    NULL,
    'success',
    'OK',
    '{"rus": 456}'::JSONB
), (
    'vezet_rule_id',
    'call-taxi-vezet',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru'],
    NULL,
    'success',
    'OK',
    '{"rus": 456}'::JSONB
);

INSERT INTO piecework.calculation_result(
  calculation_result_id, country, tariff_type, calculation_rule_id, start_date,
  stop_date, login, detail, daytime_cost, night_cost,
  holidays_daytime_cost, holidays_night_cost, benefits,
  extra_workshift_benefits, branch_benefit_conditions, conversion_benefits,
  cargo_benefits, corporate_benefits, newbie_cargo_benefits,
  newbie_corporate_benefits, min_qa_ratio, calc_type, calc_subtype,
  benefit_conditions
) VALUES (
  'result_id_1', 'rus', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanov', '{}',
  10.0, 5.0, 8.0, 1.0, 0.0, NULL,
  ('{' ||
    '"min_hour_cost": "1.0",' ||
    '"min_csat_ratio": "80.0",' ||
    '"min_qa_ratio": "90.0",' ||
    '"high_benefit_percentage": "10.0",' ||
    '"low_benefit_percentage": "90.0",' ||
    '"rating_avg_duration_weight": "0.0",' ||
    '"rating_total_cost_weight": "0.0025",' ||
    '"rating_csat_weight": "0.49875",' ||
    '"rating_qa_weight": "0.49875",' ||
    '"high_benefit_factor": "0.5",' ||
    '"low_benefit_factor": "0.2"' ||
  '}')::JSONB,
  NULL, NULL, NULL, NULL, NULL, NULL, 'general', 'chatterbox', NULL
), (
  'result_id_2', 'rus', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrov', '{}',  15.0, 7.0, 10.0, 0.0,
  0.0, NULL,
  ('{' ||
    '"min_hour_cost": "1.0",' ||
    '"min_csat_ratio": "80.0",' ||
    '"min_qa_ratio": "90.0",' ||
    '"high_benefit_percentage": "10.0",' ||
    '"low_benefit_percentage": "90.0",' ||
    '"rating_avg_duration_weight": "0.0",' ||
    '"rating_total_cost_weight": "0.0025",' ||
    '"rating_csat_weight": "0.49875",' ||
    '"rating_qa_weight": "0.49875",' ||
    '"high_benefit_factor": "0.5",' ||
    '"low_benefit_factor": "0.5"' ||
  '}')::JSONB,
  NULL, NULL, NULL, NULL, NULL, NULL, 'general', 'chatterbox', NULL
), (
  'result_id_4', 'rus', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'smirnoff', '{}', 0.0, 0.0, 0.0, 0.0,
  0.0, NULL,
  ('{' ||
    '"min_hour_cost": "1.0",' ||
    '"min_csat_ratio": "80.0",' ||
    '"min_qa_ratio": "90.0",' ||
    '"high_benefit_percentage": "10.0",' ||
    '"low_benefit_percentage": "90.0",' ||
    '"rating_avg_duration_weight": "0.0",' ||
    '"rating_total_cost_weight": "0.0025",' ||
    '"rating_csat_weight": "0.49875",' ||
    '"rating_qa_weight": "0.49875",' ||
    '"high_benefit_factor": "0.5",' ||
    '"low_benefit_factor": "0.2"' ||
  '}')::JSONB,
  NULL, NULL, NULL, NULL, NULL, NULL, 'general', 'chatterbox', NULL
), (
  'result_id_5', 'rus', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanoff', NULL, 10.0, 0.0, 0.0, 0.0,
  NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
  'correction', 'intermediate', NULL
), (
  'result_id_6', 'blr', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'popov', '{}', 0.0, 0.0, 0.0, 0.0,
  0.0, NULL,
  ('{' ||
    '"min_hour_cost": "1.0",' ||
    '"min_csat_ratio": "80.0",' ||
    '"min_qa_ratio": "90.0",' ||
    '"high_benefit_percentage": "10.0",' ||
    '"low_benefit_percentage": "90.0",' ||
    '"rating_avg_duration_weight": "0.0",' ||
    '"rating_total_cost_weight": "0.0025",' ||
    '"rating_csat_weight": "0.49875",' ||
    '"rating_qa_weight": "0.49875",' ||
    '"high_benefit_factor": "0.5",' ||
    '"low_benefit_factor": "0.2"' ||
  '}')::JSONB,
  NULL, NULL, NULL, NULL, NULL, NULL, 'correction', 'final', NULL
);

INSERT INTO piecework.payment(
  payment_id, tariff_type, calculation_rule_id, start_date,
  stop_date, country, login, branch, daytime_cost, night_cost,
  holidays_daytime_cost, holidays_night_cost, total_cost, min_hour_cost, workshifts_duration,
  plan_workshifts_duration, csat_ratio, min_csat_ratio, qa_ratio, min_qa_ratio,
  rating_factor, rating, high_benefit_percentage, low_benefit_percentage, benefit_factor,
  extra_workshift_benefits, benefits, extra_costs, branch_benefit_conditions
) VALUES (
  'result_id_1', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'rus', 'ivanov', 'general',
  10.0, 5.0, 8.0, 1.0, 23.0, 1.0, 10.0, 10.0, 85.0, 80.0, 95.0, 90.0, 1.0,
  50.0, 0.0, 0.0, 0.5, 11.0, 0.0, NULL,
  ('{' ||
    '"min_hour_cost": "1.0",' ||
    '"min_csat_ratio": "80.0",' ||
    '"min_qa_ratio": "90.0",' ||
    '"high_benefit_percentage": "10.0",' ||
    '"low_benefit_percentage": "90.0",' ||
    '"rating_avg_duration_weight": "0.0",' ||
    '"rating_total_cost_weight": "0.0025",' ||
    '"rating_csat_weight": "0.49875",' ||
    '"rating_qa_weight": "0.49875",' ||
    '"high_benefit_factor": "0.5",' ||
    '"low_benefit_factor": "0.2"' ||
  '}')::JSONB
), (
  'result_id_2', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'rus', 'petrov', 'general',
  25.0, 7.0, 10.0, 0.0, 42.0, 1.0, 12.0, 12.0, 90.0, 80.0, 100.0, 90.0, 1.0,
  40.0, 0.0, 0.0, 0.5, 16.0, 0.0, NULL,
  ('{' ||
    '"min_hour_cost": "1.0",' ||
    '"min_csat_ratio": "80.0",' ||
    '"min_qa_ratio": "90.0",' ||
    '"high_benefit_percentage": "10.0",' ||
    '"low_benefit_percentage": "90.0",' ||
    '"rating_avg_duration_weight": "0.0",' ||
    '"rating_total_cost_weight": "0.0025",' ||
    '"rating_csat_weight": "0.49875",' ||
    '"rating_qa_weight": "0.49875",' ||
    '"high_benefit_factor": "0.5",' ||
    '"low_benefit_factor": "0.5"' ||
  '}')::JSONB
), (
  'result_id_4', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'rus', 'smirnoff', 'general',
  0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 70.0, 80.0, 60.0, 0.0, 1.0, 30.0,
  0.0, 0.0, 0.5, 0.0, 0.0, NULL,
  ('{' ||
    '"min_hour_cost": "1.0",' ||
    '"min_csat_ratio": "80.0",' ||
    '"min_qa_ratio": "90.0",' ||
    '"high_benefit_percentage": "10.0",' ||
    '"low_benefit_percentage": "90.0",' ||
    '"rating_avg_duration_weight": "0.0",' ||
    '"rating_total_cost_weight": "0.0025",' ||
    '"rating_csat_weight": "0.49875",' ||
    '"rating_qa_weight": "0.49875",' ||
    '"high_benefit_factor": "0.5",' ||
    '"low_benefit_factor": "0.2"' ||
  '}')::JSONB
), (
  'result_id_5', 'support-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'blr', 'popov', 'general',
  0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 70.0, 80.0, 60.0, 0.0, 1.0, 30.0,
  0.0, 0.0, 0.5, 0.0, 0.0, NULL,
  ('{' ||
    '"min_hour_cost": "1.0",' ||
    '"min_csat_ratio": "80.0",' ||
    '"min_qa_ratio": "90.0",' ||
    '"high_benefit_percentage": "10.0",' ||
    '"low_benefit_percentage": "90.0",' ||
    '"rating_avg_duration_weight": "0.0",' ||
    '"rating_total_cost_weight": "0.0025",' ||
    '"rating_csat_weight": "0.49875",' ||
    '"rating_qa_weight": "0.49875",' ||
    '"high_benefit_factor": "0.5",' ||
    '"low_benefit_factor": "0.2"' ||
  '}')::JSONB
);

INSERT INTO piecework.payment_draft (
  payment_draft_id, tariff_type, calculation_rule_id, country, start_date,
  stop_date, status, approvals_id
) VALUES (
  'some_draft_id', 'support-taxi', 'some_rule_id', 'rus', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'need_approval', 123
), (
  'blr_draft_id', 'support-taxi', 'some_rule_id', 'blr', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'need_approval', 123
);
