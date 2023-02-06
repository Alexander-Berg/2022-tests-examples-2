INSERT INTO secrets.templates (
  service_name,
  type_name,
  content,
  updated,
  pull_number
)
VALUES (
  'test_service_1',
  'secdist',
  '',
  150,
  1
),
(
  'test_service_2',
  'secdist',
  '{"key" : "value"}'||E'\n',
  150,
  2
),
(
  'test_service_3',
  'secdist',
  '',
  150,
  NULL
);

INSERT INTO secrets.secrets (
    key,
    secret_uuid, -- ID секрета в Секретнице
    version_uuid,
    type,
    updated,
    env
)
VALUES (
  'TEST_1',
  'YAV_UUID_1',
  'VERSION_UUID_1',
  'mongodb',
  250,
  'production'
),
(
  'TEST_2',
  'YAV_UUID_1',
  'VERSION_UUID_1',
  'mongodb',
  250,
  'production'
),
(
  'TEST_3',
  'YAV_UUID_1',
  'VERSION_UUID_1',
  'mongodb',
  250,
  'unstable'
);
