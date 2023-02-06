INSERT INTO piecework.agent_employee(
  agent_employee_id,
  tariff_type,
  start_date,
  stop_date,
  login,
  country,
  branch
) VALUES (
  'ivanov_id',
  'driver-hiring',
  '2020-01-01'::DATE,
  '2020-01-16'::DATE,
  'ivanov',
  'rus',
  'general'
), (
  'petrov_id',
  'driver-hiring',
  '2020-01-01'::DATE,
  '2020-01-16'::DATE,
  'petrov',
  'blr',
  'general'
), (
  'smirnoff_id',
  'driver-hiring',
  '2020-01-01'::DATE,
  '2020-01-16'::DATE,
  'smirnoff',
  'rus',
  'general'
);

INSERT INTO piecework.calculation_rule (
    calculation_rule_id,
    tariff_type,
    start_date,
    stop_date,
    repeat,
    countries,
    logins,
    status,
    description
) VALUES (
    'some_rule_id',
    'driver-hiring',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['rus', 'blr'],
    NULL,
    'waiting_benefits',
    'OK'
), (
    'corrected_rule_id',
    'driver-hiring',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['rus', 'blr'],
    NULL,
    'waiting_benefits',
    'OK'
);

INSERT INTO piecework.calculation_result(
  calculation_result_id, tariff_type, calculation_rule_id, start_date,
  stop_date, login, daytime_cost, night_cost,
  holidays_daytime_cost, holidays_night_cost, benefits,
  benefit_conditions, calc_type, calc_subtype
) VALUES (
  'result_id_1', 'driver-hiring', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanov', 7.0, 2.0, 5.0, 0.0,
  NULL,
  (
      '{' ||
       '"min_hour_cost": 1.0, "workshifts_duration_sec": 36000.0, ' ||
       '"plan_workshifts_duration_sec": 36000.0, ' ||
       '"min_workshifts_ratio": 0.25, ' ||
       '"conversion_ratio": 90.0, "unified_qa_ratio": 85.0, ' ||
       '"conversion_rating_weight": 0.2, ' ||
       '"hour_cost_rating_weight": 0.3, ' ||
       '"unified_qa_rating_weight": 0.4, ' ||
       '"benefit_thresholds_strict": [' ||
        '{"threshold": 0, "value": 0.5}, ' ||
        '{"threshold": 80, "value": 0.0}' ||
       ']' ||
      '}'
  )::JSONB,
  'general', 'chatterbox'
), (
  'result_id_2', 'driver-hiring', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanov', 3.0, 3.0, 3.0, 0.0,
  NULL, NULL, 'correction', 'intermediate'
), (
  'result_id_3', 'driver-hiring', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrov', 15.0, 7.0, 10.0, 0.0,
  NULL,
  (
      '{' ||
       '"min_hour_cost": 1.0, "workshifts_duration_sec": 28800.0, ' ||
       '"plan_workshifts_duration_sec": 36000.0, ' ||
       '"min_workshifts_ratio": 0.25, ' ||
       '"unified_qa_ratio": 80.0, "conversion_ratio": 65.0, ' ||
       '"conversion_rating_weight": 0.2, ' ||
       '"hour_cost_rating_weight": 0.3, ' ||
       '"unified_qa_rating_weight": 0.4, ' ||
       '"benefit_thresholds_strict": [' ||
        '{"threshold": 0, "value": 0.5}, ' ||
        '{"threshold": 80, "value": 0.0}' ||
       ']' ||
      '}'
  )::JSONB,
  'general', 'chatterbox'
), (
  'result_id_4', 'driver-hiring', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrov', 0.0, 3.0, 3.0, 3.0,
  3.0, NULL, 'correction', 'final'
), (
  'result_id_5', 'driver-hiring', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'smirnoff', 0.0, 0.0, 0.0, 0.0,
  NULL,
    (
      '{' ||
       '"min_hour_cost": 1.0, "workshifts_duration_sec": 7200.0, ' ||
       '"plan_workshifts_duration_sec": 36000.0, ' ||
       '"min_workshifts_ratio": 0.25, ' ||
       '"unified_qa_ratio": 90.0, "conversion_ratio": 95.0, ' ||
       '"conversion_rating_weight": 0.2, ' ||
       '"hour_cost_rating_weight": 0.3, ' ||
       '"unified_qa_rating_weight": 0.4, ' ||
       '"benefit_thresholds_strict": [' ||
        '{"threshold": 0, "value": 0.5}, ' ||
        '{"threshold": 80, "value": 0.0}' ||
       ']' ||
      '}'
  )::JSONB,
  'general', 'chatterbox'
);

INSERT INTO piecework.payment_draft (
  payment_draft_id, tariff_type, calculation_rule_id, country, start_date,
  stop_date, status, approvals_id
) VALUES (
  'some_draft_id', 'driver-hiring', 'some_rule_id', 'rus', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'failed', 123
), (
  'corrected_draft_id', 'driver-hiring', 'corrected_rule_id', 'rus',
  '2020-01-01'::DATE, '2020-01-16'::DATE, 'updating', 1
);
