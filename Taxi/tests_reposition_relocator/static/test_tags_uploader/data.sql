INSERT INTO state.uploading_tags (
  driver_id,
  merge_policy,
  tags,
  created_at,
  until
) VALUES (
  ('dbid1','uuid1'),
  'append',
  ARRAY['reposition_offer_sent'],
  '2020-05-18T12:00:00',
  '2020-05-18T15:00:00'
), (
  ('dbid2','uuid2'),
  'append',
  ARRAY['reposition_offer_sent'],
  '2020-05-18T12:00:00',
  '2020-05-18T15:00:00'
), (
  ('dbid3','uuid3'),
  'append',
  ARRAY['reposition_offer_sent'],
  '2020-05-18T12:00:00',
  '2020-05-18T15:00:00'
), (
  ('dbid4','uuid4'),
  'append',
  ARRAY['reposition_offer_sent'],
  '2020-05-18T11:00:00',
  '2020-05-18T11:30:00'
);
