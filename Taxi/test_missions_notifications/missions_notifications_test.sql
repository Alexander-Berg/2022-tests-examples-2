INSERT INTO cashback_levels.missions_notifications (yandex_uid, task_description_id, stage_id, type,
                                                    event_id, client_status, details)
VALUES ('123', 'task_id_1', 'stage1', 'assigned', 'event_id_1', 'new', '{"target": 1}'::jsonb),
       ('123', 'task_id_2', 'stage1', 'completed', 'event_id_2', 'new', '{"target": 1}'::jsonb),
       ('123', 'task_id_3', 'stage1', 'assigned',
        'event_id_3', 'new', '{"target": 1, "stop_time": "2021-09-26T13:00:00+0000"}'::jsonb),
       ('123', 'task_id_4', 'stage1', 'completed', 'event_id_4', 'seen', '{"target": 1}'::jsonb)
