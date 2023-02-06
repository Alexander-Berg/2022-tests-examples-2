INSERT INTO secrets.groups (
  name,
  secret_uuid,
  version_uuid,
  env,
  service_name
)
VALUES (
  'taxi:imports:unstable',
  'auth_secret_uuid_1',
  'auth_version_uuid_1',
  'unstable',
  'imports'
)
;
