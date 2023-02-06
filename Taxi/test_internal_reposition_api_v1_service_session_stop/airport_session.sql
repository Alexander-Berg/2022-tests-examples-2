INSERT INTO settings.points (
  point_id,
  mode_id,
  driver_id_id,
  updated,
  name,
  address,
  city,
  location,
  offer_id
) VALUES (
  102,
  1,
  IdId('uuid2', 'dbid777'),
  '01-09-2020',
  'pg_point_3',
  'some address',
  'Postgresql',
  (3, 4)::db.geopoint,
  NULL
);

INSERT INTO state.sessions (
  session_id,
  active,
  point_id,
  start,
  driver_id_id,
  mode_id,
  destination_point
) VALUES (
  1002,
  True,
  102,
  '2020-09-01T11:00:00',
  IdId('uuid2', 'dbid777'),
  1,
  (3, 4)::db.geopoint
);
