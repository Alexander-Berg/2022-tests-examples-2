CREATE SCHEMA IF NOT EXISTS "taxi_rep_callcenter";
DROP TABLE IF EXISTS taxi_rep_callcenter.rep_operator_activity_daily;
CREATE TABLE taxi_rep_callcenter.rep_operator_activity_daily (
    rep_operator_activity_daily_id VARCHAR PRIMARY KEY,
    staff_login VARCHAR NOT NULL,
    daytime_weekday_disp_order_cnt INT NOT NULL,
    nighttime_weekday_disp_order_cnt INT NOT NULL,
    daytime_holiday_disp_order_cnt INT NOT NULL,
    nighttime_holiday_disp_order_cnt INT NOT NULL,
    daytime_weekday_cargo_order_cnt INT NOT NULL,
    nighttime_weekday_cargo_order_cnt INT NOT NULL,
    daytime_holiday_cargo_order_cnt INT NOT NULL,
    nighttime_holiday_cargo_order_cnt INT NOT NULL,
    daytime_weekday_corp_order_cnt INT NOT NULL,
    nighttime_weekday_corp_order_cnt INT NOT NULL,
    daytime_holiday_corp_order_cnt INT NOT NULL,
    nighttime_holiday_corp_order_cnt INT NOT NULL,
    daytime_weekday_econom_order_cnt INT NOT NULL,
    nighttime_weekday_econom_order_cnt INT NOT NULL,
    daytime_holiday_econom_order_cnt INT NOT NULL,
    nighttime_holiday_econom_order_cnt INT NOT NULL,
    daytime_weekday_cargo_call_cnt INT NOT NULL,
    nighttime_weekday_cargo_call_cnt INT NOT NULL,
    daytime_holiday_cargo_call_cnt INT NOT NULL,
    nighttime_holiday_cargo_call_cnt INT NOT NULL,
    daytime_weekday_corp_call_cnt INT NOT NULL,
    nighttime_weekday_corp_call_cnt INT NOT NULL,
    daytime_holiday_corp_call_cnt INT NOT NULL,
    nighttime_holiday_corp_call_cnt INT NOT NULL,
    daytime_weekday_econom_call_cnt INT NOT NULL,
    nighttime_weekday_econom_call_cnt INT NOT NULL,
    daytime_holiday_econom_call_cnt INT NOT NULL,
    nighttime_holiday_econom_call_cnt INT NOT NULL,
    converted_disp_call_cnt INT NOT NULL,
    completed_disp_call_cnt INT NOT NULL,
    corporate_call_cnt INT NOT NULL,
    cargo_call_cnt INT NOT NULL,
    quality_coeff_consultation_cnt INT NOT NULL,
    quality_coeff_consultation_sum NUMERIC NOT NULL,
    quality_coeff_order_placing_cnt INT NOT NULL,
    quality_coeff_order_placing_sum NUMERIC NOT NULL,
    claim_cnt INT NOT NULL,
    abcense_cnt INT NOT NULL,
    delay_cnt INT NOT NULL,
    operator_short_shift_flg BOOLEAN NOT NULL,
    quality_shift_coeff_cnt INT NOT NULL,
    fact_perfomance_sec INT,
    newbie_flg INT NOT NULL,
    lcl_report_dt DATE NOT NULL,
    daytime_weekday_disp_success_order_cnt INT NOT NULL,
    nighttime_weekday_disp_success_order_cnt INT NOT NULL,
    daytime_holiday_disp_success_order_cnt INT NOT NULL,
    nighttime_holiday_disp_success_order_cnt INT NOT NULL
);

DROP TABLE IF EXISTS taxi_rep_callcenter.rep_operator_line_activity;
CREATE TABLE taxi_rep_callcenter.rep_operator_line_activity (
    rep_operator_line_activity_id VARCHAR PRIMARY KEY,
    staff_login VARCHAR NOT NULL,
    lcl_report_dt DATE NOT NULL,
    meta_queue_code VARCHAR,
    daytime_weekday_order_cnt INT NOT NULL,
    nighttime_weekday_order_cnt INT NOT NULL,
    daytime_holiday_order_cnt INT NOT NULL,
    nighttime_holiday_order_cnt INT NOT NULL,
    daytime_weekday_converted_order_cnt INT NOT NULL,
    nighttime_weekday_converted_order_cnt INT NOT NULL,
    daytime_holiday_converted_order_cnt INT NOT NULL,
    nighttime_holiday_converted_order_cnt INT NOT NULL,
    daytime_weekday_created_order_cnt INT NOT NULL,
    nighttime_weekday_created_order_cnt INT NOT NULL,
    daytime_holiday_created_order_cnt INT NOT NULL,
    nighttime_holiday_created_order_cnt INT NOT NULL,
    daytime_weekday_call_cnt INT NOT NULL,
    nighttime_weekday_call_cnt INT NOT NULL,
    daytime_holiday_call_cnt INT NOT NULL,
    nighttime_holiday_call_cnt INT NOT NULL
);

