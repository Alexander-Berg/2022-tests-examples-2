insert into cashback_levels.missions_notifications
    (yandex_uid, task_description_id, stage_id, version, completions, event_id)
values
    ('123', 'task_id_1', 'stage1', 0, 0, ''),
    ('123', 'task_id_2', 'stage1', 0, 0, ''),
    ('123', 'task_id_3', 'stage1', 0, 0, '');

insert into cashback_levels.missions_completed
    (yandex_uid, task_description_id, stage_id, version, completions)
values
    ('123', 'task_id_1', 'stage1', 0, 1),
    ('123', 'task_id_2', 'stage1', 0, 2),
    ('123', 'task_id_3', 'stage1', 0, 3);
