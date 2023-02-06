INSERT INTO fleet_drivers_scoring.yt_update_states
(id, operation_id, name, type, status, src_path, dst_path, src_cluster,
 dst_cluster, created_at, updated_at, parent_id, revision)
VALUES (1,
        'r11',
        'ratings',
        'calc',
        'done',
        null,
        '//home/opteum/fm/unittests/features/scoring/2020-05-08_02-00',
        null,
        'hahn',
        '2020-05-08 02:00:00',
        '2020-05-08 02:10:00',
        null,
        '2020-05-08 02:00:00'),
       (2,
        'r12',
        'ratings',
        'copy',
        'done',
        '//home/opteum/fm/unittests/features/scoring/2020-05-08_02-00',
        '//home/opteum/fm/unittests/features/scoring/2020-05-08_02-00',
        'hahn',
        'seneca-man',
        '2020-05-08 02:10:00',
        '2020-05-08 02:20:00',
        1,
        '2020-05-08 02:00:00'),
       (3,
        'r13',
        'ratings',
        'convert',
        'done',
        '//home/opteum/fm/unittests/features/scoring/2020-05-08_02-00',
        '//home/opteum/fm/unittests/features/scoring/2020-05-08_02-00',
        'seneca-man',
        'seneca-man',
        '2020-05-08 02:20:00',
        '2020-05-08 02:30:00',
        1,
        '2020-05-08 02:00:00'),
       (4,
        'r21',
        'ratings',
        'calc',
        'pending',
        null,
        '//home/opteum/fm/unittests/features/scoring/2020-05-08_17-00',
        null,
        'hahn',
        '2020-05-08 17:00:00',
        '2020-05-08 17:00:00',
        null,
        '2020-05-08 17:00:00')
;
ALTER SEQUENCE fleet_drivers_scoring.yt_update_states_id_seq RESTART WITH 4;