CREATE SCHEMA IF NOT EXISTS "taxi_cdm_callcenter";
DROP TABLE IF EXISTS taxi_cdm_callcenter.fct_operator_standart_performance;
CREATE TABLE taxi_cdm_callcenter.fct_operator_standart_performance (
    fct_operator_standart_perfomance_id VARCHAR PRIMARY KEY,
    staff_login VARCHAR NOT NULL,
    utc_actual_dttm DATE NOT NULL,
    standart_performance_value INT NOT NULL
);

INSERT INTO taxi_rep_callcenter.rep_operator_activity_daily VALUES (
    'rec4', 'ivanova', 10, 4, 2, 1, 10, 4, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0,
    10, 4, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 17, 20, 15, 5,
    1, 32, 3, 62, 3, 0, 2, True, 5, 3600, 0, '2021-01-05',
    0, 0, 0, 1
), (
    'rec5', 'ivanova', 6, 0, 4, 3, 0, 0, 0, 0, 8, 0, 4, 3, 0, 0, 0, 0,
    0, 0, 0, 0, 8, 0, 4, 3, 0, 0, 0, 0, 15, 18, 10, 8,
    3, 93, 1, 32, 1, 0, 1, True, 3, 7200, 0, '2021-01-07',
    0, 1, 0, 0
), (
    'rec6', 'petrova', 12, 0, 5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 12, 1, 5, 6,
    0, 0, 0, 0, 0, 0, 0, 0, 12, 1, 5, 6, 24, 27, 5, 22,
    2, 32, 3, 92, 10, 2, 1, False, 5, 7200, 1, '2021-01-06',
    1, 0, 0, 0
), (
    'rec7', 'popova', 12, 1, 5, 6, 0, 0, 0, 0, 0, 0, 0, 0, 12, 1, 5, 6,
    0, 0, 0, 0, 0, 0, 0, 0, 12, 1, 5, 6, 24, 27, 5, 22,
    2, 32, 3, 92, 10, 2, 1, False, 5, 7200, 1, '2021-01-06',
    0, 0, 0, 0
);

INSERT INTO taxi_rep_callcenter.rep_operator_line_activity VALUES (
    'rec1', 'ivanova', '2021-01-05', 'cargo', 10, 4, 2, 1, 10, 4, 2, 1, 10, 4, 2, 1, 10, 4, 2, 1
), (
    'rec2', 'ivanova', '2021-01-05', 'calltaxi_common', 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1
), (
    'rec3', 'ivanova', '2021-01-07', 'corp', 8, 0, 4, 3, 8, 0, 4, 3, 8, 0, 4, 3, 8, 0, 4, 3
), (
    'rec4', 'ivanova', '2021-01-07', 'calltaxi_common', 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0
), (
    'rec5', 'petrova', '2021-01-06', 'econom', 12, 1, 5, 6, 12, 1, 5, 6, 12, 1, 5, 6, 12, 1, 5, 6
), (
    'rec6', 'petrova', '2021-01-06', 'calltaxi_common', 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0
), (
    'rec7', 'popova', '2021-01-06', 'econom', 12, 1, 5, 6, 12, 1, 5, 6, 12, 1, 5, 6, 12, 1, 5, 6
);

INSERT INTO taxi_cdm_callcenter.fct_operator_standart_performance(
  fct_operator_standart_perfomance_id,
  staff_login,
  utc_actual_dttm,
  standart_performance_value
) VALUES (
    'rec1', 'ivanova', '2021-01-01', 28800
), (
    'rec2', 'petrova', '2021-01-01', 14400
), (
    'rec3', 'smirnova', '2021-01-01', 14400
), (
    'rec4', 'popova', '2021-01-01', 14400
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
    rule_type
) VALUES (
    'unified_rule_id',
    'call-taxi-unified',
    '2021-01-01'::DATE,
    '2021-01-16'::DATE,
    True,
    ARRAY['ru'],
    NULL,
    'waiting_agent',
    'regular'
), (
    'cargo_rule_id',
    'cargo-callcenter',
    '2021-01-01'::DATE,
    '2021-01-16'::DATE,
    True,
    ARRAY['ru'],
    NULL,
    'waiting_agent',
    'regular'
), (
    'dismissal_cargo_rule_id',
    'cargo-callcenter',
    '2021-01-01'::DATE,
    '2021-01-01'::DATE,
    True,
    ARRAY['ru'],
    ARRAY['ivanova', 'petrova', 'smirnova'],
    'waiting_agent',
    'dismissal'
);

