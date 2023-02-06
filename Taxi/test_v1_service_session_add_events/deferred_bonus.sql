INSERT INTO settings.points(
  point_id, mode_id, driver_id_id,        updated,      name,         address,         city,        location,              offer_id
) VALUES (
  2001,     1,       IdId('uuid','dbid'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (30, 60)::db.geopoint, NULL
);

INSERT INTO config.completion_bonuses(
  mode_id, period,       image,   tanker_key
) VALUES (
  1,       '10 minutes', 'image', 'bonus.tanker'
);

INSERT INTO state.sessions(
  session_id, point_id, active, completed, start,                     "end",                     bonus_until,               driver_id_id,        mode_id, destination_point
) VALUES (
  3001,       2001,     false,  true,      '2017-11-19T16:47:54.721', '2017-11-19T17:00:00.000', '2017-11-19T22:00:00.000', IdId('uuid','dbid'), 1,       (30, 60)::db.geopoint
);
