INSERT INTO settings.driver_ids (driver_id) VALUES
(('dbid777','888')),
(('1488','driverSS')),
(('1488','driverSS2')),
(('pg_park','pg_driver')),
(('dbid','uuid')),
(('dbid','uuid1')),
(('dbid','uuid2')),
(('dbid777','uuid')),
(('dbid777','uuid1')),
(('dbid777','uuid2')),
(('dbid777','uuid3')),
(('dbidparis','uuid2')) ON CONFLICT DO NOTHING;

CREATE OR REPLACE FUNCTION IdId(uuid TEXT, dbid TEXT)
RETURNS integer AS $$
  SELECT driver_id_id FROM settings.driver_ids WHERE (driver_id).uuid = uuid AND (driver_id).dbid = dbid $$ LANGUAGE SQL;

INSERT INTO
    state.geo_hierarchies(
        driver_id_id,
        geo_hierarchy,
        updated_at,
        fetched_at
    )
VALUES
    (
        IdId('888', 'dbid777'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    ),
    (
        IdId('driverSS', '1488'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    ),
    (
        IdId('driverSS2', '1488'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    ),
    (
        IdId('pg_driver', 'pg_park'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    ),
    (
        IdId('uuid', 'dbid'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    ),
    (
        IdId('uuid1', 'dbid'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    ),
    (
        IdId('uuid2', 'dbid'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    ),
    (
        IdId('uuid', 'dbid777'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    ),
    (
        IdId('uuid1', 'dbid777'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    ),
    (
        IdId('uuid2', 'dbid777'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    ),
    (
        IdId('uuid3', 'dbid777'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    ),
    (
        IdId('uuid2', 'dbidparis'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        '01-01-2021T00:00:00+00:00',
        '01-01-2021T00:00:00+00:00'
    )
ON CONFLICT(driver_id_id) DO NOTHING;
