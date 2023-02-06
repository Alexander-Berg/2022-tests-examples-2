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

CREATE SCHEMA IF NOT EXISTS "taxi_cdm_piecework";
DROP TABLE IF EXISTS taxi_cdm_piecework.rep_operator_activity_halfhourly;
CREATE TABLE taxi_cdm_piecework.rep_operator_activity_halfhourly (
    utc_report_dttm TIMESTAMP WITHOUT TIME ZONE,
    staff_login VARCHAR NOT NULL,
    sector_name VARCHAR NOT NULL,
    action_cnt INT NOT NULL,
    operator_shift_flg BOOLEAN NOT NULL,
    cc_solved_flg BOOLEAN NOT NULL,
    call_income_flg BOOLEAN NOT NULL,
    action_name VARCHAR  NOT NULL,
    call_over_15_sec_flg BOOLEAN NOT NULL,
    cc_flg BOOLEAN NOT NULL
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

CREATE SCHEMA IF NOT EXISTS eda_ods_oktell;
DROP TABLE IF EXISTS eda_ods_oktell.effort_connection;
CREATE TABLE eda_ods_oktell.effort_connection(
    sk_id VARCHAR PRIMARY KEY,
    utc_call_started_dttm TIMESTAMP NOT NULL,
    call_id VARCHAR,
    call_dur NUMERIC NOT NULL,
    operator_id VARCHAR,
    task_id VARCHAR NOT NULL
);
DROP TABLE IF EXISTS eda_ods_oktell.taskmanager_task;
CREATE TABLE eda_ods_oktell.taskmanager_task(
    task_id VARCHAR PRIMARY KEY,
    task_name VARCHAR NOT NULL
);
DROP TABLE IF EXISTS eda_ods_oktell.user;
CREATE TABLE eda_ods_oktell.user(
    user_id VARCHAR PRIMARY KEY,
    user_login VARCHAR NOT NULL
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
), (
    'event_6', -- event_id
    'ticket_id_1', -- chatterbox_ticket_id
    0, -- event_id_sec
    '2020-01-05 11:22:33', -- utc_event_dttm
    False, -- event_robot_flg,
    'popov', -- staff_login
    'close', -- action_type
    'first', -- ticket_sector_name
    ARRAY[123], -- event_macro_id_list,
    'chatterbox_close', -- chatterbox_button_id
    ARRAY['closed'], -- full_added_tag_id_list,
    NULL -- smm_login
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
  'ru_tariff_id_old',
  'support-eats',
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
  'support-eats',
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
   '},' ||
   '{' ||
    '"type": "call_oktell", "key": "oktell_call", "min_duration": 5, ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"Support Eats Client-Courier": 5.5,' ||
     '"Support Eats L1-Retail": 7.5' ||
    '}' ||
   '},' ||
   '{' ||
      '"type": "call", "key": "sip_call", "min_duration": 16, ' ||
      '"direction": "outgoing", ' ||
      '"cost_by_line": {' ||
      '"__default__": 0.0,' ||
      '"tracker_dtpStrahovanie": 5.5,' ||
      '"tracker_corp_users": 7.5' ||
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
  'support-eats',
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
  'support-eats',
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
   '},' ||
   '{' ||
    '"type": "call_oktell", "key": "oktell_call", "min_duration": 5, ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"Support Eats L1-Retail": 5.5,' ||
     '"Support Eats Chats": 7.5' ||
    '}' ||
   '},' ||
     '{' ||
      '"type": "call", "key": "sip_call", "min_duration": 16, ' ||
      '"direction": "outgoing", ' ||
      '"cost_by_line": {' ||
      '"__default__": 0.0,' ||
      '"tracker_dtpStrahovanie": 5.5,' ||
      '"tracker_corp_users": 7.5' ||
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
  'support-eats',
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
    'support-eats',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru', 'md'],
    NULL,
    'waiting_agent'
);

INSERT INTO eda_ods_oktell.effort_connection(
  sk_id,
  utc_call_started_dttm,
  call_id,
  call_dur,
  operator_id,
  task_id
) VALUES (
  'commutation_1',
  '2020-01-04 11:22:33'::TIMESTAMP,
  'call_1',
   0.5,
   NULL,
  'task_1'
), (
  'commutation_2',
  '2020-01-05T19:00:00'::TIMESTAMP,
  'call_2',
   4,
  'ivanov_id',
  'task_2'
), (
  'commutation_3',
  '2020-01-05T19:00:04'::TIMESTAMP,
  'call_2',
   15.5,
  'petrov_id',
  'task_2'
), (
  'commutation_4',
  '2020-01-15T11:22:33'::TIMESTAMP,
  'call_3',
   5,
  'smirnoff_id',
  'task_3'
), (
  'commutation_5',
  '2020-01-11T11:22:38'::TIMESTAMP,
  'call_3',
   6.5,
  'petrov_id',
  'task_3'
), (
  'commutation_6',
  '2020-01-15T21:58:38'::TIMESTAMP,
  'call_4',
   3,
  'petrov_id',
  'task_2'
), (
  'commutation_7',
  '2020-01-15T22:02:11'::TIMESTAMP,
  'call_4',
   2,
  'petrov_id',
  'task_2'
), (
  'commutation_8',
  '2020-01-15T20:02:11'::TIMESTAMP,
  'call_5',
   10,
  'smirnoff_id',
  'task_3'
);

INSERT INTO eda_ods_oktell.taskmanager_task(task_id, task_name)
VALUES
  ('task_1', 'Support Eats L1-Retail'),
  ('task_2', 'Support Eats Chats'),
  ('task_3', 'Support Eats Client-Courier');

INSERT INTO eda_ods_oktell.user(user_id, user_login)
VALUES
  ('ivanov_id', 'ivanov'),
  ('petrov_id', 'petrov'),
  ('smirnoff_id', 'smirnoff');

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

INSERT INTO piecework.eats_support_metrics (
    operator_login,
    csat_sum,
    csat_cnt,
    quality_sum,
    quality_cnt,
    claim_cnt,
    utc_event_dt
) VALUES
('ivanov', 285, 3, 232.5, 3, 1, '2020-01-03'),
('petrov', 288, 3, 236.25, 3, 1, '2020-01-05');

INSERT INTO taxi_cdm_piecework.rep_operator_activity_halfhourly VALUES
('2020-01-10T21:00:00.000000', 'ivanov', 'test1', 4, true, false, true, 'call', true, true),
('2020-01-10T21:00:00.000000', 'ivanov', 'test1', 4, true, false, true, 'call', false, true);;
