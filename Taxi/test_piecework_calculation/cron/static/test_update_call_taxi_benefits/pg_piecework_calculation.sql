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
    'call-taxi',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru'],
    NULL,
    'waiting_benefits',
    'OK'
), (
    'corrected_rule_id',
    'call-taxi',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru'],
    NULL,
    'waiting_benefits',
    'OK'
), (
    'unified_rule_id',
    'call-taxi-unified',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru'],
    NULL,
    'waiting_benefits',
    'OK'
), (
    'cargo_rule_id',
    'cargo-callcenter',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru'],
    NULL,
    'waiting_benefits',
    'OK'
), (
    'vezet_rule_id',
    'call-taxi-vezet',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru'],
    NULL,
    'waiting_benefits',
    'OK'
);

INSERT INTO piecework.calculation_result(
  calculation_result_id, tariff_type, calculation_rule_id, start_date,
  stop_date, login, detail, daytime_cost, night_cost,
  holidays_daytime_cost, holidays_night_cost, benefits,
  newbie_daytime_cost, newbie_night_cost, newbie_holidays_daytime_cost,
  newbie_holidays_night_cost, conversion, conversion_benefits,
  conversion_benefits_weight, qa_ratio, calc_type, calc_subtype,
  benefit_conditions
) VALUES (
  'result_id_1', 'call-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanov', '{}', 7.0, 2.0, 5.0, 0.0,
  NULL, 4.0, 3.0, 2.0, 2.0, 0.6, 5.0, NULL, NULL, 'general', 'call-taxi',
  (
    '{"qa_ratio": 0.92, "min_qa_ratio": 0.88, "cargo_calls": 13, ' ||
    '"claim_ratio": 1.0, "cargo_benefits": 52, "corporate_calls": 25, ' ||
    '"discipline_ratio": 1.0, "corporate_benefits": 75, ' ||
    '"newbie_cargo_calls": 0, "newbie_cargo_benefits": 0, ' ||
    '"newbie_corporate_calls": 0, "newbie_corporate_benefits": 0}'
  )::JSONB
), (
  'result_id_2', 'call-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanov', '{}', 0.0, 0.0, 0.0, 0.0,
  8.0, NULL, NULL, NULL, NULL, 0.6, 10.0, 0.8, NULL, 'correction',
  'call-taxi-conversion', NULL
), (
  'result_id_3', 'call-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrov', '{}', 15.0, 7.0, 10.0, 0.0,
  NULL, 0.0, 0.0, 0.0, 0.0, 0.7, 7.5, NULL, NULL, 'general', 'call-taxi',
  (
    '{"qa_ratio": 0.72, "min_qa_ratio": 0.88, "cargo_calls": 22, ' ||
    '"claim_ratio": 1.0, "cargo_benefits": 88, "corporate_calls": 5, ' ||
    '"discipline_ratio": 1.0, "corporate_benefits": 15, ' ||
    '"newbie_cargo_calls": 22, "newbie_cargo_benefits": 88, ' ||
    '"newbie_corporate_calls": 5, ' ||
    '"newbie_corporate_benefits": 15}'
  )::JSONB
), (
  'result_id_4', 'call-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrov', '{}', 0.0, 0.0, 0.0, 0.0,
  3.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'correction', 'final',
  NULL
), (
  'result_id_5', 'call-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'smirnoff', '{}', 0.0, 0.0, 0.0, 0.0,
  NULL, 0.0, 0.0, 0.0, 0.0, 0.8, 1.5, NULL, NULL, 'general', 'call-taxi',
  (
    '{"qa_ratio": 0.95, "min_qa_ratio": 0.88, "cargo_calls": 22, ' ||
    '"claim_ratio": 1.0, "cargo_benefits": 88, "corporate_calls": 5, ' ||
    '"discipline_ratio": 1.0, "corporate_benefits": 15, ' ||
    '"newbie_cargo_calls": 22, "newbie_cargo_benefits": 88, ' ||
    '"newbie_corporate_calls": 5, "newbie_corporate_benefits": 15}'
  )::JSONB
), (
  'result_id_6', 'call-taxi', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'smirnoff', '{}', 0.0, 0.0, 0.0, 0.0,
  11.7, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0.9, 'correction',
  'call-taxi-qa', NULL
), (
  'result_id_7', 'call-taxi-unified', 'unified_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanova', '{}', 7.0, 2.0, 5.0, 0.0,
  NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'general', 'call-taxi',
  (
    '{' ||
     '"unified_qa_ratio": 0.8, "discipline_ratio": 0.7, ' ||
     '"workshifts_duration_sec": 3600, ' ||
     '"plan_workshifts_duration_sec": 7200, ' ||
     '"unified_qa_rating_weight": 0.8, ' ||
     '"discipline_rating_weight": 0.1, ' ||
     '"hour_cost_rating_weight": 0.1, ' ||
     '"min_workshifts_ratio": 0.25, ' ||
     '"min_hour_cost": 10.0, ' ||
     '"benefit_thresholds_strict": [' ||
      '{"threshold": 0, "value": 0.5}, ' ||
      '{"threshold": 80, "value": 0.0}' ||
     ']' ||
    '}'
  )::JSONB
), (
  'result_id_8', 'call-taxi-unified', 'unified_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanova', '{}', 0.0, 0.0, 0.0, 0.0,
  8.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'correction',
  'intermediate', NULL
), (
  'result_id_9', 'call-taxi-unified', 'unified_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrova', '{}', 15.0, 7.0, 10.0, 0.0,
  NULL, 0.0, 0.0, 0.0, 0.0, 0.7, 7.5, NULL, NULL, 'general', 'call-taxi',
  (
    '{' ||
     '"unified_qa_ratio": 0.9, "discipline_ratio": 0.6, ' ||
     '"workshifts_duration_sec": 7200, ' ||
     '"plan_workshifts_duration_sec": 7200, ' ||
     '"unified_qa_rating_weight": 0.8, ' ||
     '"discipline_rating_weight": 0.1, ' ||
     '"hour_cost_rating_weight": 0.1, ' ||
     '"min_workshifts_ratio": 0.25, ' ||
     '"min_hour_cost": 10.0, ' ||
     '"benefit_thresholds_strict": [' ||
      '{"threshold": 0, "value": 0.5}, ' ||
      '{"threshold": 80, "value": 0.0}' ||
     ']' ||
    '}'
  )::JSONB
), (
  'result_id_10', 'call-taxi-unified', 'unified_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrova', '{}', 0.0, 0.0, 0.0, 0.0,
  3.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'correction', 'final',
  NULL
), (
  'result_id_11', 'call-taxi-unified', 'unified_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'smirnova', '{}', 0.0, 0.0, 0.0, 0.0,
  NULL, 0.0, 0.0, 0.0, 0.0, 0.8, 1.5, NULL, NULL, 'general', 'call-taxi',
  (
    '{' ||
     '"unified_qa_ratio": 0.7, "discipline_ratio": 0.8, ' ||
     '"workshifts_duration_sec": 100, ' ||
     '"plan_workshifts_duration_sec": 7200, ' ||
     '"unified_qa_rating_weight": 0.8, ' ||
     '"discipline_rating_weight": 0.1, ' ||
     '"hour_cost_rating_weight": 0.1, ' ||
     '"min_workshifts_ratio": 0.25, ' ||
     '"min_hour_cost": 10.0, ' ||
     '"benefit_thresholds_strict": [' ||
      '{"threshold": 0, "value": 0.5}, ' ||
      '{"threshold": 80, "value": 0.0}' ||
     ']' ||
    '}'
  )::JSONB
), (
  'result_id_12', 'call-taxi-unified', 'unified_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'popova', '{}', 0.0, 0.0, 0.0, 0.0,
  NULL, 0.0, 0.0, 0.0, 0.0, 0.8, 1.5, NULL, NULL, 'general', 'call-taxi',
  (
    '{' ||
     '"unified_qa_ratio": 0.7, "discipline_ratio": 0.8, ' ||
     '"workshifts_duration_sec": 0, ' ||
     '"plan_workshifts_duration_sec": 7200, ' ||
     '"unified_qa_rating_weight": 0.8, ' ||
     '"discipline_rating_weight": 0.1, ' ||
     '"hour_cost_rating_weight": 0.1, ' ||
     '"min_workshifts_ratio": 0.25, ' ||
     '"min_hour_cost": 10.0, ' ||
     '"benefit_thresholds_strict": [' ||
      '{"threshold": 0, "value": 0.5}, ' ||
      '{"threshold": 80, "value": 0.0}' ||
     ']' ||
    '}'
  )::JSONB
), (
  'result_id_13', 'call-taxi-vezet', 'vezet_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanov', '{}', 7.0, 2.0, 5.0, 0.0,
  NULL, 4.0, 3.0, 2.0, 2.0, 0.6, 5.0, NULL, NULL, 'general', 'call-taxi',
  (
    '{"qa_ratio": 0.92, "min_qa_ratio": 0.88, "cargo_calls": 13, ' ||
    '"claim_ratio": 1.0, "cargo_benefits": 52, "corporate_calls": 25, ' ||
    '"discipline_ratio": 1.0, "corporate_benefits": 75, ' ||
    '"newbie_cargo_calls": 0, "newbie_cargo_benefits": 0, ' ||
    '"newbie_corporate_calls": 0, "newbie_corporate_benefits": 0, ' ||
    '"max_benefits": 100}'
  )::JSONB
), (
  'result_id_14', 'call-taxi-vezet', 'vezet_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrov', '{}', 15.0, 7.0, 10.0, 0.0,
  NULL, 0.0, 0.0, 0.0, 0.0, 0.7, 7.5, NULL, NULL, 'general', 'call-taxi',
  (
    '{"qa_ratio": 0.72, "min_qa_ratio": 0.88, "cargo_calls": 22, ' ||
    '"claim_ratio": 1.0, "cargo_benefits": 88, "corporate_calls": 5, ' ||
    '"discipline_ratio": 1.0, "corporate_benefits": 15, ' ||
    '"newbie_cargo_calls": 22, "newbie_cargo_benefits": 88, ' ||
    '"newbie_corporate_calls": 5, ' ||
    '"newbie_corporate_benefits": 15, "max_benefits": 150}'
  )::JSONB
), (
  'result_id_15', 'call-taxi-vezet', 'vezet_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'smirnoff', '{}', 0.0, 0.0, 0.0, 0.0,
  NULL, 0.0, 0.0, 0.0, 0.0, 0.8, 1.5, NULL, NULL, 'general', 'call-taxi',
  (
    '{"qa_ratio": 0.95, "min_qa_ratio": 0.88, "cargo_calls": 22, ' ||
    '"claim_ratio": 1.0, "cargo_benefits": 88, "corporate_calls": 5, ' ||
    '"discipline_ratio": 1.0, "corporate_benefits": 15, ' ||
    '"newbie_cargo_calls": 22, "newbie_cargo_benefits": 88, ' ||
    '"newbie_corporate_calls": 5, "newbie_corporate_benefits": 15, ' ||
    '"max_benefits": 80}'
  )::JSONB
), (
  'result_id_16', 'cargo-callcenter', 'cargo_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanova', '{}', 7.0, 2.0, 5.0, 0.0,
  NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'general', 'call-taxi',
  (
    '{' ||
     '"unified_qa_ratio": 0.8, "discipline_ratio": 0.7, ' ||
     '"workshifts_duration_sec": 3600, ' ||
     '"plan_workshifts_duration_sec": 7200, ' ||
     '"unified_qa_rating_weight": 0.8, ' ||
     '"discipline_rating_weight": 0.1, ' ||
     '"hour_cost_rating_weight": 0.1, ' ||
     '"min_workshifts_ratio": 0.25, ' ||
     '"min_hour_cost": 10.0, ' ||
     '"benefit_thresholds_strict": [' ||
      '{"threshold": 0, "value": 0.5}, ' ||
      '{"threshold": 80, "value": 0.0}' ||
     ']' ||
    '}'
  )::JSONB
), (
  'result_id_17', 'cargo-callcenter', 'cargo_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanova', '{}', 0.0, 0.0, 0.0, 0.0,
  8.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'correction',
  'intermediate', NULL
), (
  'result_id_18', 'cargo-callcenter', 'cargo_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrova', '{}', 15.0, 7.0, 10.0, 0.0,
  NULL, 0.0, 0.0, 0.0, 0.0, 0.7, 7.5, NULL, NULL, 'general', 'call-taxi',
  (
    '{' ||
     '"unified_qa_ratio": 0.9, "discipline_ratio": 0.6, ' ||
     '"workshifts_duration_sec": 7200, ' ||
     '"plan_workshifts_duration_sec": 7200, ' ||
     '"unified_qa_rating_weight": 0.8, ' ||
     '"discipline_rating_weight": 0.1, ' ||
     '"hour_cost_rating_weight": 0.1, ' ||
     '"min_workshifts_ratio": 0.25, ' ||
     '"min_hour_cost": 10.0, ' ||
     '"benefit_thresholds_strict": [' ||
      '{"threshold": 0, "value": 0.5}, ' ||
      '{"threshold": 80, "value": 0.0}' ||
     ']' ||
    '}'
  )::JSONB
), (
  'result_id_19', 'cargo-callcenter', 'cargo_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrova', '{}', 0.0, 0.0, 0.0, 0.0,
  3.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'correction', 'final',
  NULL
), (
  'result_id_20', 'cargo-callcenter', 'cargo_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'smirnova', '{}', 0.0, 0.0, 0.0, 0.0,
  NULL, 0.0, 0.0, 0.0, 0.0, 0.8, 1.5, NULL, NULL, 'general', 'call-taxi',
  (
    '{' ||
     '"unified_qa_ratio": 0.7, "discipline_ratio": 0.8, ' ||
     '"workshifts_duration_sec": 100, ' ||
     '"plan_workshifts_duration_sec": 7200, ' ||
     '"unified_qa_rating_weight": 0.8, ' ||
     '"discipline_rating_weight": 0.1, ' ||
     '"hour_cost_rating_weight": 0.1, ' ||
     '"min_workshifts_ratio": 0.25, ' ||
     '"min_hour_cost": 10.0, ' ||
     '"benefit_thresholds_strict": [' ||
      '{"threshold": 0, "value": 0.5}, ' ||
      '{"threshold": 80, "value": 0.0}' ||
     ']' ||
    '}'
  )::JSONB
);

INSERT INTO piecework.payment_draft (
  payment_draft_id, tariff_type, calculation_rule_id, country, start_date,
  stop_date, status, approvals_id
) VALUES (
  'some_draft_id', 'call-taxi', 'some_rule_id', 'ru', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'failed', 123
), (
  'corrected_draft_id', 'call-taxi', 'corrected_rule_id', 'ru',
  '2020-01-01'::DATE, '2020-01-16'::DATE, 'need_approval', NULL
);

INSERT INTO piecework.agent_employee(
  agent_employee_id,
  tariff_type,
  start_date,
  stop_date,
  country,
  login,
  branch
) VALUES (
    'employee1',
    'call-taxi-unified',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'ivanova',
    'first'
), (
    'employee2',
    'call-taxi-unified',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'petrova',
    'first'
), (
    'employee3',
    'call-taxi-unified',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'smirnova',
    'first'
), (
    'employee4',
    'call-taxi-unified',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'popova',
    'first'
), (
    'employee5',
    'cargo-callcenter',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'ivanova',
    'first'
), (
    'employee6',
    'cargo-callcenter',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'petrova',
    'first'
), (
    'employee7',
    'cargo-callcenter',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    'ru',
    'smirnova',
    'first'
);
