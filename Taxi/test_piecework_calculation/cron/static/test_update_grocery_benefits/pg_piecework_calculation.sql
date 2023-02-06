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
  'grocery',
  '2020-01-01'::DATE,
  '2020-01-16'::DATE,
  'ivanov',
  'rus',
  'general'
), (
  'ivanova_id',
  'grocery',
  '2020-01-01'::DATE,
  '2020-01-16'::DATE,
  'ivanova',
  'rus',
  's_general'
), (
  'petrova_id',
  'grocery',
  '2020-01-01'::DATE,
  '2020-01-16'::DATE,
  'petrova',
  'blr',
  's_general'
), (
  'smirnoffa_id',
  'grocery',
  '2020-01-01'::DATE,
  '2020-01-16'::DATE,
  'smirnoffa',
  'rus',
  's_general'
), (
  'petrov_id',
  'grocery',
  '2020-01-01'::DATE,
  '2020-01-16'::DATE,
  'petrov',
  'blr',
  'general'
), (
  'smirnoff_id',
  'grocery',
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
    'grocery',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['rus', 'blr'],
    NULL,
    'waiting_benefits',
    'OK'
), (
    'corrected_rule_id',
    'grocery',
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
  'result_id_1', 'grocery', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanov', 7.0, 2.0, 5.0, 0.0,
  NULL,
  (
      '{' ||
       '"min_csat_ratio": 70,' ||
       '"min_qa_ratio": 80,' ||
       '"min_hour_cost": 1.0, "workshifts_duration_sec": 36000.0, ' ||
       '"plan_workshifts_duration_sec": 36000.0, "min_workshifts_ratio": 0.25, ' ||
       '"rating_factor": 1.0, "rating_max_total_cost": 30.0, ' ||
       '"csat_ratio": 90.0, "qa_ratio": 85.0, ' ||
       '"rating_total_cost_weight": 1.0, ' ||
       '"rating_csat_weight": 1.0, "rating_qa_weight": 1.0, ' ||
       '"benefit_thresholds_strict": [' ||
        '{"threshold": 0, "value": 0.5}, ' ||
        '{"threshold": 80, "value": 0.0}' ||
       '], ' ||
       '"avg_duration": 10.0, ' ||
       '"rating_avg_duration_weight": 1.0' ||
      '}'
  )::JSONB,
  'general', 'chatterbox'
), (
  'result_id_2', 'grocery', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanov', 3.0, 3.0, 3.0, 0.0,
  NULL, NULL, 'correction', 'intermediate'
), (
  'result_id_3', 'grocery', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrov', 15.0, 7.0, 10.0, 0.0,
  NULL,
  (
      '{' ||
       '"min_csat_ratio": 70,' ||
       '"min_qa_ratio": 80,' ||
       '"min_hour_cost": 1.0, "workshifts_duration_sec": 28800.0, ' ||
       '"plan_workshifts_duration_sec": 36000.0, "min_workshifts_ratio": 0.25, ' ||
       '"rating_factor": 2.0, "rating_max_total_cost": 30.0, ' ||
       '"csat_ratio": 95.0, "qa_ratio": 80.0, ' ||
       '"rating_total_cost_weight": 1.0, ' ||
       '"rating_csat_weight": 1.0, "rating_qa_weight": 1.0, ' ||
       '"benefit_thresholds_strict": [' ||
        '{"threshold": 0, "value": 0.5}, ' ||
        '{"threshold": 80, "value": 0.0}' ||
       '], ' ||
       '"rating_avg_duration_weight": 0.0' ||
      '}'
  )::JSONB,
  'general', 'chatterbox'
), (
  'result_id_33', 'grocery', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrova', 15.0, 7.0, 10.0, 0.0,
  NULL,
  (
      '{' ||
       '"min_csat_ratio": 70,' ||
       '"min_qa_ratio": 80,' ||
       '"min_hour_cost": 1.0, "workshifts_duration_sec": 28800.0, ' ||
       '"plan_workshifts_duration_sec": 36000.0, "min_workshifts_ratio": 0.25, ' ||
       '"rating_factor": 2.0, "rating_max_total_cost": 30.0, ' ||
       '"csat_ratio": 95.0, "qa_ratio": 79.0, ' ||
       '"rating_total_cost_weight": 1.0, ' ||
       '"rating_csat_weight": 1.0, "rating_qa_weight": 1.0, ' ||
       '"benefit_thresholds_strict": [' ||
        '{"threshold": 0, "value": 0.5}, ' ||
        '{"threshold": 60, "value": 0.0}' ||
       '], ' ||
       '"rating_avg_duration_weight": 0.0' ||
      '}'
  )::JSONB,
  'general', 'chatterbox'
), (
  'result_id_333', 'grocery', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ivanova', 15.0, 7.0, 10.0, 0.0,
  NULL,
  (
      '{' ||
       '"min_csat_ratio": 70,' ||
       '"min_qa_ratio": 80,' ||
       '"min_hour_cost": 1.0, "workshifts_duration_sec": 28800.0, ' ||
       '"plan_workshifts_duration_sec": 36000.0, "min_workshifts_ratio": 0.25, ' ||
       '"rating_factor": 2.0, "rating_max_total_cost": 30.0, ' ||
       '"csat_ratio": 69.0, "qa_ratio": 85.0, ' ||
       '"rating_total_cost_weight": 1.0, ' ||
       '"rating_csat_weight": 1.0, "rating_qa_weight": 1.0, ' ||
       '"benefit_thresholds_strict": [' ||
        '{"threshold": 0, "value": 0.5}, ' ||
        '{"threshold": 60, "value": 0.0}' ||
       '], ' ||
       '"rating_avg_duration_weight": 0.0' ||
      '}'
  )::JSONB,
  'general', 'chatterbox'
), (
  'result_id_4', 'grocery', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'petrov', 0.0, 3.0, 3.0, 3.0,
  3.0, NULL, 'correction', 'final'
), (
  'result_id_55', 'grocery', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'smirnoffa', 1.0, 10.0, 10.0, 10.0,
  NULL,
    (
      '{' ||
       '"min_csat_ratio": 70,' ||
       '"min_qa_ratio": 80,' ||
       '"min_hour_cost": 1.0, "workshifts_duration_sec": 7200.0, ' ||
       '"plan_workshifts_duration_sec": 36000.0, "min_workshifts_ratio": 0.25, ' ||
       '"rating_factor": 1.0, "rating_max_total_cost": 100.0, ' ||
       '"csat_ratio": 85.0, "qa_ratio": 90.0, ' ||
       '"rating_total_cost_weight": 1.0, ' ||
       '"rating_csat_weight": 1.0, "rating_qa_weight": 1.0, ' ||
       '"benefit_thresholds_strict": [' ||
        '{"threshold": 0, "value": 0.5}, ' ||
        '{"threshold": 60, "value": 0.0}' ||
       '], ' ||
       '"rating_avg_duration_weight": 0.0' ||
      '}'
  )::JSONB,
  'general', 'chatterbox'
), (
  'result_id_5', 'grocery', 'some_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'smirnoff', 0.0, 0.0, 0.0, 0.0,
  NULL,
    (
      '{' ||
       '"min_csat_ratio": 70,' ||
       '"min_qa_ratio": 80,' ||
       '"min_hour_cost": 1.0, "workshifts_duration_sec": 7200.0, ' ||
       '"plan_workshifts_duration_sec": 36000.0, "min_workshifts_ratio": 0.25, ' ||
       '"rating_factor": 1.0, "rating_max_total_cost": 100.0, ' ||
       '"csat_ratio": 85.0, "qa_ratio": 90.0, ' ||
       '"rating_total_cost_weight": 1.0, ' ||
       '"rating_csat_weight": 1.0, "rating_qa_weight": 1.0, ' ||
       '"benefit_thresholds_strict": [' ||
        '{"threshold": 0, "value": 0.5}, ' ||
        '{"threshold": 80, "value": 0.0}' ||
       '], ' ||
       '"rating_avg_duration_weight": 0.0' ||
      '}'
  )::JSONB,
  'general', 'chatterbox'
);

INSERT INTO piecework.payment_draft (
  payment_draft_id, tariff_type, calculation_rule_id, country, start_date,
  stop_date, status, approvals_id
) VALUES (
  'some_draft_id', 'grocery', 'some_rule_id', 'rus', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'failed', 123
), (
  'corrected_draft_id', 'grocery', 'corrected_rule_id', 'rus',
  '2020-01-01'::DATE, '2020-01-16'::DATE, 'updating', 1
);
