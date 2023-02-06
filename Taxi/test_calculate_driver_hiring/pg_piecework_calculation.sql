CREATE SCHEMA IF NOT EXISTS "taxi_cdm_contactcenter";
DROP TABLE IF EXISTS taxi_cdm_contactcenter.dm_operator_quality_metric;
CREATE TABLE taxi_cdm_contactcenter.dm_operator_quality_metric (
    _etl_processed_dttm TIMESTAMP WITHOUT TIME ZONE,
    operator_login VARCHAR,
    csat_not_excepted_sum NUMERIC,
    csat_not_excepted_cnt INTEGER,
    quality_cnt INTEGER,
    quality_sum NUMERIC,
    utc_report_dt DATE,
    csat_low_not_excepted_cnt INTEGER,
    claim_cnt INTEGER
);

CREATE SCHEMA IF NOT EXISTS taxi_udm_piecework;
DROP TABLE IF EXISTS taxi_udm_piecework.rep_operator_hiring_conversion_daily_snp;
CREATE TABLE taxi_udm_piecework.rep_operator_hiring_conversion_daily_snp (
    user_login VARCHAR NOT NULL,
    activated_lead_cnt INTEGER NOT NULL,
    call_cnt INTEGER NOT NULL,
    utc_business_dttm TIMESTAMP NOT NULL
);
DROP TABLE IF EXISTS taxi_udm_piecework.rep_operator_hiring_call_halfhourly;
CREATE TABLE taxi_udm_piecework.rep_operator_hiring_call_halfhourly(
    utc_business_dttm TIMESTAMP WITHOUT TIME ZONE,
    user_login VARCHAR,
    operator_skill_code VARCHAR,
    call_cnt INT NOT NULL,
    operator_shift_flg BOOLEAN NOT NULL,
    call_over_15_sec_flg BOOLEAN NOT NULL
);

CREATE SCHEMA IF NOT EXISTS taxi_cdm_piecework;
DROP TABLE IF EXISTS taxi_cdm_piecework.dim_operator_profile_hist;
CREATE TABLE taxi_cdm_piecework.dim_operator_profile_hist(
        dim_operator_profile_hist_id BIGSERIAL PRIMARY KEY,
        staff_login VARCHAR NOT NULL,
        timezone VARCHAR,
        position_name_ru VARCHAR,
        payment_period_start_dt TIMESTAMP NOT NULL,
        utc_valid_from_dttm TIMESTAMP NOT NULL,
        utc_valid_to_dttm TIMESTAMP NOT NULL
);
DROP TABLE IF EXISTS taxi_cdm_piecework.fct_operator_shift_act;
CREATE TABLE taxi_cdm_piecework.fct_operator_shift_act(
        fct_operator_shift_act_id BIGSERIAL PRIMARY KEY,
        staff_login VARCHAR NOT NULL,
        utc_shift_started_dttm TIMESTAMP NOT NULL,
        utc_shift_finished_dttm TIMESTAMP NOT NULL
);

CREATE SCHEMA IF NOT EXISTS taxi_ods_chatterbox_support_taxi;
DROP TABLE IF EXISTS taxi_ods_chatterbox_support_taxi.ticket;
CREATE TABLE taxi_ods_chatterbox_support_taxi.ticket(
    chatterbox_ticket_id VARCHAR PRIMARY KEY,
    tag_id_list VARCHAR[],
    utc_updated_dttm TIMESTAMP
);
DROP TABLE IF EXISTS taxi_ods_chatterbox_support_taxi.history;
CREATE TABLE taxi_ods_chatterbox_support_taxi.history(
    event_id VARCHAR PRIMARY KEY ,
    chatterbox_ticket_id VARCHAR NOT NULL,
    event_id_seq NUMERIC NOT NULL,
    utc_event_dttm TIMESTAMP NOT NULL,
    event_robot_flg BOOLEAN NOT NULL,
    staff_login VARCHAR NOT NULL,
    action_type VARCHAR NOT NULL,
    ticket_sector_name VARCHAR NOT NULL,
    event_macro_id_list VARCHAR[],
    chatterbox_button_id VARCHAR,
    full_added_tag_id_list VARCHAR[],
    smm_login VARCHAR
);
DROP TABLE IF EXISTS taxi_ods_chatterbox_support_taxi.event_change_log;
CREATE TABLE taxi_ods_chatterbox_support_taxi.event_change_log(
    event_id VARCHAR NOT NULL,
    ticket_id VARCHAR NOT NULL,
    change_type VARCHAR NOT NULL,
    field_name VARCHAR NOT NULL,
    change_value VARCHAR,
    PRIMARY KEY (event_id, field_name, ticket_id)
);

