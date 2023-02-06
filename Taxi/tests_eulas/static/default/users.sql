-- noinspection SqlNoDataSourceInspectionForFile

/* V1 */
-- enabled_at timestamptz, disabled_at timestamptz

INSERT INTO eulas.users
(yandex_uid, eula_id, status, valid_till, updated_at)
VALUES
(
  '1',
  'a',
  'accepted',
  '2020-02-26 19:11:13 +03:00',
  '2018-01-01 19:11:13 +03:00'
),
(
  '1',
  'b',
  'rejected',
  '2019-02-26 19:11:13 +03:00',
  '2017-01-01 19:11:13 +03:00'
),
(
  '2',
  'b',
  'accepted',
  '2019-02-26 19:11:13 +03:00',
  '2018-01-01 19:11:13 +03:00'
),
(
  '3',
  'c',
  'rejected',
  '2019-02-26 19:11:13 +03:00',
  CURRENT_TIMESTAMP
);
