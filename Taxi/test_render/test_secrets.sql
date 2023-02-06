INSERT INTO secrets.groups (
  name,
  secret_uuid,
  version_uuid,
  env,
  service_name
)
VALUES (
  'test_group_1',
  'auth_secret_uuid_1',
  'auth_version_uuid_1',
  'unstable',
  'test_service'
),
(
  'test_group_3',
  'auth_secret_uuid_3',
  'auth_version_uuid_3',
  'unstable',
  'test_service_1'
),
(
  'test_group_5',
  'auth_secret_uuid_5',
  'auth_version_uuid_5',
  'unstable',
  'test_service_2'
),
(
  'test_group_6',
  'auth_secret_uuid_6',
  'auth_version_uuid_6',
  'unstable',
  'test_service_3'
),
(
  'test_group_7',
  'auth_secret_uuid_7',
  'auth_version_uuid_7',
  'unstable',
  'test_service_6'
),
(
  'test_group_8',
  'auth_secret_uuid_8',
  'auth_version_uuid_8',
  'unstable',
  'test_service_4'
),
(
  'test_group_9',
  'auth_secret_uuid_9',
  'auth_version_uuid_9',
  'testing',
  'test_service_2'
),
(
  'test_group_10',
  'auth_secret_uuid_10',
  'auth_version_uuid_10',
  'unstable',
  'test_service_5'
),
(
  'taxi:some-service:unstable',
  'auth_secret_uuid_5',
  'auth_version_uuid_5',
  'unstable',
  'test_service_2'
);

INSERT INTO secrets.templates (
  service_name,
  type_name,
  content,
  updated
)
VALUES (
  'test_service_1',
  'secdist',
  'mongo_settings',
  150
),
(
  'test_service_2',
  'secdist',
  '{{ TEST_1 }}',
  150
),
(
  'test_service_3',
  'secdist',
  '{{ UNKNOWN }}',
  150
),
(
  'test_service_4',
  'secdist',
  '{{{ TEST_2 }}',
  150
),
(
  'test_service_5',
  'secdist',
  '{{ TEST_1 }}',
  350
),
(
  'test_service_6',
  'secdist',
  '{{ TEST_2 }}',
  150
),
(
  '_default',
  'audit_secrets',
  'really common audit secret',
  150
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
  'unstable'
),
(
  'TEST_2',
  'YAV_UUID_2',
  'VERSION_UUID_2',
  'mongodb',
  250,
  'unstable'
),
(
  'MONGODB_TAXI_STRONGBOX',
  'YAV_UUID_2',
  'VERSION_UUID_2',
  'mongodb',
  250,
  'testing'
);