INSERT INTO taxi_ods_chatterbox_support_taxi.ticket (chatterbox_ticket_id, tag_id_list) VALUES (
    'ticket_id_1', -- chatterbox_ticket_id
    ARRAY['tag1', 'tag2'] -- tag_id_list
), (
    'ticket_id_2', -- chatterbox_ticket_id
    ARRAY['tag3'] -- tag_id_list
);

INSERT INTO taxi_ods_chatterbox_support_taxi.history VALUES (
    'event_1', -- event_id
    'ticket_id_1', -- chatterbox_ticket_id
    0, -- event_id_sec
    '2020-01-05 11:22:33', -- utc_event_dttm
    False, -- event_robot_flg,
    'ivanov', -- staff_login
    'close', -- action_type
    'first', -- ticket_sector_name
    ARRAY[123], -- event_macro_id_list,
    'chatterbox_close', -- chatterbox_button_id
    ARRAY['closed'], -- full_added_tag_id_list,
    NULL -- smm_login
), (
    'event_2', -- event_id
    'ticket_id_1', -- chatterbox_ticket_id
    0, -- event_id_sec
    '2020-01-05 11:22:33', -- utc_event_dttm
    False, -- event_robot_flg,
    'ivanov', -- staff_login
    'forward', -- action_type
    'first', -- ticket_sector_name
    ARRAY[456], -- event_macro_id_list,
    'chatterbox_forward', -- chatterbox_button_id
    ARRAY['forwarded'], -- full_added_tag_id_list,
    NULL -- smm_login
), (
    'event_3', -- event_id
    'ticket_id_1', -- chatterbox_ticket_id
    0, -- event_id_sec
    '2020-01-11 11:22:33', -- utc_event_dttm
    False, -- event_robot_flg,
    'ivanov', -- staff_login
    'communicate', -- action_type
    'first', -- ticket_sector_name
    ARRAY[789], -- event_macro_id_list,
    'chatterbox_communicate', -- chatterbox_button_id
    ARRAY['just_talk'], -- full_added_tag_id_list,
    NULL -- smm_login
), (
    'event_4', -- event_id
    'ticket_id_2', -- chatterbox_ticket_id
    0, -- event_id_sec
    '2020-01-11 11:22:33', -- utc_event_dttm
    False, -- event_robot_flg,
    'petrov', -- staff_login
    'close', -- action_type
    'urgent', -- ticket_sector_name
    ARRAY[]::varchar[], -- event_macro_id_list,
    'chatterbox_communicate', -- chatterbox_button_id
    ARRAY['just_talk'], -- full_added_tag_id_list,
    NULL -- smm_login
), (
    'event_5', -- event_id
    'ticket_id_2', -- chatterbox_ticket_id
    0, -- event_id_sec
    '2020-01-05 11:22:33', -- utc_event_dttm
    True, -- event_robot_flg,
    'superuser', -- staff_login
    'update_meta', -- action_type
    'smm', -- ticket_sector_name
    ARRAY[]::varchar[], -- event_macro_id_list,
    'chatterbox_smm', -- chatterbox_button_id
    ARRAY['smm'], -- full_added_tag_id_list,
    'petrov' -- smm_login
);

