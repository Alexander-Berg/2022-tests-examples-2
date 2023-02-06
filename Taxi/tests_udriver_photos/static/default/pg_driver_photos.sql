INSERT INTO driver_photos(id, driver_id, photo_name, group_id, photo_type, photo_status, created_at, park_id, driver_profile_id, priority)
VALUES

('114', '64256bf766d749fb905ff4d9', '324',     '108', 'avatar',   'need_moderation', '2018-12-24T11:00:00+03:00', '345', '456', 'admin'),
('115', '64256bf766d749fb905ff4d9', '324',     '108', 'portrait', 'need_moderation', '2018-12-24T11:00:00+03:00', '345', '456', 'admin');

INSERT INTO driver_photos(id, driver_id, photo_name, group_id, photo_type, photo_status, created_at, park_id, driver_profile_id, priority, reason)
VALUES
('142', 'rejected_no_reason_driver_id', '191', '108', 'avatar', 'rejected', '2017-12-24T11:00:00+03:00', '3456',  '4567',  'taximeter',  null),
('127', '34256bf766d749fb905ff4d9', '191', '108', 'avatar',   'rejected', '2017-12-24T11:00:00+03:00', '3456',  '4567',  'admin',  null),
('128', '34256bf766d749fb905ff4d9', '191', '108', 'portrait', 'rejected', '2017-12-24T11:00:00+03:00', '3456',  '4567',  'admin',  null),
('117', '34256bf766d749fb905ff4d9', '091', '108', 'avatar',   'approved', '2018-12-24T11:00:00+03:00', '3456',  '4567',  'admin',  null),
('118', '34256bf766d749fb905ff4d9', '091', '108', 'portrait', 'approved', '2018-12-24T11:00:00+03:00', '3456',  '4567',  'admin',  null),
('122', '34256bf766d749fb905ff4d8', '092', '108', 'avatar', 'rejected', '2018-12-24T11:00:00+03:00', '2345',  '3456',  'admin', 'no_person'),
('27',  '34256bf766d749fb905ff4d0', '093', '108', 'avatar', 'rejected', '2018-12-24T11:00:00+03:00', '2345',  '3456',  'admin', 'need_biometry'),
('28',  '34256bf766d749fb905ff4d1', '094', '108', 'avatar', 'rejected', '2018-12-24T11:00:00+03:00', '2345',  '3456',  'admin', null),
('29',  '34256bf766d749fb905ff4d1', '095', '108', 'avatar', 'approved', '2019-12-24T11:00:00+03:00', '2345',  '3456',  'taximeter', null),
('130', '34256bf766d749fb905ff4d2', '948', '108', 'avatar', 'rejected', '2018-12-24T11:00:00+03:00', '23457', '34568', 'admin', 'too_small'),
('131', '34256bf766d749fb905ff4d3', '949', '108', 'avatar', 'rejected', '2018-12-24T11:00:00+03:00', '23457', '34568', 'admin', 'wrong_photo_format'),
('132', '34256bf766d749fb905ff4d4', '950', '108', 'avatar', 'rejected', '2018-12-24T11:00:00+03:00', '23457', '34568', 'taximeter', 'studio_dark');


INSERT INTO driver_photos(id, driver_id, photo_name, group_id, photo_type, photo_status, created_at, park_id, driver_profile_id, priority, reason)
VALUES
('235', '34256bf766d749fb905ff442', '730', '108', 'avatar',   'approved',      '2019-11-21T11:00:00+03:00', '1112',   '2221',             'taximeter', null),
('236', '34256bf766d749fb905ff442', '731', '108', 'portrait', 'approved',      '2019-11-21T11:00:00+03:00', '1112',   '2221',             'taximeter', null);
