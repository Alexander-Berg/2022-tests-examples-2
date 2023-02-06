insert into cashback_levels.missions_notifications
    (yandex_uid, task_description_id, stage_id, version, completions, event_id)
values
    ('123', 'task1_level1', 'stage1', 0, 0, ''),
    ('123', 'task1_level1', 'stage2', 0, 0, ''),
    ('123', 'task2_level1', 'stage1', 0, 0, ''),
    ('789', 'task1_level1', 'stage1', 0, 0, '');

insert into cashback_levels.missions_completed
    (yandex_uid, task_description_id, stage_id, version, completions)
values
    ('123', 'task1_level1', 'stage1', 0, 1),
    ('123', 'task1_level1', 'stage2', 0, 2),
    ('123', 'task2_level1', 'stage1', 0, 3),
    ('789', 'task1_level1', 'stage1', 0, 4);
