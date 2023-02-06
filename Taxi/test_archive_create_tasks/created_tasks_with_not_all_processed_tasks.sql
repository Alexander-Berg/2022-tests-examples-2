INSERT INTO driver_trackstory.archive_process_tasks (partition_num, time_created)
VALUES (1, '2020-01-01 00:00:00'),
       (2, '2020-01-01 00:00:00'),
       (3, '2020-01-01 00:00:00'),
       (4, '2020-01-01 00:00:00'),
       (5, '2020-01-01 00:00:00'),
       (6, '2020-01-01 00:00:00'),
       (7, '2020-01-01 00:00:00');

INSERT INTO driver_trackstory.current_archive_process_hour (id, hour)
    VALUES (1, 444);

INSERT INTO driver_trackstory.archive_process_info (partition_num, hour, logbroker_offsets, work_duration)
VALUES (1, 444, '[]', INTERVAL '2 seconds'),
       (2, 444, '[]', INTERVAL '2 seconds'),
       (3, 444, '[]', INTERVAL '2 seconds'),
       (4, 444, '[]', INTERVAL '2 seconds'),
       (5, 444, '[]', INTERVAL '2 seconds'),
       (6, 444, '[]', INTERVAL '2 seconds');
