CREATE SCHEMA IF NOT EXISTS taxi_cdm_contactcenter;
DROP TABLE IF EXISTS taxi_cdm_contactcenter.dm_operator_quality_metric;
CREATE TABLE taxi_cdm_contactcenter.dm_operator_quality_metric (
    csat_sum NUMERIC,
    csat_cnt INT,
    operator_login VARCHAR(255),
    quality_sum NUMERIC,
    quality_cnt INT,
    claim_cnt INT,
    utc_report_dt DATE NOT NULL
);

INSERT INTO taxi_cdm_contactcenter.dm_operator_quality_metric (
    csat_sum,
    csat_cnt,
    operator_login,
    quality_sum,
    quality_cnt,
    claim_cnt,
    utc_report_dt
)
VALUES
(
    9.8,
    2,
    'support',
    145,
    2,
    0,
    '2022-02-02'
),
(
    4,
    1,
    'supersupport',
    80,
    1,
    2,
    '2022-02-03'
),
(
    null,
    null,
    'nice_support',
    99,
    1,
    1,
    '2022-02-05'
),
(
    13.5,
    3,
    'nice_support',
    270.9,
    3,
    1,
    '2022-02-10'
),
(
  null,
  null,
  'nice_support',
  30,
  1,
  1,
  '2022-02-11'
),
(
  null,
  null,
  'support',
  90,
  1,
  5,
  '2022-01-11'
),
(
  null,
  null,
  'nice_support',
  30,
  1,
  2,
  '2022-01-10'
),
(
  12,
  3,
  'nice_support',
  null,
  null,
  null,
  '2022-02-07'
);

CREATE SCHEMA IF NOT EXISTS eda_ods_oktell;
DROP TABLE IF EXISTS eda_ods_oktell.user;
CREATE TABLE eda_ods_oktell.user (
    user_id VARCHAR(255) NOT NULL,
    user_login VARCHAR(255) NOT NULL
);

INSERT INTO eda_ods_oktell.user
(user_id, user_login)
VALUES
(
    'supersupport_id',
    'supersupport'
),
(
    'bad_support_id',
    'bad_support'
),
(
    'nice_support_id',
    'nice_support'
);


DROP TABLE IF EXISTS eda_ods_oktell.dialog_result;
CREATE TABLE eda_ods_oktell.dialog_result (
    first_operator_id VARCHAR(255) NOT NULL,
    csat_value INT,
    utc_call_dttm TIMESTAMP WITHOUT TIME ZONE NOT NULL
);

INSERT INTO eda_ods_oktell.dialog_result
(first_operator_id, csat_value, utc_call_dttm)
VALUES
(
    'supersupport_id',
    5,
    '2022-02-03T15:20:00'
),
(
    'bad_support_id',
    3,
    '2022-02-04T15:20:00'
),
(
    'bad_support_id',
    2,
    '2022-02-04T16:20:00'
),
(
    'nice_support_id',
    5,
    '2022-02-05T15:00:00'
),
(
    'nice_support_id',
    4,
    '2022-02-05T15:10:00'
),
(
    'nice_support_id',
    5,
    '2022-02-06T15:10:00'
),
(
    'nice_support_id',
    5,
    '2022-02-10T15:10:00'
),
(
    'nice_support_id',
    5,
    '2022-02-10T15:20:00'
);
