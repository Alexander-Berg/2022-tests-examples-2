INSERT INTO driver_options.drivers
(id, park_driver_profile_id, etag, finished_etag)
VALUES
(10, 'park_id1_uuid1', '123', '123');

INSERT INTO driver_options.options
(driver_options_id, name, is_active)
VALUES
(10, 'thermobag', True),
(10, 'thermopack', False);
