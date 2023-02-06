INSERT INTO driver_photos(id, driver_id, photo_name, group_id, photo_type, photo_status, created_at, park_id, driver_profile_id, priority)
VALUES
('1',   '54256bf766d93ee2c902dcbd', '111',     '603', 'avatar',   'approved', '2018-11-24T11:00:00+03:00',         null,  null, 'admin'),
('12',  '54256bf766d93ee2c902dcbd', '112',     '603', 'avatar',   'approved', '2014-11-24T11:00:00+03:00',         null,  null, 'admin'),
('13',  '54256bf766d93ee2c902dcbd', '113',     '603', 'avatar',   'approved', '2020-11-24T11:00:00+03:00',         null,  null, 'admin'),
('2',   '54256bf766d93ee2c902dcbd', '222',     '603', 'portrait', 'approved', '2018-11-24T11:00:00+03:00',         null,  null, 'admin'),
('3',   '54256bf766d93ee2c902dcbd', '333',     '603', 'original', 'approved', '2018-11-24T11:00:00+03:00',         null,  null, 'admin'),
('4',   '54256bf766d93ee2c902dcbd', '777',     '603', 'avatar',   'approved', '2017-11-24T11:00:00+03:00',         null,  null, 'admin'),
('5',   '54256bf766d93ee2c902dcbd', '888',     '603', 'portrait', 'approved', '2019-11-24T11:00:00+03:00',         null,  null, 'admin'),
('6',   '54256bf766d93ee2c902dcbd', '999',     '603', 'original', 'approved', '2016-11-24T11:00:00+03:00',         null,  null, 'admin'),
('7',   '54256bf766d93ee2c902dcbd', '999',     '603', 'avatar',   'new',      '2016-11-24T11:00:00+03:00',         null,  null, 'admin'),
('8',   '54256bf766d93ee2c902dcbd', '999',     '603', 'portrait', 'rejected', '2016-11-24T11:00:00+03:00',         null,  null, 'admin'),
('9',   '54256bf766d93ee2c902dcbd', '999',     '603', 'original', 'new',      '2016-11-24T11:00:00+03:00',         null,  null, 'admin'),
('10',  '54256bf766d93ee2c902dcbd', '999',     '603', 'original', 'rejected', '2016-12-24T11:00:00+03:00',         null,  null, 'admin'),

('900', '4c380d9f8c2749fb905ff4d9', '444',     '800', 'avatar',   'approved', '2016-11-24T11:00:00+03:00',         null,  null, 'admin'),
('901', '4c380d9f8c2749fb905ff4d9', '555',     '800', 'portrait', 'approved', '2016-11-24T11:00:00+03:00',         null,  null, 'admin'),
('902', '4c380d9f8c2749fb905ff4d9', '666',     '800', 'original', 'approved', '2016-11-24T11:00:00+03:00',         null,  null, 'admin'),

('100', '4c380d9f8c2749fb905ff4d9', 'nirvana', '800', 'avatar',   'on_moderation', '2016-11-24T11:00:00+03:00',    null,  null, 'admin'),
('101', '4c380d9f8c2749fb905ff4d9', 'nirvana', '800', 'portrait', 'on_moderation', '2016-11-24T11:00:00+03:00',    null,  null, 'admin'),
('102', '4c380d9f8c2749fb905ff4d9', 'nirvana', '800', 'original', 'on_moderation', '2016-11-24T11:00:00+03:00',    null,  null, 'admin'),

('108', '4c380d9f8c273ee2c902dcbd', '108',     '108', 'avatar',   'need_moderation', '2016-12-24T11:00:00+03:00', '123', '234', 'admin'),
('109', '4c380d9f8c273ee2c902dcbd', '108',     '108', 'portrait', 'need_moderation', '2016-12-24T11:00:00+03:00', '123', '234', 'admin'),
('110', '4c380d9f8c273ee2c902dcbd', '108',     '108', 'original', 'need_moderation', '2016-12-24T11:00:00+03:00', '123', '234', 'admin'),
('111', '54256d9f8c2749fb905ff4d9', '216',     '108', 'avatar',   'need_moderation', '2017-12-24T11:00:00+03:00', '123', '234', 'admin'),
('112', '54256d9f8c2749fb905ff4d9', '216',     '108', 'portrait', 'need_moderation', '2017-12-24T11:00:00+03:00', '123', '234', 'admin'),
('113', '54256d9f8c2749fb905ff4d9', '216',     '108', 'original', 'need_moderation', '2017-12-24T11:00:00+03:00', '123', '234', 'admin'),
('114', '64256bf766d749fb905ff4d9', '324',     '108', 'avatar',   'need_moderation', '2018-12-24T11:00:00+03:00', '345', '456', 'admin'),
('115', '64256bf766d749fb905ff4d9', '324',     '108', 'portrait', 'need_moderation', '2018-12-24T11:00:00+03:00', '345', '456', 'admin'),
('116', '64256bf766d749fb905ff4d9', '324',     '108', 'original', 'need_moderation', '2018-12-24T11:00:00+03:00', '345', '456', 'admin');

