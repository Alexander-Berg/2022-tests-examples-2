INSERT INTO config.modes
(mode_id, mode_name, offer_only, offer_radius, min_allowed_distance, max_allowed_distance, mode_type, work_modes)
VALUES
    (1102,'poi',False,NULL, 2000, 180000, ('ToPoint')::db.mode_type, ARRAY['orders']),
    (1103,'surge',True,3.1415926535897932384626433832795, 2000, 180000, ('ToPoint')::db.mode_type, ARRAY['orders']);

INSERT INTO config.completion_bonuses(mode_id, period, image, tanker_key)
VALUES
    (1, '1h', 'image_1', 'tanker_key_1'),
    (1102, '2h', 'image_2', 'tanker_key_2'),
    (1103, '3h', 'image_3', 'tanker_key_3')
;

INSERT INTO config.tags_zones_assignments
(zone_id, mode_id, session_tags)
VALUES
    (1, 1, ARRAY['reposition_home']),
    (1, 1103, ARRAY['reposition_surge'])
;

INSERT INTO check_rules.duration (duration_id, _span, due) VALUES
    (1301, make_interval(mins => 15), NOW() + interval '1 hour');

INSERT INTO check_rules.arrival
(arrival_id, _eta, distance)
VALUES
    (1601, make_interval(secs=>5), 25);

INSERT INTO check_rules.immobility (immobility_id, min_track_speed, position_threshold, _max_immobility_time) VALUES
    (1701, 11, 22,  make_interval(secs=>33));

INSERT INTO check_rules.surge_arrival
(surge_arrival_id, time_coeff, surge_arrival_coef, min_arrival_surge, min_arrival_eta)
VALUES
    (1801,            2.0, 0.9, 0.5, make_interval(secs=>2));

INSERT INTO state.offers
(offer_id, valid_until,                image_id, description,    created,                    tariff_class, origin)
VALUES
    (1408,     '2018-11-26T09:00:00+0000', 'icon_1', 'some text #1', '2018-11-25T09:00:00+0000', 'comfort',    ('reposition-relocator')::db.offer_origin);

INSERT INTO settings.points
(point_id, mode_id, driver_id_id, updated, name, address, city, location, offer_id) VALUES
                                                                                        (1401, 1, IdId('888', 'dbid777'), '09-01-2018', 'dbid777_888_home', 'some home address', 'Postgresql', (30, 60)::db.geopoint, NULL),
                                                                                        (1402, 1102, IdId('driverSS', '1488'), '09-01-2018', '1488_driverSS_poi', 'some poi address', 'Postgresql', (30, 60)::db.geopoint, NULL),
                                                                                        (1403, 1, IdId('driverSS2', '1488'), '09-01-2018', '1488_driverSS2_home', 'some home address', 'Postgresql', (30, 60)::db.geopoint, NULL),
                                                                                        (1404, 1, IdId('pg_driver', 'pg_park'), '09-01-2018', 'pg_park_pg_driver_home', 'some home address', 'Postgresql', (30, 60)::db.geopoint, NULL),
                                                                                        (1405, 1, IdId('uuid', 'dbid'), '09-01-2018', 'dbid_uuid_home', 'some home address', 'Postgresql', (30, 60)::db.geopoint, NULL),
                                                                                        (1406, 1, IdId('uuid1', 'dbid'), '09-01-2018', 'dbid_uuid1_home', 'some home address', 'Postgresql', (30, 60)::db.geopoint, NULL),
                                                                                        (1407, 1, IdId('uuid2', 'dbid'), '09-01-2018', 'dbid_uuid2_home', 'some home address', 'Postgresql', (30, 60)::db.geopoint, NULL),
                                                                                        (1408, 1103, IdId('uuid', 'dbid777'), '09-01-2018', 'dbid777_uuid_surge', 'some surge address', 'Postgresql', (30, 60)::db.geopoint, 1408);

INSERT INTO state.sessions
(session_id, driver_id_id,      completed, active, point_id, start,              "end", mode_id, destination_point, submode_id)
VALUES
    (1501, IdId('888','dbid777'),       FALSE, TRUE,  1401, '2018-11-26T08:00:00+0000', NULL, 1, (30, 60)::db.geopoint, NULL),
    (1502, IdId('driverSS','1488'),     FALSE, TRUE,  1402, '2018-11-26T08:00:00+0000', NULL, 1102, (30.01, 60.01)::db.geopoint, NULL),
    (1503, IdId('driverSS2','1488'),    FALSE, TRUE,  1403, '2018-11-26T08:00:00+0000', '2018-11-26T08:30:00+0000', 1, (30, 60)::db.geopoint, NULL),
    (1504, IdId('pg_driver','pg_park'), FALSE, FALSE, 1404, '2018-11-26T08:00:00+0000', NULL, 1, (30, 60)::db.geopoint, NULL),
    (1505, IdId('uuid','dbid'),         FALSE, TRUE,  1405, '2018-11-26T08:00:00+0000', NULL, 1, (30, 60)::db.geopoint, 1),
    (1506, IdId('uuid1','dbid'),        FALSE, TRUE,  1406, '2018-11-26T08:00:00+0000', NULL, 1, (30, 60)::db.geopoint, NULL),
    (1507, IdId('uuid2','dbid'),        FALSE, TRUE,  1407, '2018-11-26T08:00:00+0000', NULL, 1, (30, 60)::db.geopoint, NULL),
    (1508, IdId('uuid','dbid777'),      TRUE,  TRUE,  1408, '2018-11-26T08:00:00+0000', NULL, 1103, (30, 60)::db.geopoint, NULL)
;

INSERT INTO state.check_rules
(session_id, duration_id, arrival_id, immobility_id, surge_arrival_id, checking,                   last_check)
VALUES
    (1501,       1301,        NULL,       NULL,          NULL,             '2018-11-26T11:59:59+0000', NULL),
    (1502,       1301,        1601,       1701,          NULL,             '2018-11-26T07:59:59+0000', NULL),
    (1503,       1301,        NULL,       NULL,          NULL,             NULL,                       NULL),
    (1504,       NULL,        NULL,       NULL,          NULL,             NULL,                       NULL),
    (1505,       NULL,        1601,       NULL,          NULL,             NULL,                       NULL),
    (1506,       NULL,        1601,       NULL,          NULL,             NULL,                       NULL),
    (1507,       NULL,        NULL,       NULL,          NULL,             NULL,                       '2018-11-26T08:59:59+0000'),
    (1508,       NULL,        NULL,       NULL,          1801,             NULL,                       NULL)
;
