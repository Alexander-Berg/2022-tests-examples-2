INSERT INTO etag_data.update_requests
(
  update_state,
  update_modes,
  update_offered_modes,
  created_at,
  started_at,
  finished_at,
  cancelled
)
VALUES
(
  true,
  true,
  true,
  '2019-11-05T11:00:00',
  '2019-11-05T11:05:00',
  '2019-11-05T11:30:00',
  false
),
(
  false,
  true,
  false,
  '2019-11-05T11:35:00',
  '2019-11-05T11:40:00',
  '2019-11-05T11:55:00',
  false
),
(
  true,
  true,
  true,
  '2019-11-05T11:55:00',
  '2019-11-05T12:00:00',
  NULL,
  false
),
(
  true,
  false,
  true,
  '2019-11-05T11:57:00',
  NULL,
  NULL,
  true
),
(
  true,
  true,
  false,
  '2019-11-05T11:58:00',
  NULL,
  NULL,
  true
),
(
  false,
  true,
  false,
  '2019-11-05T12:00:00',
  NULL,
  NULL,
  false
);

UPDATE etag_data.drivers_update_state
SET
  updating = '2019-11-05T00:00:00',
  updated_at = '2019-11-05T00:00:00';

UPDATE etag_data.drivers_update_state
SET
  updating = '2019-11-05T12:00:00',
  updated_at = '2019-11-05T12:00:00'
WHERE
  driver_id_id IN (1, 2, 3, 4, 5);
