INSERT INTO drivers_status_ranges.status_ranges
  (clid_uuid, range_begin, range_end, status, license_id)
VALUES
  ('park1_driver1', '2019-04-05 01:01:00', '2019-04-05 01:12:25', 'free', '9900530551'),
  ('park1_driver2', '2019-04-05 01:10:00', '2019-04-05 01:12:45', 'free', '9900530552'),
  ('park1_driver3', '2019-04-04 00:30:00', '2019-04-04 00:52:00', 'busy', '9900530553'),
  ('park1_driver3', '2019-04-05 02:30:00', '2019-04-05 02:52:00', 'busy', '9900530553');
