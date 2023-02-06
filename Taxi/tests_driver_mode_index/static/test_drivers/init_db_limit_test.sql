INSERT INTO dmi.modes(mode_id, mode) VALUES
(0, 'orders');

INSERT INTO dmi.documents(
  id, park_id, driver_profile_id, external_ref, mode_id, billing_mode, billing_mode_rule, event_at, updated
) VALUES
( 0, 'dbid1', 'uuid1',  'ext_ref01', 0, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00'),
( 1, 'dbid2', 'uuid1',  'ext_ref01', 0, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00'),
( 2, 'dbid3', 'uuid1',  'ext_ref01', 0, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00'),
( 3, 'dbid4', 'uuid1',  'ext_ref01', 0, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00'),
( 4, 'dbid5', 'uuid1',  'ext_ref01', 0, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00'),
( 5, 'dbid6', 'uuid1',  'ext_ref01', 0, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00'),
( 6, 'dbid7', 'uuid1',  'ext_ref01', 0, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00'),
( 7, 'dbid1', 'uuid2',  'ext_ref01', 0, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00')
;