INSERT INTO taxi_ods_chatterbox_support_taxi.event_change_log VALUES (
    'event_5', -- event_id
    'ticket_id_2', -- ticket_id
    'set', -- change_type
    'smm', -- field_name
    'yes' -- change_value
), (
    'event_5', -- event_id
    'ticket_id_2', -- ticket_id
    'set', -- change_type
    'ml_request_id', -- field_name
    '123' -- change_value
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
  'ru_tariff_id',
  'driver-hiring',
  ('{"rules": [' ||
   '{' ||
    '"key": "close", "type": "action", "actions": ["close"], ' ||
    '"cost_by_line": {"__default__": 1.0}' ||
   '}, ' ||
   '{' ||
    '"key": "forward", "type": "action", "actions": ["forward"], ' ||
    '"cost_by_line": {"__default__": 0.8}' ||
   '},' ||
   '{' ||
    '"key": "communicate", "type": "action", "actions": ["communicate"], ' ||
    '"cost_by_line": {"__default__": 0.0, "urgent": 1.0}' ||
   '}, ' ||
   '{' ||
    '"key": "smm", "type": "action", "actions": ["update_meta"], ' ||
    '"meta_set": {"smm": "yes"}, ' ||
    '"cost_by_line": {"__default__": 0.0, "smm": 8.0}' ||
   '}, ' ||
   '{' ||
    '"type": "sf_oktell_call", "key": "sf_oktell_call", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"first": 10.0,' ||
     '"second": 15.0' ||
    '}' ||
   '}' ||
  ']}')::JSONB,
  ('{' ||
    '"min_hour_cost": 10.0,' ||
    '"unified_qa_rating_weight": 0.2,' ||
    '"hour_cost_rating_weight": 0.3,' ||
    '"conversion_rating_weight": 0.4,' ||
    '"min_workshifts_ratio": 0.25,' ||
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
  '2020-02-10'::DATE,
  '08:00'::TIME,
  '20:00'::TIME
);

INSERT INTO piecework.calculation_rule (
    calculation_rule_id,
    tariff_type,
    start_date,
    stop_date,
    repeat,
    countries,
    logins,
    status
) VALUES (
    'periodic_rule_id',
    'driver-hiring',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru', 'md'],
    NULL,
    'waiting_agent'
);

INSERT INTO taxi_cdm_piecework.fct_operator_shift_act
VALUES
(default, 'ivanov', '2019-11-30T17:00:00Z', '2019-12-01T05:00:00Z'),
(default, 'ivanov', '2019-12-02T17:00:00Z', '2019-12-03T05:00:00Z'),
(default, 'ivanov', '2019-12-05T17:00:00Z', '2019-12-06T05:00:00Z'),
(default, 'ivanov', '2019-12-07T17:00:00Z', '2019-12-08T05:00:00Z'),
(default, 'ivanov', '2019-12-10T17:00:00Z', '2019-12-11T05:00:00Z'),
(default, 'ivanov', '2019-12-12T17:00:00Z', '2019-12-13T05:00:00Z'),
(default, 'ivanov', '2019-12-15T17:00:00Z', '2019-12-16T05:00:00Z'),
(default, 'ivanov', '2019-12-31T17:00:00Z', '2020-01-01T05:00:00Z'),
(default, 'ivanov', '2020-01-02T17:00:00Z', '2020-01-03T05:00:00Z'),
(default, 'ivanov', '2020-01-05T17:00:00Z', '2020-01-06T05:00:00Z'),
(default, 'ivanov', '2020-01-07T17:00:00Z', '2020-01-08T05:00:00Z'),
(default, 'ivanov', '2020-01-10T17:00:00Z', '2020-01-11T05:00:00Z'),
(default, 'ivanov', '2020-01-12T17:00:00Z', '2020-01-13T05:00:00Z'),
(default, 'ivanov', '2020-01-15T17:00:00Z', '2020-01-16T05:00:00Z'),
(default, 'petrov', '2020-01-01T05:00:00Z', '2020-01-01T17:00:00Z'),
(default, 'petrov', '2020-01-02T05:00:00Z', '2020-01-02T17:00:00Z'),
(default, 'petrov', '2020-01-05T05:00:00Z', '2020-01-05T17:00:00Z'),
(default, 'petrov', '2020-01-06T05:00:00Z', '2020-01-06T17:00:00Z'),
(default, 'petrov', '2020-01-09T05:00:00Z', '2020-01-09T17:00:00Z'),
(default, 'petrov', '2020-01-10T05:00:00Z', '2020-01-10T17:00:00Z'),
(default, 'petrov', '2020-01-13T05:00:00Z', '2020-01-13T17:00:00Z'),
(default, 'petrov', '2020-01-14T05:00:00Z', '2020-01-14T17:00:00Z'),
(default, 'petrov', '2020-02-01T05:00:00Z', '2020-02-01T17:00:00Z'),
(default, 'petrov', '2020-02-02T05:00:00Z', '2020-02-02T17:00:00Z'),
(default, 'petrov', '2020-02-05T05:00:00Z', '2020-02-05T17:00:00Z'),
(default, 'petrov', '2020-02-06T05:00:00Z', '2020-02-06T17:00:00Z'),
(default, 'petrov', '2020-02-09T05:00:00Z', '2020-02-09T17:00:00Z'),
(default, 'petrov', '2020-02-10T05:00:00Z', '2020-02-10T17:00:00Z'),
(default, 'petrov', '2020-02-13T05:00:00Z', '2020-02-13T17:00:00Z'),
(default, 'petrov', '2020-02-14T05:00:00Z', '2020-02-14T17:00:00Z');

INSERT INTO taxi_cdm_piecework.dim_operator_profile_hist
VALUES
(default, 'ivanov', 'Europe/Moscow', 'support', '2019-12-01'::DATE, '2019-01-01T00:00:00', '2020-01-01T00:00:00'),
(default, 'ivanov', 'Europe/Kiev', 'support', '2020-01-01'::DATE, '2020-01-01T00:00:00', '2020-01-10T00:00:00'),
(default, 'ivanov', 'Europe/Moscow', 'support', '2020-01-01'::DATE, '2020-01-10T00:00:00', '9999-12-31T23:59:59'),
(default, 'petrov', 'Europe/Kiev', 'support', '2020-01-01'::DATE, '2020-01-01T00:00:00', '2020-01-16T00:00:00'),
(default, 'petrov', 'Europe/Moscow', 'support', '2020-01-01'::DATE, '2020-01-16T00:00:00', '2020-02-01T00:00:00'),
(default, 'petrov', 'Europe/Kiev', 'support', '2020-02-01'::DATE, '2020-02-01T00:00:00', '9999-12-31T23:59:59'),
(default, 'smirnoff', 'Europe/Volgograd', 'support', '2020-01-01'::DATE, '2020-01-01T00:00:00', '9999-12-31T23:59:59'),
(default, 'popov', NULL, 'support', '2020-01-01'::DATE, '2020-01-01T00:00:00', '9999-12-31T23:59:59');

INSERT INTO taxi_cdm_contactcenter.dm_operator_quality_metric VALUES
(NOW(), 'ivanov', 400, 4, 4, 320, '2020-01-01', 3, 0),
(NOW(), 'ivanov', 360, 4, 4, 360, '2020-01-03', 2, 0),
(NOW(), 'petrov', 294, 3, 3, 258, '2020-01-02', 1, 0),
(NOW(), 'petrov', 282, 3, 3, 255, '2020-01-05', 0, 0);

INSERT INTO taxi_udm_piecework.rep_operator_hiring_call_halfhourly VALUES
    ('2020-01-11T20:30:00.000000', 'ivanov', 'first', 4, true, true),
    ('2020-01-11T21:00:00.000000', 'ivanov', 'second', 4, false, true);

INSERT INTO taxi_udm_piecework.rep_operator_hiring_conversion_daily_snp VALUES
    ('ivanov', 5, 5, '2020-01-02T20:30:00.000000'),
    ('ivanov', 4, 5, '2020-01-11T20:30:00.000000'),
    ('petrov', 1, 3, '2020-01-03T20:30:00.000000'),
    ('petrov', 4, 5, '2020-01-08T20:30:00.000000');
