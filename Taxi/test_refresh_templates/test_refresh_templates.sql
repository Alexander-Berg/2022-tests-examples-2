INSERT INTO secrets.templates (
  service_name,
  type_name,
  content,
  updated
)
VALUES (
  'test_service_1',
  'secdist',
  'test_content_1',
  100
),
(
  'test_service_3',
  'secdist',
  'old_content',
  200
);

INSERT INTO secrets.secrets (
    key,
    secret_uuid,
    version_uuid,
    updated,
    type,
    env
)
VALUES (
  'MONGODB_TEST',
  'YAV_UUID_1',
  'VERSION_UUID_1',
  150,
  'mongodb',
  'unstable'
), (
  'MONGODB_TEST',
  'YAV_UUID_2',
  'VERSION_UUID_2',
  150,
  'mongodb',
  'testing'
),(
  'MONGODB_TEST',
  'YAV_UUID_3',
  'VERSION_UUID_3',
  150,
  'mongodb',
  'production'
), (
  'TEST_VALUE',
  'YAV_UUID_4',
  'VERSION_UUID_4',
  150,
  'api_token',
  'production'
), (
  'DELETED_KEY_IN_TEMPLATE',
  'YAV_UUID_5',
  'VERSION_UUID_5',
  150,
  'api_token',
  'production'
)
;

INSERT INTO secrets.secrets_templates (secret_id, template_id)
VALUES (4, 1), (5, 1), (5, 2)
;
