INSERT INTO settings.driver_ids (driver_id) VALUES
(('dbid777','888')),
(('1488','driverSS')),
(('1488','driverSS2')),
(('pg_park','pg_driver')),
(('dbid','uuid')),
(('dbid','uuid1')),
(('dbid','uuid2')),
(('dbid777','uuid')),
(('dbid777','uuid1')),
(('dbid777','uuid2')),
(('dbid777','uuid3')),
(('dbidparis','uuid2')) ON CONFLICT DO NOTHING;

INSERT INTO etag_data.states (driver_id_id, valid_since, is_sequence_start, data)
SELECT driver_id_id, '2019-11-05T11:00:00', true, '{}' FROM settings.driver_ids;

CREATE OR REPLACE FUNCTION IdId(uuid TEXT, dbid TEXT)
RETURNS integer AS $$
  SELECT driver_id_id FROM settings.driver_ids WHERE (driver_id).uuid = uuid AND (driver_id).dbid = dbid $$ LANGUAGE SQL;
