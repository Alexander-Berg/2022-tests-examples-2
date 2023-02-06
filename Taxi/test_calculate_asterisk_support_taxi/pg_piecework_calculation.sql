CREATE SCHEMA IF NOT EXISTS "taxi_cdm_contactcenter";
DROP TABLE IF EXISTS taxi_cdm_contactcenter.dm_operator_quality_metric;
CREATE TABLE taxi_cdm_contactcenter.dm_operator_quality_metric (
    _etl_processed_dttm TIMESTAMP WITHOUT TIME ZONE,
    operator_login VARCHAR,
    csat_not_excepted_sum NUMERIC,
    csat_not_excepted_cnt INTEGER,
    quality_cnt INTEGER,
    quality_sum NUMERIC,
    claim_cnt INTEGER,
    utc_report_dt DATE,
    csat_low_not_excepted_cnt INTEGER
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

INSERT INTO taxi_ods_support_tracker.ticket VALUES
('ticket_1', 'dtpStrahovanie', 'test-ticket'),
('ticket_2', 'dtpStrahovanie', 'test-ticket_1'),
('ticket_3', 'corp_users', 'test-ticket_2'),
('ticket_4', 'incident', 'test-ticket_open');

INSERT INTO taxi_ods_support_tracker.ticket_log VALUES
('event_1', 'ivanov', 'ticket_1', ARRAY[]::varchar[], 'close', True, NULL, '2020-01-01T05:00:00'),
('event_2', 'superuser', 'ticket_1', ARRAY[]::varchar[], 'close', False, 'dtpStrahovanie', '2020-01-01T05:00:00'),
('event_3', 'ivanov', 'ticket_2', ARRAY[]::varchar[], 'close', True, NULL, '2020-01-06T03:00:00'),
(
 'event_4', 'robotsupporttaxi', 'ticket_2',
 ARRAY[
     E'blablabla\n' ||
     E'-----\n' ||
     E'login: ivanov\n' ||
     E'create_dt: 2020-01-06T03:00:00\n' ||
     E'status: sent'
 ],
 'close', False, NULL, '2020-01-06T05:00:00'
),
('event_5', 'superuser', 'ticket_2', ARRAY[]::varchar[], 'close', False, 'dtpStrahovanie', '2020-01-06T04:00:00'),
('event_6', 'petrov', 'ticket_3', ARRAY[]::varchar[], 'close', True, NULL, '2020-01-02T03:00:00'),
('event_7', 'petrov', 'ticket_3', ARRAY[]::varchar[], 'close', True, NULL, '2020-01-02T06:00:00'),
(
 'event_8', 'robotsupporttaxi', 'ticket_3',
 ARRAY[
     E'blablabla\n' ||
     E'-----\n' ||
     E'login: petrov\n' ||
     E'create_dt: 2020-01-06T03:00:00\n' ||
     E'status: failed'
 ],
 'close', False, NULL, '2020-01-06T05:00:00'
),
('event_9', 'unknown', 'ticket_3', ARRAY[]::varchar[], 'close', True, NULL, '2020-01-02T06:00:00'),
('event_10', 'superuser', 'ticket_3', ARRAY[]::varchar[], 'close', False, 'corp_users', '2020-01-02T06:00:00'),
('event_11', 'ivanov', 'ticket_4', ARRAY[]::varchar[], 'open', False, 'incident', '2020-01-02T18:00:00'),
('event_12', 'ivanov', 'ticket_4', ARRAY[]::varchar[], 'close', False, 'incident', '2020-01-02T18:01:00'),
('event_13', 'ivanov', 'ticket_4', ARRAY[]::varchar[], 'open', False, 'incident', '2020-01-02T18:02:00'),
('event_14', 'popov', 'ticket_3', ARRAY[]::varchar[], 'close', True, NULL, '2020-01-02T06:01:00'),
('event_15', 'popov2', 'ticket_3', ARRAY[]::varchar[], 'close', True, NULL, '2020-01-12T06:01:00');

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
), (
    'event_7', -- event_id
    'ticket_id_1', -- chatterbox_ticket_id
    0, -- event_id_sec
    '2020-01-13 11:22:33', -- utc_event_dttm
    False, -- event_robot_flg,
    'popov2', -- staff_login
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
  'asterisk-support-taxi',
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
    '"type": "action", "actions": ["mail"], "key": "mail", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.0,' ||
     '"tracker_corp_users": 2.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["sms"], "key": "sms", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.5,' ||
     '"tracker_corp_users": 2.5' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "call", "key": "sip_call", "min_duration": 16, ' ||
    '"direction": "outgoing", "status_completed": "bridged", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 5.5,' ||
     '"tracker_corp_users": 7.5' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["tracker_create"], ' ||
    '"key": "tracker_create", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_incident": 324.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "asterisk_call", "key": "asterisk_solved_call", ' ||
    '"solved": true,' ||
    '"direction": "incoming",' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"test1": 33.0' ||
    '}' ||
   '},'
   '{' ||
    '"type": "asterisk_call", "key": "asterisk_call", ' ||
    '"direction": "incoming",' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"test1": 11.0' ||
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
    '"lunch_duration_sec": 3600,' ||
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
  'asterisk-support-taxi',
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
    '"key": "sip_call", "type": "call", "min_duration": 15, ' ||
    '"direction": "outgoing", "status_completed": "bridged", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0, ' ||
     '"sip": 3.5,' ||
     '"tracker_dtpStrahovanie": 5.5,' ||
     '"tracker_corp_users": 7.5' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["mail"], "key": "mail", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.0,' ||
     '"tracker_corp_users": 2.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["sms"], "key": "sms", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.5,' ||
     '"tracker_corp_users": 2.5' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "asterisk_call", "key": "asterisk_solved_call", ' ||
    '"solved": true,' ||
    '"direction": "incoming",' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"test1": 33.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "asterisk_call", "key": "asterisk_call", ' ||
    '"direction": "incoming",' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"test1": 11.0, "test2": 13.0' ||
    '}' ||
   '}' ||
  ']}')::JSONB,
  ('{' ||
    '"min_hour_cost_by_position": {' ||
     '"__default__": 10.0,' ||
     '"head_of_support_department": 5.0' ||
   '},' ||
    '"rating_avg_duration_weight": 0.0,' ||
    '"rating_total_cost_weight": 0.0025,' ||
    '"rating_csat_weight": 0.49875,' ||
    '"rating_qa_weight": 0.49875,' ||
    '"min_workshifts_ratio": 0.25,' ||
    '"rating_max_total_cost": 11000,' ||
    '"lunch_duration_sec": 3600,' ||
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
  'asterisk-support-taxi',
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
    '"type": "action", "actions": ["mail"], "key": "mail", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.0,' ||
     '"tracker_corp_users": 2.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["sms"], "key": "sms", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.5,' ||
     '"tracker_corp_users": 2.5' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "call", "key": "sip_call", "min_duration": 16, ' ||
    '"direction": "outgoing", "status_completed": "bridged", ' ||
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
    '"lunch_duration_sec": 3600,' ||
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
  'asterisk-support-taxi',
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
    '"key": "sip_call", "type": "call", "min_duration": 15, ' ||
    '"direction": "outgoing", "status_completed": "bridged", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0, ' ||
     '"sip": 3.5,' ||
     '"tracker_dtpStrahovanie": 5.5,' ||
     '"tracker_corp_users": 7.5' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["mail"], "key": "mail", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.0,' ||
     '"tracker_corp_users": 2.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["sms"], "key": "sms", ' ||
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
    '"lunch_duration_sec": 3600,' ||
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
  'asterisk-support-taxi',
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
    '"type": "action", "actions": ["mail"], "key": "mail", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.0,' ||
     '"tracker_corp_users": 2.0' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "action", "actions": ["sms"], "key": "sms", ' ||
    '"cost_by_line": {' ||
     '"__default__": 0.0,' ||
     '"tracker_dtpStrahovanie": 1.5,' ||
     '"tracker_corp_users": 2.5' ||
    '}' ||
   '},' ||
   '{' ||
    '"type": "call", "key": "sip_call", "min_duration": 16, ' ||
    '"direction": "outgoing", "status_completed": "bridged", ' ||
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
    '"lunch_duration_sec": 3600,' ||
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
    start_date,
    stop_date,
    repeat,
    countries,
    logins,
    status,
    rule_type,
    tariff_type
) VALUES (
    'periodic_rule_id',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru', 'md'],
    NULL,
    'waiting_agent',
    'regular',
    'asterisk-support-taxi'
),
(
    'dismissal_rule_id',
    '2020-01-01'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru', 'md'],
    ARRAY['ivanov', 'petrov', 'smirnoff', 'popov', 'popov2'],
    'waiting_agent',
    'dismissal',
    'asterisk-support-taxi'
),
(
    'dismissal_rule_id_start',
    '2020-01-16'::DATE,
    '2020-01-16'::DATE,
    True,
    ARRAY['ru', 'md'],
    ARRAY['ivanov', 'petrov', 'smirnoff', 'popov', 'popov2'],
    'waiting_agent',
    'dismissal',
    'asterisk-support-taxi'
 )
