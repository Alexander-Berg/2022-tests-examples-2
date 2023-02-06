INSERT INTO piecework.calculation_daily_result(
    calculation_daily_result_id, tariff_type,
    calc_type, calc_subtype, calculation_rule_id, calc_date,
    country, login, daytime_cost, night_cost,
    holidays_daytime_cost, holidays_night_cost
) VALUES (
     'daily_result_id_1', 'support-taxi', 'general',
     'chatterbox', 'some_rule_id_1', '2020-01-03'::DATE, 'rus', 'first',
     10.0, 5.0, 8.0, 1.0
), (
    'daily_result_id_2', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_1', '2020-01-04'::DATE, 'rus', 'second',
    11.0, 6.0, 9.0, 2.0
), (
    'daily_result_id_3', 'support-taxi', 'general',
    'call-taxi', 'some_rule_id_1', '2020-01-04'::DATE, 'rus', 'second',
    1.0, 1.0, 1.0, 1.0
), (
    'daily_result_id_4', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_1', '2020-01-05'::DATE, 'rus', 'second',
    1.0, 1.0, 1.0, 1.0
), (
    'daily_result_id_5', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_2', '2020-01-04'::DATE, 'rus', 'second',
    12.0, 7.0, 10.0, 3.0
), (
    'daily_result_id_6', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_1', '2020-01-02'::DATE, 'rus', 'third',
    120.0, 70.0, 100.0, 30.0
), (
    'daily_result_id_7', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_1', '2020-01-01'::DATE, 'rus', 'third',
    12.0, 7.0, 10.0, 3.0
), (
    'daily_result_id_11', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_1', '2020-01-04'::DATE, 'rus', 'third',
    12.0, 7.0, 10.0, 3.0
), (
    'daily_result_id_8', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_3', '2020-01-02'::DATE, 'rus', 'third',
    12.0, 7.0, 10.0, 3.0
), (
    'daily_result_id_10', 'support-taxi', 'general',
    'call-taxi', 'some_rule_id_3', '2020-01-02'::DATE, 'rus', 'third',
    12.0, 7.0, 10.0, 3.0
), (
    'daily_result_id_9', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_3', '2020-01-01'::DATE, 'rus', 'third',
    120.0, 70.0, 100.0, 30.0
),
(
    'daily_result_id_12', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_1', '2020-01-02'::DATE, 'rus', 'fourth',
    120.0, 70.0, 100.0, 30.0
), (
    'daily_result_id_13', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_1', '2020-01-01'::DATE, 'rus', 'fourth',
    12.0, 7.0, 10.0, 3.0
), (
    'daily_result_id_14', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_1', '2020-01-04'::DATE, 'rus', 'fourth',
    12.0, 7.0, 10.0, 3.0
), (
    'daily_result_id_15', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_4', '2020-01-02'::DATE, 'rus', 'fourth',
    12.0, 7.0, 10.0, 3.0
), (
    'daily_result_id_16', 'support-taxi', 'general',
    'call-taxi', 'some_rule_id_4', '2020-01-02'::DATE, 'rus', 'fourth',
    12.0, 7.0, 10.0, 3.0
), (
    'daily_result_id_17', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_4', '2020-01-01'::DATE, 'rus', 'fourth',
    120.0, 70.0, 100.0, 30.0
), (
    'daily_result_id_18', 'support-taxi', 'general',
    'call-taxi', 'some_rule_id_3', '2020-01-02'::DATE, 'rus', 'fifth',
    12.0, 7.0, 10.0, 3.0
), (
    'daily_result_id_19', 'support-taxi', 'general',
    'chatterbox', 'some_rule_id_3', '2020-01-01'::DATE, 'rus', 'fifth',
    120.0, 70.0, 100.0, 30.0
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
    description,
    payment_draft_ids,
    updated,
    rule_type
) VALUES (
    'some_rule_id_1',
    'support-taxi',
    '2020-01-01'::DATE,
    '2020-01-05'::DATE,
    True,
    ARRAY['rus'],
    ARRAY['first', 'second'],
    'success',
    'OK',
    '{"rus": 123}'::JSONB,
    '2020-01-10T14:00:00'::TIMESTAMP,
    'regular'
), (
    'some_rule_id_2',
    'support-taxi',
    '2020-01-01'::DATE,
    '2020-01-05'::DATE,
    True,
    ARRAY['rus'],
    null,
    'success',
    'OK',
    '{"rus": 123}'::JSONB,
    '2020-01-10T13:00:00'::TIMESTAMP,
    'regular'
), (
    'some_rule_id_3',
    'support-taxi',
    '2020-01-01'::DATE,
    '2020-01-03'::DATE,
    True,
    ARRAY['rus'],
    ARRAY['third', 'fifth'],
    'success',
    'OK',
    '{"rus": 123}'::JSONB,
    '2020-01-10T12:00:00'::TIMESTAMP,
    'dismissal'
), (
    'some_rule_id_4',
    'support-taxi',
    '2020-01-01'::DATE,
    '2020-01-04'::DATE,
    True,
    ARRAY['rus'],
    ARRAY['fourth'],
    'success',
    'OK',
    '{"rus": 123}'::JSONB,
    '2020-01-10T11:00:00'::TIMESTAMP,
    'dismissal'
);