INSERT INTO driver_photos(id, driver_id, photo_name, group_id, photo_type, photo_status, created_at, park_id, driver_profile_id, priority, reason)
VALUES
('235', '34256bf766d749fb905ff442', '730', '108', 'avatar',   'approved',      '2019-11-21T11:00:00+03:00', '1112',   '2221',             'taximeter', null),
('236', '34256bf766d749fb905ff442', '731', '108', 'portrait', 'approved',      '2019-11-21T11:00:00+03:00', '1112',   '2221',             'taximeter', null),
('237', '34256bf766d749fb905ff442', '732', '108', 'original', 'approved',      '2019-11-21T11:00:00+03:00', '1112',   '2221',             'taximeter', null),
('238', '34256bf766d749fb905ff000', '733', '108', 'avatar',   'on_moderation', '2019-11-26T11:00:00+03:00', 'park_2', 'driver_profile_2', 'taximeter', null),
('239', '34256bf766d749fb905ff000', '734', '108', 'portrait', 'on_moderation', '2019-11-26T10:00:00+03:00', 'park_2', 'driver_profile_2', 'taximeter', null),
('240', '34256bf766d749fb905ff000', '735', '108', 'original', 'on_moderation', '2019-11-26T09:00:00+03:00', 'park_2', 'driver_profile_2', 'taximeter', null),

('242', 'unique_driver_3',          '833', '108', 'avatar',   'approved',      '2019-11-26T11:00:00+03:00', 'park_3', 'driver_profile_3', 'taximeter', null),
('243', 'unique_driver_3',          '834', '108', 'portrait', 'approved',      '2019-11-26T10:00:00+03:00', 'park_3', 'driver_profile_3', 'taximeter', null),
('244', 'unique_driver_3',          '835', '108', 'original', 'approved',      '2019-11-26T09:00:00+03:00', 'park_3', 'driver_profile_3', 'taximeter', null),
('245', 'unique_driver_3',          '836', '108', 'avatar',   'on_moderation', '2019-12-26T11:00:00+03:00', 'park_3', 'driver_profile_3', 'taximeter', null),
('246', 'unique_driver_3',          '837', '108', 'portrait', 'on_moderation', '2019-12-26T10:00:00+03:00', 'park_3', 'driver_profile_3', 'taximeter', null),
('247', 'unique_driver_3',          '838', '108', 'original', 'on_moderation', '2019-12-26T09:00:00+03:00', 'park_3', 'driver_profile_3', 'taximeter', null),

('250', 'unique_driver_4',          '833', '108', 'avatar',   'approved',      '2019-11-26T11:00:00+03:00', 'park_4', 'driver_profile_4', 'admin',     null),
('251', 'unique_driver_4',          '834', '108', 'portrait', 'approved',      '2019-11-26T10:00:00+03:00', 'park_4', 'driver_profile_4', 'admin',     null),
('252', 'unique_driver_4',          '835', '108', 'original', 'approved',      '2019-11-26T09:00:00+03:00', 'park_4', 'driver_profile_4', 'admin',     null),
('253', 'unique_driver_4',          '836', '108', 'avatar',   'on_moderation', '2019-12-26T11:00:00+03:00', 'park_4', 'driver_profile_4', 'taximeter', null),
('254', 'unique_driver_4',          '837', '108', 'portrait', 'on_moderation', '2019-12-26T10:00:00+03:00', 'park_4', 'driver_profile_4', 'taximeter', null),
('255', 'unique_driver_4',          '838', '108', 'original', 'on_moderation', '2019-12-26T09:00:00+03:00', 'park_4', 'driver_profile_4', 'taximeter', null);