;

INSERT INTO taxi_ods_support_chatterbox.startrack_sip_calls
VALUES
    ('call_id_1', 'ivanov@prod.prod', 'dtpStrahovanie', '2020-01-01T06:00:00', '2020-01-01T06:01:00', '2020-01-01T06:02:00', 'bridged', 'outgoing'),
    ('call_id_2', 'ivanov@prod.prod', 'dtpStrahovanie', '2020-01-01T06:00:00', '2020-01-01T06:01:00', '2020-01-01T06:01:01', 'bridged', 'outgoing'),
    ('call_id_3', 'ivanov@prod.prod', 'dtpStrahovanie', '2020-01-01T06:00:00', '2020-01-01T06:01:00', '2020-01-01T06:02:00', 'failed', 'outgoing'),
    ('call_id_4', 'ivanov@prod.prod', 'dtpStrahovanie', '2020-01-01T06:00:00', '2020-01-01T06:01:00', '2020-01-01T06:02:00', 'bridged', 'incoming'),
    ('call_id_5', 'ivanov@prod.prod', 'corp_users', '2020-01-01T16:00:00', '2020-01-01T16:01:00', '2020-01-01T16:02:00', 'bridged', 'outgoing'),
    ('call_id_6', 'petrov@prod.prod', 'corp_users', '2020-01-01T16:00:00', '2020-01-01T16:01:00', '2020-01-01T16:02:00', 'bridged', 'outgoing'),
    ('call_id_7', 'unknown@prod.prod', 'dtpStrahovanie', '2020-01-01T16:00:00', '2020-01-01T16:01:00', '2020-01-01T16:02:00', 'bridged', 'outgoing'),
    ('call_id_8', 'smirnoff@prod.prod', 'dtpStrahovanie', '2020-01-10T06:00:00', '2020-01-10T06:01:00', '2020-01-10T06:02:00', 'bridged', 'outgoing'),
    ('call_id_9', 'smirnoff@prod.prod', 'dtpStrahovanie', '2020-01-10T16:00:00', '2020-01-10T16:01:00', '2020-01-10T16:02:00', 'bridged', 'outgoing');

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
    (default, 'ivanov', 'Europe/Moscow', 'Head of "support department".', '2020-01-01'::DATE, '2020-01-10T00:00:00', '9999-12-31T23:59:59'),
    (default, 'petrov', 'Europe/Kiev', 'support', '2020-01-01'::DATE, '2020-01-01T00:00:00', '2020-01-16T00:00:00'),
    (default, 'petrov', 'Europe/Moscow', 'support', '2020-01-01'::DATE, '2020-01-16T00:00:00', '2020-02-01T00:00:00'),
    (default, 'petrov', 'Europe/Kiev', 'support', '2020-02-01'::DATE, '2020-02-01T00:00:00', '9999-12-31T23:59:59'),
    (default, 'smirnoff', 'Europe/Volgograd', 'support', '2020-01-01'::DATE, '2020-01-01T00:00:00', '9999-12-31T23:59:59'),
    (default, 'popov', NULL, 'support', '2020-01-01'::DATE, '2020-01-01T00:00:00', '9999-12-31T23:59:59'),
    (default, 'ivanov', 'Europe/Moscow', 'head_of_support_department', '2020-01-16'::DATE, '2019-12-31T00:00:00', '9999-12-31T23:59:59'),
    (default, 'petrov', 'Europe/Kiev', 'support', '2020-01-16'::DATE, '2019-12-31T00:00:00', '9999-12-31T23:59:59'),
    (default, 'smirnoff', 'Europe/Volgograd', 'support', '2020-01-16'::DATE, '2019-12-31T00:00:00', '9999-12-31T23:59:59'),
    (default, 'popov', NULL, 'support', '2020-01-16'::DATE, '2019-12-31T00:00:00', '9999-12-31T23:59:59'),
    (default, 'popov2', NULL, 'support', '2020-01-01'::DATE, '2020-01-15T04:15:46', '2020-01-16T04:16:15'),
    (default, 'popov2', NULL, 'support', '2020-01-16'::DATE, '2020-01-16T04:16:16', '9999-12-31T23:59:59');


