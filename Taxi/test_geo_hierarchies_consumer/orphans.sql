INSERT INTO state.orphan_geo_hierarchies(
    driver_id,
    geo_hierarchy,
    updated_at,
	processed_at
) VALUES (
    ('dbid', 'uuid')::db.driver_id,
    '{br_moscow, br_russia, br_root}'::VARCHAR(128)[],
    '2021-05-01T00:00:00.000+00:00',
    '2021-05-01T00:00:00.000+00:00'
), (
    ('dbid', 'uuid1')::db.driver_id,
    '{br_spb, br_russia, br_root}'::VARCHAR(128)[],
    '2021-05-01T00:00:00.000+00:00',
    '2021-05-01T00:00:00.000+00:00'
), (
    ('dbid', 'uuid2')::db.driver_id,
    '{br_perm, br_russia, br_root}'::VARCHAR(128)[],
    '2021-05-01T00:00:00.000+00:00',
    '2021-05-01T00:00:00.000+00:00'
);
