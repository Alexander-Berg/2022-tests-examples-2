INSERT INTO settings.points
  (point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id)
VALUES
  (101,      3, IdId('888', 'dbid777'), '09-01-2018', 'pg_point_1', 'some address', 'Postgresql', (3, 4)::db.geopoint, NULL);

INSERT INTO state.sessions
  (session_id, active, point_id, start,                        "end",                        driver_id_id,             mode_id, submode_id, destination_point,   session_deadline, disable_reason)
VALUES
  (2001,       False,  101,      '2018-10-11T16:01:11.540859', NULL,                         IdId('888', 'dbid777'),   3,       NULL,       (3, 4)::db.geopoint, NULL, 'Immobility')
;
