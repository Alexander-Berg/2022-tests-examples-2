UPDATE
    config.modes
SET
    geo_nodes_permitted = ARRAY['br_moscow']
WHERE
    mode_name = 'home';

UPDATE
    config.modes
SET
    geo_nodes_prohibited = ARRAY['br_perm']
WHERE
    mode_name = 'poi';

UPDATE
    config.modes
SET
    geo_nodes_permitted = ARRAY['br_russia']
WHERE
    mode_name = 'my_district';

INSERT INTO
    state.geo_hierarchies(
        driver_id_id,
        geo_hierarchy,
        updated_at,
        fetched_at
    )
VALUES
    (
        IdId('uuid', 'dbid777'),
        '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
        now(),
        now()
    ),
    (
        IdId('uuid1', 'dbid777'),
        '{br_spb, br_russia, br_root}'::VARCHAR(128)[],
        now(),
        now()
    ),
    (
        IdId('driverSS','1488'),
        '{br_perm, br_russia, br_root}'::VARCHAR(128)[],
        now(),
        now()
    )
    ON CONFLICT(driver_id_id)
    DO UPDATE SET
        geo_hierarchy = EXCLUDED.geo_hierarchy,
        updated_at = EXCLUDED.updated_at,
        fetched_at = EXCLUDED.fetched_at;
