INSERT INTO fleet_drivers_scoring.yt_update_states
(id, operation_id, name, type, status, src_path, dst_path, src_cluster,
 dst_cluster, created_at, updated_at, parent_id, revision)
VALUES (5,
        'r31',
        'ratings',
        'convert',
        'done',
        '//home/opteum/fm/unittests/features/scoring/2020-05-08_02-00',
        '//home/opteum/fm/unittests/features/scoring/2020-05-08_02-00',
        'hahn',
        'seneca-man',
        '2020-05-08 02:20:00',
        '2020-05-08 02:30:00',
        1,
        '2020-05-08 02:00:00'),
       (6,
        'r32',
        'ratings',
        'convert',
        'done',
        '//home/opteum/fm/unittests/features/scoring/2020-05-08_02-00',
        '//home/opteum/fm/unittests/features/scoring/2020-05-08_02-00',
        'hahn',
        'seneca-vla',
        '2020-05-08 02:20:00',
        '2020-05-08 02:30:00',
        1,
        '2020-05-08 02:00:00')
;

INSERT INTO fleet_drivers_scoring.yt_updates
(
    name,
    path,
    revision,
    created_at
)
VALUES
(
    'high_speed_driving',
    '//home/opteum/fm/testing/features/scoring/high_speed_driving/2020-05-04',
    '2020-05-08 02:00:00',
    CURRENT_TIMESTAMP
)
