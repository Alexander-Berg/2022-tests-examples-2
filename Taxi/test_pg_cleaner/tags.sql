INSERT INTO state.uploading_tags (
  tags_id,
  udid,
  merge_policy,
  confirmation_token,
  tags,
  ttl,
  uploading,
  uploaded,
  provider,
  created_at
)
VALUES
(
  1000,
  '000000000000000000000011',
  'any_merge_policy',
  'any_token',
  '{"tag_0", "tag_1"}',
  '2019-09-01T13:30:00',
  '2019-09-01T12:59:30',
  True,
  ('reposition')::db.tags_provider,
  '2019-09-01T12:30:00'
),
(
  1001,
  '000000000000000000000011',
  'any_merge_policy',
  'any_token',
  '{"tag_0", "tag_1"}',
  '2019-09-01T12:30:00',
  NULL,
  False,
  ('reposition')::db.tags_provider,
  '2019-09-01T12:30:00'
),
(
  1002,
  '000000000000000000000011',
  'any_merge_policy',
  'any_token',
  '{"tag_0", "tag_1"}',
  '2019-09-01T13:30:00',
  NULL,
  False,
  ('reposition')::db.tags_provider,
  '2019-09-01T12:30:00'
);