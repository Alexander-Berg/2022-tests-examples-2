INSERT INTO driver_photos(id, driver_id, photo_name, group_id, photo_type, photo_status, created_at, park_id, driver_profile_id, priority, reason)
VALUES
('111',   'driver_id_1', '111',  '603',  'avatar',    'approved',       '2020-01-15T11:00:00+03:00',  'park_id_1',  'driver_profile_id_1', 'taximeter',  null),
('112',   'driver_id_1', '111',  '603',  'portrait',  'approved',       '2020-01-15T11:00:00+03:00',  'park_id_1',  'driver_profile_id_1', 'admin',      null),
('121',   'driver_id_1', '112',  '603',  'avatar',    'approved',       '2020-01-16T11:00:00+03:00',  'park_id_1',  'driver_profile_id_1', 'taximeter',  null),
('122',   'driver_id_1', '112',  '603',  'portrait',  'approved',       '2020-01-16T11:00:00+03:00',  'park_id_1',  'driver_profile_id_1', 'admin',      null),
('131',   'driver_id_1', '113',  '603',  'avatar',    'on_moderation',  '2020-01-17T11:00:00+03:00',  'park_id_1',  'driver_profile_id_1', 'taximeter',  null),
('132',   'driver_id_1', '113',  '603',  'portrait',  'on_moderation',  '2020-01-17T11:00:00+03:00',  'park_id_1',  'driver_profile_id_1', 'admin',      null),
('141',   'driver_id_1', '114',  '603',  'avatar',    'rejected',       '2020-01-18T11:00:00+03:00',  'park_id_1',  'driver_profile_id_1', 'taximeter',  'need_biometry'),
('142',   'driver_id_1', '114',  '603',  'portrait',  'rejected',       '2020-01-18T11:00:00+03:00',  'park_id_1',  'driver_profile_id_1', 'admin',      'need_biometry'),

('211',   'driver_id_2', '211',  '603',  'avatar',    'on_moderation', '2020-01-15T11:00:00+03:00',  'park_id_2',  'driver_profile_id_2', 'taximeter',  null),
('212',   'driver_id_2', '211',  '603',  'portrait',  'on_moderation', '2020-01-15T11:00:00+03:00',  'park_id_2',  'driver_profile_id_2', 'taximeter',  null),
('221',   'driver_id_2', '212',  '603',  'avatar',    'on_moderation', '2020-01-16T11:00:00+03:00',  'park_id_2',  'driver_profile_id_2', 'taximeter',  null),
('222',   'driver_id_2', '212',  '603',  'portrait',  'on_moderation', '2020-01-16T11:00:00+03:00',  'park_id_2',  'driver_profile_id_2', 'taximeter',  null),
('231',   'driver_id_2', '213',  '603',  'avatar',    'rejected',      '2020-01-17T11:00:00+03:00',  'park_id_2',  'driver_profile_id_2', 'taximeter',  'need_biometry'),

('311',   'driver_id_3', '311',  '603',  'avatar',    'rejected',      '2020-01-15T11:00:00+03:00',  'park_id_3',  'driver_profile_id_3', 'taximeter',  'need_biometry');