INSERT INTO piecework.tariff(
  tariff_id,
  tariff_type,
  cost_conditions,
  benefit_conditions,
  countries,
  calc_night,
  calc_holidays,
  calc_workshifts,
  start_date,
  stop_date,
  daytime_begins,
  daytime_ends
)
VALUES (
  'unified_tariff_id',
  'call-taxi-unified',
  ('{' ||
    '"rules": [' ||
     '{' ||
      '"type": "calltaxi_aggregate", ' ||
      '"branch": "first", ' ||
      '"line": "cargo", ' ||
      '"bo_per_order": 5.0, ' ||
      '"bo_per_call": 0.01 ' ||
     '}, ' ||
     '{' ||
      '"type": "calltaxi_aggregate", ' ||
      '"branch": "first", ' ||
      '"line": "corp", ' ||
      '"bo_per_order": 5.0, ' ||
      '"bo_per_call": 0.01 ' ||
     '}, ' ||
     '{' ||
      '"type": "calltaxi_aggregate", ' ||
      '"branch": "second", ' ||
      '"line": "econom", ' ||
      '"bo_per_order": 3.0, ' ||
      '"bo_per_call": 0.01 ' ||
     '}, ' ||
     '{' ||
      '"type": "calltaxi_aggregate", ' ||
      '"branch": "first", ' ||
      '"bo_per_order": 4.0, ' ||
      '"bo_per_call": 0.01 ' ||
     '}, ' ||
     '{' ||
      '"type": "calltaxi_aggregate", ' ||
      '"branch": "second", ' ||
      '"bo_per_order": 2.0, ' ||
      '"bo_per_call": 0.01 ' ||
     '} ' ||
    ']' ||
   '}')::JSONB,
  ('{' ||
    '"claim_ratios": [' ||
     '{"threshold": 0, "value": 1.0}, ' ||
     '{"threshold": 1, "value": 0.9}, ' ||
     '{"threshold": 2, "value": 0.8}, ' ||
     '{"threshold": 3, "value": 0.7}, ' ||
     '{"threshold": 4, "value": 0.6}, ' ||
     '{"threshold": 5, "value": 0.5}, ' ||
     '{"threshold": 6, "value": 0.4}, ' ||
     '{"threshold": 7, "value": 0.3}, ' ||
     '{"threshold": 8, "value": 0.2}, ' ||
     '{"threshold": 9, "value": 0.1}, ' ||
     '{"threshold": 10, "value": 0.0}' ||
    '],' ||
    '"delay_ratios": [' ||
     '{"threshold": 0, "value": 1.0}, ' ||
     '{"threshold": 1, "value": 0.9}, ' ||
     '{"threshold": 2, "value": 0.8}, ' ||
     '{"threshold": 3, "value": 0.7}, ' ||
     '{"threshold": 4, "value": 0.6}, ' ||
     '{"threshold": 5, "value": 0.5}, ' ||
     '{"threshold": 6, "value": 0.4}, ' ||
     '{"threshold": 7, "value": 0.3}, ' ||
     '{"threshold": 8, "value": 0.2}, ' ||
     '{"threshold": 9, "value": 0.1}, ' ||
     '{"threshold": 10, "value": 0.0}' ||
    '],' ||
    '"abcense_ratios": [' ||
     '{"threshold": 0, "value": 1.0}, ' ||
     '{"threshold": 1, "value": 0.8}, ' ||
     '{"threshold": 2, "value": 0.6}, ' ||
     '{"threshold": 3, "value": 0.4}, ' ||
     '{"threshold": 4, "value": 0.2}, ' ||
     '{"threshold": 5, "value": 0.0}' ||
    '],' ||
    '"min_shifts_cnt": 4, ' ||
    '"min_short_shifts_cnt": 6, ' ||
    '"qa_unified_qa_weight": 0.6, ' ||
    '"claim_unified_qa_weight": 0.4, ' ||
    '"abcense_discipline_weight": 0.5, ' ||
    '"delay_discipline_weight": 0.5, ' ||
    '"unified_qa_rating_weight": 0.8, ' ||
    '"discipline_rating_weight": 0.1, ' ||
    '"hour_cost_rating_weight": 0.1, ' ||
    '"min_workshifts_ratio": 0.25, ' ||
    '"min_hour_cost": 10.0, ' ||
    '"benefit_thresholds_strict": [' ||
     '{"threshold": 0, "value": 0.5}, ' ||
     '{"threshold": 80, "value": 0.0}' ||
    ']' ||
   '}')::JSONB,
  ARRAY['ru'],
  True,
  True,
  True,
  '2019-12-01'::DATE,
  'infinity',
  '08:00'::TIME,
  '20:00'::TIME
), (
  'cargo_tariff_id',
  'cargo-callcenter',
  ('{' ||
    '"rules": [' ||
     '{' ||
      '"key": "calltaxi_order_first_cargo", ' ||
      '"type": "created_order", ' ||
      '"branch": "first", ' ||
      '"line": "cargo", ' ||
      '"cost": 5.0 ' ||
     '}, ' ||
     '{' ||
      '"key": "calltaxi_order_first_corp", ' ||
      '"type": "created_order", ' ||
      '"branch": "first", ' ||
      '"line": "corp", ' ||
      '"cost": 5.0 ' ||
     '}, ' ||
     '{' ||
      '"key": "calltaxi_order_second_econom", ' ||
      '"type": "created_order", ' ||
      '"branch": "second", ' ||
      '"line": "econom", ' ||
      '"cost": 3.0 ' ||
     '}, ' ||
     '{' ||
      '"key": "calltaxi_order_first", ' ||
      '"type": "created_order", ' ||
      '"branch": "first", ' ||
      '"cost": 4.0 ' ||
     '}, ' ||
     '{' ||
      '"key": "calltaxi_order_second", ' ||
      '"type": "created_order", ' ||
      '"branch": "second", ' ||
      '"cost": 2.0 ' ||
     '}, ' ||
     '{' ||
      '"key": "calltaxi_call", ' ||
      '"type": "call", ' ||
      '"cost": 0.01 ' ||
     '} ' ||
    ']' ||
   '}')::JSONB,
  ('{' ||
    '"claim_ratios": [' ||
     '{"threshold": 0, "value": 1.0}, ' ||
     '{"threshold": 1, "value": 0.9}, ' ||
     '{"threshold": 2, "value": 0.8}, ' ||
     '{"threshold": 3, "value": 0.7}, ' ||
     '{"threshold": 4, "value": 0.6}, ' ||
     '{"threshold": 5, "value": 0.5}, ' ||
     '{"threshold": 6, "value": 0.4}, ' ||
     '{"threshold": 7, "value": 0.3}, ' ||
     '{"threshold": 8, "value": 0.2}, ' ||
     '{"threshold": 9, "value": 0.1}, ' ||
     '{"threshold": 10, "value": 0.0}' ||
    '],' ||
    '"delay_ratios": [' ||
     '{"threshold": 0, "value": 1.0}, ' ||
     '{"threshold": 1, "value": 0.9}, ' ||
     '{"threshold": 2, "value": 0.8}, ' ||
     '{"threshold": 3, "value": 0.7}, ' ||
     '{"threshold": 4, "value": 0.6}, ' ||
     '{"threshold": 5, "value": 0.5}, ' ||
     '{"threshold": 6, "value": 0.4}, ' ||
     '{"threshold": 7, "value": 0.3}, ' ||
     '{"threshold": 8, "value": 0.2}, ' ||
     '{"threshold": 9, "value": 0.1}, ' ||
     '{"threshold": 10, "value": 0.0}' ||
    '],' ||
    '"abcense_ratios": [' ||
     '{"threshold": 0, "value": 1.0}, ' ||
     '{"threshold": 1, "value": 0.8}, ' ||
     '{"threshold": 2, "value": 0.6}, ' ||
     '{"threshold": 3, "value": 0.4}, ' ||
     '{"threshold": 4, "value": 0.2}, ' ||
     '{"threshold": 5, "value": 0.0}' ||
    '],' ||
    '"min_shifts_cnt": 4, ' ||
    '"min_short_shifts_cnt": 6, ' ||
    '"qa_unified_qa_weight": 0.6, ' ||
    '"claim_unified_qa_weight": 0.4, ' ||
    '"abcense_discipline_weight": 0.5, ' ||
    '"delay_discipline_weight": 0.5, ' ||
    '"unified_qa_rating_weight": 0.8, ' ||
    '"discipline_rating_weight": 0.1, ' ||
    '"hour_cost_rating_weight": 0.1, ' ||
    '"min_workshifts_ratio": 0.25, ' ||
    '"min_hour_cost": 10.0, ' ||
    '"benefit_thresholds_strict": [' ||
     '{"threshold": 0, "value": 0.5}, ' ||
     '{"threshold": 80, "value": 0.0}' ||
    ']' ||
   '}')::JSONB,
  ARRAY['ru'],
  True,
  True,
  True,
  '2019-12-01'::DATE,
  'infinity',
  '08:00'::TIME,
  '20:00'::TIME
);

