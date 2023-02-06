INSERT INTO dmi.modes(mode_id, mode) VALUES
(0, 'orders'),
(1, 'driver_fix'),
(2, 'uberdriver'),
(3, 'driver_fix1'),
(4, 'medic'),
(5, 'flexible_mode');

INSERT INTO dmi.mode_properties(properties_id, properties) VALUES
(0, '{"time_based_subvention"}');

INSERT INTO dmi.documents(
  id, park_id, driver_profile_id, external_ref, mode_id, billing_mode, billing_mode_rule, event_at, updated, properties_id
) VALUES
( 1, 'dbid1', 'uuid1',  'ext_ref01', 1, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00', 0),

( 2, 'dbid1', 'uuid2',  'ext_ref02', 0, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00', NULL),
( 3, 'dbid1', 'uuid2',  'ext_ref01', 3, 'not_used','not_used', '2020-01-02 12:00:00', '2020-01-02 12:00:00', 0),

( 4, 'dbid2', 'uuid1',  'ext_ref04', 0, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00', NULL),
( 5, 'dbid2', 'uuid1',  'ext_ref05', 1, 'not_used','not_used', '2020-01-02 12:00:00', '2020-01-02 12:00:00', 0),
( 6, 'dbid2', 'uuid1',  'ext_ref06', 2, 'not_used','not_used', '2020-01-03 12:00:00', '2020-01-03 12:00:00', NULL),
( 7, 'dbid2', 'uuid1',  'ext_ref07', 3, 'not_used','not_used', '2020-01-04 12:00:00', '2020-01-04 12:00:00', 0),
( 8, 'dbid2', 'uuid1',  'ext_ref08', 4, 'not_used','not_used', '2020-01-05 12:00:00', '2020-01-05 12:00:00', NULL),
( 9, 'dbid2', 'uuid1',  'ext_ref09', 5, 'not_used','not_used', '2020-01-06 12:00:00', '2020-01-06 12:00:00', NULL),

(10, 'dbid2', 'uuid2',  'ext_ref10', 4, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00', NULL),
(11, 'dbid2', 'uuid2',  'ext_ref11', 4, 'not_used','not_used', '2020-01-02 12:00:00', '2020-01-02 12:00:00', NULL),

(12, 'dbid3', 'uuid1',  'ext_ref12', 2, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00', NULL),
(13, 'dbid3', 'uuid1',  'ext_ref13', 0, 'not_used','not_used', '2020-01-02 12:00:00', '2020-01-02 12:00:00', NULL),
(14, 'dbid3', 'uuid1',  'ext_ref14', 2, 'not_used','not_used', '2020-01-03 12:00:00', '2020-01-03 12:00:00', NULL),


(15, 'dbid3', 'uuid2',  'ext_ref15', 5, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00', NULL),
(16, 'dbid3', 'uuid2',  'ext_ref16', 3, 'not_used','not_used', '2020-01-02 12:00:00', '2020-01-02 12:00:00', 0),
(17, 'dbid3', 'uuid2',  'ext_ref17', 2, 'not_used','not_used', '2020-01-03 12:00:00', '2020-01-03 12:00:00', NULL),

(18, 'dbid3', 'uuid3',  'ext_ref18', 3, 'not_used','not_used', '2020-01-01 12:00:00', '2020-01-01 12:00:00', 0),

(19, 'dbid3', 'uuid4',  'ext_ref19', 2, 'not_used','not_used', '2020-01-08 12:00:00', '2020-01-08 12:00:00', NULL)
;
