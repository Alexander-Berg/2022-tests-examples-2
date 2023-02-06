INSERT INTO dmi.modes(mode_id, mode) VALUES
(0, 'orders'),
(1, 'driver_fix'),
(2, 'uberdriver'),
(3, 'secret_mode');

INSERT INTO dmi.documents(
  id, park_id, driver_profile_id, external_ref, mode_id, billing_mode, billing_mode_rule, event_at, updated
) VALUES
( 1, 'dbid1', 'uuid1',  'ext_ref05', 0, 'orders', 'orders', '2020-01-01 12:00:00', '2020-01-01 12:00:00'),
( 2, 'dbid2', 'uuid2',  'ext_ref06', 1, 'driver_fix', 'driver_fix', '2020-01-01 12:00:00', '2020-01-01 12:00:00'),
( 3, 'dbid3', 'uuid3',  'ext_ref07', 2, 'uberdriver', 'uberdriver_v3', '2020-01-01 12:00:00', '2020-01-01 12:00:00'),
( 4, 'dbid4', 'uuid4',  'ext_ref08', 3, 'secret_mode', 'driver_fix', '2020-01-01 12:00:00', '2020-01-01 12:00:00');
