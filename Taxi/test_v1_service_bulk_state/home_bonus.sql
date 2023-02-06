INSERT INTO config.completion_bonuses
  (mode_id, period,       image,   tanker_key)
VALUES
  (1,       '10 minutes', 'image', 'bonus.tanker')
;

INSERT INTO state.sessions
  (session_id, active, completed, point_id, start,                        "end",                        bonus_until,                  driver_id_id,           mode_id, destination_point)
VALUES
  (2010,       True,   True,      104,      '2018-10-12T16:03:45.540859', '2018-10-12T16:04:45.540859', '2018-10-12T16:14:45.540859', IdId('888', 'dbid777'), 1,       (3, 4)::db.geopoint),
  (2011,       True,   True,      102,      '2018-10-12T16:08:45.540859', '2018-10-12T16:12:45.540859', '2018-10-12T16:22:45.540859', IdId('888', 'dbid777'), 1,       (3, 7)::db.geopoint);
