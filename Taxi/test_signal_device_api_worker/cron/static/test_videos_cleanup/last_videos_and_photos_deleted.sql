-- last_videos_and_photos_deleted table must contain only 1 row
INSERT INTO signal_device_api.last_videos_and_photos_deleted (
  last_deleted_photo_at,
  last_deleted_video_at,
  last_deleted_event_type,
  updated_at
) VALUES (
  '2020-10-01T00:00:00+03:00',
  '2020-10-01T00:00:00+03:00',
  '__default__',
  CURRENT_TIMESTAMP
),
(
  '2020-11-01T00:00:00+03:00',
  '2020-11-01T00:00:00+03:00',
  'distraction',
  CURRENT_TIMESTAMP
),
(
  '2020-09-01T00:00:00+03:00',
  '2020-09-01T00:00:00+03:00',
  'fart',
  CURRENT_TIMESTAMP
),
(
  '2016-01-01T00:00:00+03:00',
  '2020-05-01T00:00:00+03:00',
  'seatbelt',
  CURRENT_TIMESTAMP
),
(
  '2020-12-01T00:00:00+03:00',
  '2016-01-01T00:00:00+03:00',
  'sleep',
  CURRENT_TIMESTAMP
);
