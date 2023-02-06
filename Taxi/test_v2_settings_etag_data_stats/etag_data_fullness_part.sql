UPDATE etag_data.drivers_update_state
SET
  updating = '2019-11-05T00:00:00',
  updated_at = '2019-11-05T00:00:00'
WHERE
  driver_id_id IN (1, 2, 3, 4, 5);