INSERT INTO piecework.payment(
  payment_id, tariff_type, calculation_rule_id, start_date,
  stop_date, country, login, branch, daytime_cost, night_cost,
  holidays_daytime_cost, holidays_night_cost, total_cost, min_hour_cost, workshifts_duration,
  plan_workshifts_duration, csat_ratio, min_csat_ratio, qa_ratio, min_qa_ratio,
  rating_factor, rating, high_benefit_percentage, low_benefit_percentage, benefit_factor,
  extra_workshift_benefits, benefits, extra_costs, branch_benefit_conditions
) VALUES (
  'result_id_5', 'call-taxi-unified', 'call_taxi_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ru', 'ivanova', NULL,
  10.0, 5.0, 8.0, 1.0, 23.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
  NULL, NULL, NULL, NULL, NULL, 0.0, NULL, NULL
), (
  'result_id_6', 'call-taxi-unified', 'call_taxi_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ru', 'petrova', NULL,
  25.0, 7.0, 10.0, 0.0, 42.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
  NULL, NULL, NULL, NULL, NULL, 0.0, NULL, NULL
), (
  'result_id_7', 'call-taxi-unified', 'call_taxi_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ru', 'smirnova', NULL,
  11.0, 6.0, 12.0, 3.0, 0.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
  NULL, NULL, NULL, NULL, NULL, 0.0, NULL, NULL
), (
  'result_id_8', 'cargo-callcenter', 'cargo_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ru', 'ivanova', NULL,
  10.0, 5.0, 8.0, 1.0, 23.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
  NULL, NULL, NULL, NULL, NULL, 0.0, NULL, NULL
), (
  'result_id_9', 'cargo-callcenter', 'cargo_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ru', 'petrova', NULL,
  25.0, 7.0, 10.0, 0.0, 42.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
  NULL, NULL, NULL, NULL, NULL, 0.0, NULL, NULL
), (
  'result_id_10', 'cargo-callcenter', 'cargo_rule_id', '2020-01-01'::DATE,
  '2020-01-16'::DATE, 'ru', 'smirnova', NULL,
  11.0, 6.0, 12.0, 3.0, 0.0, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
  NULL, NULL, NULL, NULL, NULL, 0.0, NULL, NULL
);

