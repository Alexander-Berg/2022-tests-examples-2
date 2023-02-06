INSERT INTO settings.driver_ids
SELECT num, ('dbid', CONCAT('uuid_', num))::db.driver_id FROM generate_series(1, 100) num;

INSERT INTO settings.points
  (point_id,  mode_id, driver_id_id, updated,      name,               address,             city,         location)
SELECT
  1000 + num, 1,       num,          '09-01-2018', 'dbid777_888_home', 'some home address', 'Postgresql', (3, 4)::db.geopoint
FROM generate_series(1, 100) num;
