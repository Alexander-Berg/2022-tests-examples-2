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

CREATE SCHEMA IF NOT EXISTS "taxi_cdm_piecework";
DROP TABLE IF EXISTS taxi_cdm_piecework.rep_operator_activity_halfhourly;
CREATE TABLE taxi_cdm_piecework.rep_operator_activity_halfhourly (
    utc_report_dttm TIMESTAMP WITHOUT TIME ZONE,
    staff_login VARCHAR,
    sector_name VARCHAR,
    action_cnt INT NOT NULL,
    operator_shift_flg BOOLEAN NOT NULL,
    cc_solved_flg BOOLEAN,
    call_income_flg BOOLEAN,
    action_name VARCHAR  NOT NULL,
    call_over_15_sec_flg BOOLEAN NOT NULL,
    cc_flg BOOLEAN NOT NULL
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
CREATE SCHEMA IF NOT EXISTS "taxi_ods_support_tracker";
DROP TABLE IF EXISTS taxi_ods_support_tracker.ticket_log;
CREATE TABLE taxi_ods_support_tracker.ticket_log(
    event_id VARCHAR PRIMARY KEY ,
    user_login VARCHAR,
    ticket_id VARCHAR,
    comment_list VARCHAR[] NOT NULL,
    status_code VARCHAR,
    has_email_message_flg BOOL,
    ticket_type VARCHAR,
    utc_event_dttm TIMESTAMP WITHOUT TIME ZONE
);
DROP TABLE IF EXISTS taxi_ods_support_tracker.ticket;
CREATE TABLE taxi_ods_support_tracker.ticket
(
    startrack_ticket_id VARCHAR,
    ticket_type         VARCHAR,
    ticket_code         VARCHAR
);

CREATE SCHEMA IF NOT EXISTS "taxi_ods_support_chatterbox";
DROP TABLE IF EXISTS taxi_ods_support_chatterbox.startrack_sip_calls;
CREATE TABLE taxi_ods_support_chatterbox.startrack_sip_calls(
    call_id VARCHAR PRIMARY KEY,
    user_login VARCHAR,
    ticket_type VARCHAR,
    utc_created_dttm TIMESTAMP WITHOUT TIME ZONE,
    utc_answered_dttm TIMESTAMP WITHOUT TIME ZONE,
    utc_completed_dttm TIMESTAMP WITHOUT TIME ZONE,
    call_completed_status VARCHAR,
    direction_code VARCHAR
);
DROP TABLE IF EXISTS taxi_ods_chatterbox_support_taxi.call;
CREATE TABLE taxi_ods_chatterbox_support_taxi.call(
    call_id VARCHAR PRIMARY KEY,
    chatterbox_ticket_id VARCHAR NOT NULL,
    staff_login VARCHAR NOT NULL,
    utc_created_dttm TIMESTAMP NOT NULL,
    utc_answered_dttm TIMESTAMP,
    utc_completed_dttm TIMESTAMP,
    sector_name VARCHAR NOT NULL,
    call_direction_name VARCHAR NOT NULL,
    call_completed_status VARCHAR NOT NULL
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
    'communicate', -- action_type
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

INSERT INTO taxi_ods_chatterbox_support_taxi.call VALUES (
    'call_id_1', -- call_id
    'ticket_id_2',-- chatterbox_ticket_id
    'petrov',-- staff_login
    '2020-01-11 11:22:33', -- utc_created_dttm
    '2020-01-11 11:22:35', -- utc_answered_dttm
    '2020-01-11 11:22:55', -- utc_completed_dttm
    'sip', -- sector_name
    'outgoing', -- call_direction_name
    'bridged' -- call_completed_status
), (
    'call_id_2', -- call_id
    'ticket_id_2', -- chatterbox_ticket_id
    'petrov', -- staff_login
    '2020-01-11 11:22:33', -- utc_created_dttm
    '2020-01-11 11:22:35', -- utc_answered_dttm
    '2020-01-11 11:22:55', -- utc_completed_dttm
    'first', -- sector_name
    'outgoing', -- call_direction_name
    'bridged' -- call_completed_status
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
  'ru_tariff_id_old',
  'cargo-support',
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
    '"type": "action", "actions": ["mail"], "key": "tracker_mail", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.0,' ||
     '"tracker_corp_users": 2.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["sms"], "key": "tracker_sms", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.5,' ||
     '"tracker_corp_users": 2.5' ||
    '}' ||
   '}' ||
  ']}')::JSONB,
  ('{' ||
    '"min_hour_cost": 10.0,' ||
    '"rating_avg_duration_weight": 0.0,' ||
    '"rating_total_cost_weight": 0.0025,' ||
    '"rating_csat_weight": 0.49875,' ||
    '"rating_qa_weight": 0.49875,' ||
    '"min_workshifts_ratio": 0.25,' ||
    '"rating_max_total_cost": 11000,' ||
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
  '2020-01-10'::DATE,
  '08:00'::TIME,
  '20:00'::TIME
), (
  'ru_tariff_id',
  'cargo-support',
  ('{"rules": [' ||
   '{' ||
    '"key": "close", "type": "action", "actions": ["close"], ' ||
    '"cost_by_line": {"__default__": 1.0, "urgent": 10.0}' ||
   '}, ' ||
   '{' ||
    '"key": "forward", "type": "action", "actions": ["forward"], ' ||
    '"cost_by_line": {"__default__": 0.8, "urgent": 5.0}' ||
   '}, ' ||
   '{' ||
    '"key": "communicate", "type": "action", "actions": ["communicate"], ' ||
    '"cost_by_line": {"__default__": 0.0, "urgent": 1.0}' ||
   '}, ' ||
   '{' ||
    '"type": "action", "actions": ["mail"], "key": "tracker_mail", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.0,' ||
     '"tracker_corp_users": 2.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["sms"], "key": "tracker_sms", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.5,' ||
     '"tracker_corp_users": 2.5' ||
    '}' ||
   '}' ||
  ']}')::JSONB,
  ('{' ||
    '"min_hour_cost": 10.0,' ||
    '"rating_avg_duration_weight": 0.0,' ||
    '"rating_total_cost_weight": 0.0025,' ||
    '"rating_csat_weight": 0.49875,' ||
    '"rating_qa_weight": 0.49875,' ||
    '"min_workshifts_ratio": 0.25,' ||
    '"rating_max_total_cost": 11000,' ||
    '"benefit_thresholds_strict": [' ||
     '{"threshold": 0, "value": 0.5}, ' ||
     '{"threshold": 80, "value": 0.0}' ||
    ']' ||
  '}')::JSONB,
  ARRAY['ru'],
  False,
  True,
  True,
  '2020-01-10'::DATE,
  'infinity'::DATE,
  '08:00'::TIME,
  '20:00'::TIME
), (
  'md_tariff_id_old',
  'cargo-support',
  ('{"rules": [' ||
   '{' ||
    '"key": "close", "type": "action", "actions": ["close"], ' ||
    '"cost_by_line": {"__default__": 1.0}' ||
   '}, ' ||
   '{' ||
    '"key": "smm", "type": "action", "actions": ["update_meta"], ' ||
    '"meta_set": {"smm": "yes"}, ' ||
    '"cost_by_line": {"__default__": 0.0, "smm": 8.0}' ||
   '}, ' ||
   '{' ||
    '"key": "forward", "type": "action", "actions": ["forward"], ' ||
    '"cost_by_line": {"__default__": 0.8}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["mail"], "key": "tracker_mail", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.0,' ||
     '"tracker_corp_users": 2.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["sms"], "key": "tracker_sms", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.5,' ||
     '"tracker_corp_users": 2.5' ||
    '}' ||
   '}' ||
  ']}')::JSONB,
  ('{' ||
    '"min_hour_cost": 10.0,' ||
    '"rating_avg_duration_weight": 0.0,' ||
    '"rating_total_cost_weight": 0.0025,' ||
    '"rating_csat_weight": 0.49875,' ||
    '"rating_qa_weight": 0.49875,' ||
    '"min_workshifts_ratio": 0.25,' ||
    '"rating_max_total_cost": 11000,' ||
    '"benefit_thresholds_strict": [' ||
     '{"threshold": 0, "value": 0.5}, ' ||
     '{"threshold": 80, "value": 0.0}' ||
    ']' ||
  '}')::JSONB,
  ARRAY['md'],
  True,
  True,
  True,
  '2019-12-01'::DATE,
  '2020-01-10'::DATE,
  '08:00'::TIME,
  '20:00'::TIME
), (
  'md_tariff_id',
  'cargo-support',
  ('{"rules": [' ||
   '{' ||
    '"key": "close", "type": "action", "actions": ["close"], ' ||
    '"cost_by_line": {"__default__": 1.0, "urgent": 10.0}' ||
   '}, ' ||
   '{' ||
    '"key": "smm", "type": "action", "actions": ["update_meta"], ' ||
    '"meta_set": {"smm": "yes"}, ' ||
    '"cost_by_line": {"__default__": 0.0, "smm": 8.0}' ||
   '}, ' ||
   '{' ||
    '"key": "forward", "type": "action", "actions": ["forward"], ' ||
    '"cost_by_line": {"__default__": 0.8, "urgent": 5.0}' ||
   '}, ' ||
   '{' ||
    '"key": "communicate", "type": "action", "actions": ["communicate"], ' ||
    '"cost_by_line": {"__default__": 0.0, "urgent": 1.0}' ||
   '}, ' ||
   '{' ||
    '"type": "action", "actions": ["mail"], "key": "tracker_mail", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.0,' ||
     '"tracker_corp_users": 2.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["sms"], "key": "tracker_sms", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.5,' ||
     '"tracker_corp_users": 2.5' ||
    '}' ||
   '}' ||
  ']}')::JSONB,
  ('{' ||
    '"min_hour_cost": 10.0,' ||
    '"rating_avg_duration_weight": 0.0,' ||
    '"rating_total_cost_weight": 0.0025,' ||
    '"rating_csat_weight": 0.49875,' ||
    '"rating_qa_weight": 0.49875,' ||
    '"min_workshifts_ratio": 0.25,' ||
    '"rating_max_total_cost": 11000,' ||
    '"benefit_thresholds_strict": [' ||
     '{"threshold": 0, "value": 0.5}, ' ||
     '{"threshold": 80, "value": 0.0}' ||
    ']' ||
  '}')::JSONB,
  ARRAY['md'],
  False,
  True,
  True,
  '2020-01-10'::DATE,
  'infinity'::DATE,
  '08:00'::TIME,
  '20:00'::TIME
), (
  'blr_tariff_id',
  'cargo-support',
  ('{"rules": [' ||
   '{' ||
    '"key": "close", "type": "action", "actions": ["close"], ' ||
    '"cost_by_line": {"__default__": 1.0}' ||
   '}, ' ||
   '{' ||
    '"key": "forward", "type": "action", "actions": ["forward"], ' ||
    '"cost_by_line": {"__default__": 0.8}' ||
   '}, ' ||
   '{' ||
    '"key": "communicate", "type": "action", "actions": ["communicate"], ' ||
    '"cost_by_line": {"__default__": 0.5}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["mail"], "key": "tracker_mail", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.0,' ||
     '"tracker_corp_users": 2.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["sms"], "key": "tracker_sms", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.5,' ||
     '"tracker_corp_users": 2.5' ||
    '}' ||
   '}' ||
  ']}')::JSONB,
  ('{' ||
    '"min_hour_cost": 10.0,' ||
    '"rating_avg_duration_weight": 0.0,' ||
    '"rating_total_cost_weight": 0.0025,' ||
    '"rating_csat_weight": 0.49875,' ||
    '"rating_qa_weight": 0.49875,' ||
    '"min_workshifts_ratio": 0.25,' ||
    '"rating_max_total_cost": 11000,' ||
    '"benefit_thresholds_strict": [' ||
     '{"threshold": 0, "value": 0.5}, ' ||
     '{"threshold": 80, "value": 0.0}' ||
    ']' ||
  '}')::JSONB,
  ARRAY['blr'],
  True,
  True,
  True,
  '2019-12-01'::DATE,
  'infinity'::DATE,
  '09:00'::TIME,
  '21:00'::TIME
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
    'cargo-support',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru', 'md'],
    NULL,
    'waiting_agent'
);

INSERT INTO piecework.cmpd_employee_period(
  cmpd_employee_period_id,
  start_date,
  stop_date,
  start_dt,
  stop_dt,
  login,
  country,
  branch,
  location,
  timezone,
  csat_ratio,
  qa_ratio,
  workshifts,
  workshifts_duration,
  plan_workshifts_duration,
  extra_workshifts,
  extra_workshifts_duration,
  vacations,
  vacations_duration,
  rating_factor,
  extra_bo
) VALUES (
  'ivanov_id_past',
  '2019-12-01'::DATE,
  '2019-12-16'::DATE,
  '2019-11-30T21:00:00Z'::TIMESTAMP,
  '2019-12-15T21:00:00Z'::TIMESTAMP,
  'ivanov',
  'ru',
  'general',
  'Moscow',
  '+0300',
  95.0,
  85.0,
  ('[["2019-11-30T20:00:00", "2019-12-01T08:00:00"],' ||
    '["2019-12-02T20:00:00", "2019-12-03T08:00:00"],' ||
    '["2019-12-05T20:00:00", "2019-12-06T08:00:00"],' ||
    '["2019-12-07T20:00:00", "2019-12-08T08:00:00"],' ||
    '["2019-12-10T20:00:00", "2019-12-11T08:00:00"],' ||
    '["2019-12-12T20:00:00", "2019-12-13T08:00:00"],' ||
    '["2019-12-15T20:00:00", "2019-12-16T08:00:00"]]')::JSONB,
  84.0,
  84.0,
  NULL,
  0,
  NULL,
  0,
  1.0,
  NULL
), (
  'ivanov_id',
  '2020-01-01'::DATE,
  '2020-01-16'::DATE,
  '2019-12-31T21:00:00Z'::TIMESTAMP,
  '2020-01-15T21:00:00Z'::TIMESTAMP,
  'ivanov',
  'ru',
  'general',
  'Moscow',
  '+0300',
  95.0,
  85.0,
  ('[["2019-12-31T20:00:00", "2020-01-01T08:00:00"],' ||
    '["2020-01-02T20:00:00", "2020-01-03T08:00:00"],' ||
    '["2020-01-05T20:00:00", "2020-01-06T08:00:00"],' ||
    '["2020-01-07T20:00:00", "2020-01-08T08:00:00"],' ||
    '["2020-01-10T20:00:00", "2020-01-11T08:00:00"],' ||
    '["2020-01-12T20:00:00", "2020-01-13T08:00:00"],' ||
    '["2020-01-15T20:00:00", "2020-01-16T08:00:00"]]')::JSONB,
  84.0,
  84.0,
  ('[{"start_ts": "2020-01-04T05:00:00+0000", ' ||
   '"stop_ts": "2020-01-04T17:00:00+0000", ' ||
   '"benefit_ratio": "0.5"}]')::JSONB,
  12,
  NULL,
  0,
  1.0,
  NULL
), (
  'petrov_id',
  '2020-01-01'::DATE,
  '2020-01-16'::DATE,
  '2019-12-31T22:00:00Z'::TIMESTAMP,
  '2020-01-15T22:00:00Z'::TIMESTAMP,
  'petrov',
  'md',
  'other',
  'Kishinev',
  '+0200',
  96.0,
  85.5,
  ('[["2020-01-01T08:00:00", "2020-01-01T20:00:00"],' ||
    '["2020-01-02T08:00:00", "2020-01-02T20:00:00"],' ||
    '["2020-01-05T08:00:00", "2020-01-05T20:00:00"],' ||
    '["2020-01-06T08:00:00", "2020-01-06T20:00:00"],' ||
    '["2020-01-09T08:00:00", "2020-01-09T20:00:00"],' ||
    '["2020-01-10T08:00:00", "2020-01-10T20:00:00"],' ||
    '["2020-01-13T08:00:00", "2020-01-13T20:00:00"],' ||
    '["2020-01-14T08:00:00", "2020-01-14T20:00:00"]]')::JSONB,
  96.0,
  96.0,
  NULL,
  0,
  NULL,
  0,
  2.0,
  ('[{' ||
   '"source": "tracker",' ||
   '"daytime_bo": "10.0",' ||
   '"night_bo": "15.0",' ||
   '"holidays_daytime_bo": "5.0",' ||
   '"holidays_night_bo": "0.0",' ||
   '"total_bo": "20.0"' ||
   '}]')::JSONB
), (
  'petrov_id_future',
  '2020-02-01'::DATE,
  '2020-02-16'::DATE,
  '2019-12-31T22:00:00Z'::TIMESTAMP,
  '2020-01-15T22:00:00Z'::TIMESTAMP,
  'petrov',
  'md',
  'other',
  'Kishinev',
  '+0200',
  96.0,
  85.5,
  ('[["2020-02-01T08:00:00", "2020-02-01T20:00:00"],' ||
    '["2020-02-02T08:00:00", "2020-02-02T20:00:00"],' ||
    '["2020-02-05T08:00:00", "2020-02-05T20:00:00"],' ||
    '["2020-02-06T08:00:00", "2020-02-06T20:00:00"],' ||
    '["2020-02-09T08:00:00", "2020-02-09T20:00:00"],' ||
    '["2020-02-10T08:00:00", "2020-02-10T20:00:00"],' ||
    '["2020-02-13T08:00:00", "2020-02-13T20:00:00"],' ||
    '["2020-02-14T08:00:00", "2020-02-14T20:00:00"]]')::JSONB,
  96.0,
  96.0,
  ('[{' ||
   '"start_ts": "2020-01-04T05:00:00+0000", ' ||
   '"stop_ts": "2020-01-04T17:00:00+0000", ' ||
   '"benefit_ratio": "0.5"}]')::JSONB,
  12,
  NULL,
  0,
  1.0,
  NULL
), (
  'smirnoff_id',
  '2020-01-01'::DATE,
  '2020-01-16'::DATE,
  '2019-12-31T20:00:00Z'::TIMESTAMP,
  '2020-01-15T20:00:00Z'::TIMESTAMP,
  'smirnoff',
  'ru',
  'general',
  'Volgograd',
  '+0400',
  0,
  0,
  '[]'::JSONB,
  0,
  0,
  NULL,
  0,
  NULL,
  0,
  1.0,
  NULL
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