INSERT INTO piecework.mapping_payday_uid_login(login, payday_uid) VALUES
    ('test_1', 'test_uid_1'),
    ('test_2', 'test_uid_2'),
    ('test_3', 'test_uid_3'),
    ('test_4', 'test_uid_4'),
    ('test_5', 'test_uid_5');

INSERT INTO piecework.payday_employee_loan VALUES
(
    'test_uid_1',
    '1',
    '2021-1-20 00:00:00',
    '1',
    15.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    NOW()
),
(
    'test_uid_2',
    '2',
    '2021-1-15 23:00:00',
    '2',
    16.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    NOW()
),
(
    'test_uid_3',
    '3',
    '2021-1-24 15:00:00',
    '3',
    16.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    NOW()
),
(
    'test_uid_4',
    '4',
    '2021-1-26 23:00:00',
    '4',
    16.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    NOW()
),
(
    'test_uid_5',
    '5',
    '2021-1-28 23:00:00',
    '5',
    16.5,
    '2022-2-20 00:00:00',
    '2022-2-20 00:00:00',
    NOW()
);

INSERT INTO piecework.agent_employee VALUES
(
    '1',
    '2021-1-16',
    '2021-2-1',
    'ru',
    'test_1',
    'b',
    NOW(),
    NOW(),
    'support-taxi',
    1,
    'Asia/Barnaul'
),
(
     '2',
    '2021-1-16',
    '2021-2-1',
     'ru',
     'test_2',
     'b',
     NOW(),
     NOW(),
     'support-taxi',
     1,
     'Asia/Irkutsk'
 ),
(
    '3',
    '2021-1-16',
    '2021-2-1',
    'ru',
    'test_3',
    'b',
    NOW(),
    NOW(),
    'support-taxi',
    1,
    NULL
 ),
(
    '4',
    '2021-1-16',
    '2021-2-1',
    'ru',
    'test_4',
    'b',
    NOW(),
    NOW(),
    'support-taxi',
    1,
    'Asia/Yekaterinburg'
 ),
(
    '5',
    '2021-1-16',
    '2021-2-1',
    'ru',
    'test_5',
    'b',
    NOW(),
    NOW(),
    'support-taxi',
    1,
    'Europe/Moscow'
 );