INSERT INTO piecework.payment(
    payment_id, tariff_type, calculation_rule_id, start_date,
    stop_date, country, login, branch, daytime_cost, night_cost,
    holidays_daytime_cost, holidays_night_cost,
    total_cost, min_hour_cost, workshifts_duration,
    plan_workshifts_duration, csat_ratio, min_csat_ratio, qa_ratio, min_qa_ratio,
    rating_factor, high_benefit_percentage, low_benefit_percentage, benefit_factor,
    extra_workshift_benefits, benefits, extra_costs, branch_benefit_conditions,
    correction, benefit_conditions
) VALUES (
    'result_id_1', 'support-taxi', 'some_rule_id_1', '2020-01-01'::DATE,
    '2020-01-05'::DATE, 'rus', 'first', 'general',
    15.0, 7.0, 10.0, 1.0, 32.0, 1.0, 12.0, 12.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
    0.0, 0.5, 0.0, 16.0, NULL, '{}'::JSONB, NULL,
    '{"rating": 0.7975, "hour_cost": 14.0, "rating_pos": 2, "rating_prcnt": 66.66666666666666, "min_hour_cost": 10.0, "benefits_per_bo": 0.5, "hour_cost_ratio": 0.875, "discipline_ratio": 0.7, "unified_qa_ratio": 0.8, "workshifts_duration_sec": 3600, "plan_workshifts_duration_sec": 7200, "extra_custom_field": "value"}'::JSONB
), (
     'result_id_2', 'support-taxi', 'some_rule_id_1', '2020-01-01'::DATE,
     '2020-01-05'::DATE, 'rus', 'second', 'general',
     16.0, 8.0, 11.0, 2.0, 33.0, 2.0, 13.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
     0.0, 0.5, 0.0, 17.0, NULL, '{}'::JSONB, NULL, NULL
 ), (
     'result_id_3', 'support-taxi', 'some_rule_id_2', '2020-01-01'::DATE,
     '2020-01-05'::DATE, 'rus', 'second', 'general',
     15.0, 7.0, 10.0, 1.0, 32.0, 1.0, 12.0, 12.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
     0.0, 0.5, 0.0, 16.0, NULL, '{}'::JSONB, NULL, '{"rating_pos": 5, "extra_custom_field": "value"}'::JSONB
 ), (
     'result_id_4', 'support-taxi', 'some_rule_id_1', '2020-01-01'::DATE,
     '2020-01-05'::DATE, 'rus', 'third', 'general',
     15.0, 7.0, 10.0, 1.0, 32.0, 1.0, 12.0, 12.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
     0.0, 0.5, 0.0, 16.0, NULL, '{}'::JSONB, NULL,
     '{"rating": 0.8975, "hour_cost": 13.0, "rating_pos": 3, "rating_prcnt": 56.66666666666666, "min_hour_cost": 11.0, "benefits_per_bo": 0.6, "hour_cost_ratio": 0.875, "discipline_ratio": 0.7, "unified_qa_ratio": 0.8, "workshifts_duration_sec": 3600, "plan_workshifts_duration_sec": 7200, "extra_custom_field": "value"}'::JSONB
 ), (
     'result_id_5', 'support-taxi', 'some_rule_id_3', '2020-01-01'::DATE,
     '2020-01-03'::DATE, 'rus', 'third', 'general',
     5.0, 17.0, 0.0, 11.0, 3.0, 11.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
     0.0, 0.5, 0.0, 0.0, NULL, '{}'::JSONB, NULL, NULL
 ), (
     'result_id_6', 'support-taxi', 'some_rule_id_1', '2020-01-01'::DATE,
     '2020-01-05'::DATE, 'rus', 'fourth', 'general',
     15.0, 7.0, 10.0, 1.0, 32.0, 1.0, 12.0, 12.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
     0.0, 0.5, 0.0, 16.0, NULL, '{}'::JSONB, NULL,
     '{"rating": 0.8975, "hour_cost": 13.0, "rating_pos": 3, "rating_prcnt": 56.66666666666666, "min_hour_cost": 11.0, "benefits_per_bo": 0.6, "hour_cost_ratio": 0.875, "discipline_ratio": 0.7, "unified_qa_ratio": 0.8, "workshifts_duration_sec": 3600, "plan_workshifts_duration_sec": 7200, "extra_custom_field": "value"}'::JSONB
 ), (
     'result_id_7', 'support-taxi', 'some_rule_id_4', '2020-01-01'::DATE,
     '2020-01-03'::DATE, 'rus', 'fourth', 'general',
     55.0, 177.0, 1.0, 111.0, 3.0, 11.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
     0.0, 0.5, 0.0, 0.0, NULL, '{}'::JSONB, NULL, NULL
 ), (
     'result_id_8', 'support-taxi', 'some_rule_id_3', '2020-01-01'::DATE,
     '2020-01-03'::DATE, 'rus', 'fifth', 'general',
     55.0, 177.0, 1.0, 111.0, 3.0, 11.0, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
     0.0, 0.5, 0.0, 0.0, NULL, '{}'::JSONB, NULL, NULL
 );
