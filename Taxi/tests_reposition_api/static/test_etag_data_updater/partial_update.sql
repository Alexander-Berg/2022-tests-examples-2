DELETE FROM etag_data.drivers_update_state;
INSERT INTO etag_data.drivers_update_state
VALUES
  (IdId('uuid', 'dbid777')),
  (IdId('uuid1', 'dbid777')),
  (IdId('uuid2', 'dbid777')),
  (IdId('uuid3', 'dbid777')),
  (IdId('driverSS','1488'))
;

UPDATE etag_data.drivers_update_state
SET
  updating = '2018-11-26T21:53:00',
  updated_at = '2018-11-26T21:53:00'
WHERE driver_id_id = IdId('uuid', 'dbid777');

UPDATE etag_data.drivers_update_state
SET
  updating = '2018-11-26T21:54:00',
  updated_at = '2018-11-26T21:54:00'
WHERE driver_id_id = IdId('uuid1', 'dbid777');

UPDATE etag_data.drivers_update_state
SET
  updating = '2018-11-26T21:55:00',
  updated_at = '2018-11-26T21:55:00'
WHERE driver_id_id = IdId('uuid2', 'dbid777');

UPDATE etag_data.drivers_update_state
SET
  updating = '2018-11-26T21:56:00',
  updated_at = '2018-11-26T21:56:00'
WHERE driver_id_id = IdId('uuid3', 'dbid777');

UPDATE etag_data.drivers_update_state
SET
  updating = '2018-11-26T21:57:00',
  updated_at = '2018-11-26T21:57:00'
WHERE driver_id_id = IdId('driverSS','1488');