INSERT INTO taxi_cdm_contactcenter.dm_operator_quality_metric VALUES
    (NOW(), 'ivanov', 285, 3, 3, 232.5, 1, '2020-01-03', 0),
    (NOW(), 'petrov', 288, 3, 3, 236.25, Null, '2020-01-05', 0),
    (NOW(), 'popov2', 288, 3, 3, 236.25, 0, '2020-01-05', 0);

INSERT INTO taxi_cdm_piecework.rep_operator_activity_halfhourly VALUES
    ('2019-12-31T20:30:00.000000', 'ivanov', 'test1', 4, true, false, true, 'call', true, true),
    ('2019-12-31T21:00:00.000000', 'ivanov', 'test1', 4, true, false, true, 'call', true, true),
    ('2020-01-01T011:00:00.000000', 'ivanov', 'test2', 3, true, false, true, 'call', true, true),
    ('2020-01-01T015:00:00.000000', 'ivanov', 'test1', 1, false, false, true, 'call', true, true),
    ('2020-01-01T015:00:00.000000', 'ivanov', 'test1', 1, false, false, false, 'call', true, true),
    ('2020-01-01T015:00:00.000000', null, 'test1', 1, false, false, true, 'call', true, true),
    ('2020-01-01T015:00:00.000000', 'ivanov', null, 1, false, false, true, 'call', true, true),
    ('2020-01-01T015:30:00.000000', 'ivanov', 'test1', 1, false, null, true, 'call', true, true),
    ('2020-01-01T016:00:00.000000', 'ivanov', 'test1', 1, false, false, true, 'call', true, true),
    ('2020-01-01T015:00:00.000000', 'ivanov', 'test1', 3, false, true, true, 'call', true, true),
    ('2020-01-15T20:30:00.000000', 'ivanov', 'test1', 2, true, false, true, 'call', true, true),
    ('2019-01-16T00:00:00.000000', 'ivanov', 'test1', 1, true, false, true, 'call', true, true),
    ('2019-12-30T23:30:00.000000', 'ivanov', 'test1', 1, true, false, true, 'call', true, true),
    ('2020-01-15T011:00:00.000000', 'ivanov', 'test1', 2, false, true, true, 'call', true, true),
    ('2019-12-31T20:30:00.000000', 'ivanov', 'test1', 4, true, false, true, 'call', false, true),
    ('2019-12-31T21:00:00.000000', 'ivanov', 'test1', 4, true, false, true, 'call', false, true),
    ('2020-01-01T011:00:00.000000', 'ivanov', 'test2', 3, true, false, true, 'call', false, true),
    ('2020-01-01T015:00:00.000000', 'ivanov', 'test1', 3, false, false, true, 'call', false, true),
    ('2020-01-01T015:00:00.000000', 'ivanov', 'test1', 3, false, true, true, 'call', false, true),
    ('2020-01-15T20:30:00.000000', 'ivanov', 'test1', 2, true, false, true, 'call', false, true),
    ('2019-01-16T00:00:00.000000', 'ivanov', 'test1', 1, true, false, true, 'call', false, true),
    ('2019-12-30T23:30:00.000000', 'ivanov', 'test1', 1, true, false, true, 'call', false, true),
    ('2020-01-15T011:00:00.000000', 'ivanov', 'test1', 2, false, true, true, 'call', false, true),
    ('2020-01-01T011:00:00.000000', 'popov', 'test2', 3, true, false, true, 'call', true, true),
    ('2020-01-01T011:00:00.000000', 'popov2', 'test2', 3, true, false, true, 'call', true, true);
