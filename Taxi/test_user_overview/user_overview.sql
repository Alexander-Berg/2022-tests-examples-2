insert into cashback_levels.users
(yandex_uid, stage_id, current_used_level, current_earned_level, progress)
values
('123', 'stage_1', 1, 2, 50),
('123', 'stage_only_level', 1, 2, 50);

insert into cashback_levels.users_segments
(yandex_uid, stage_id, segment)
values
('123', 'stage_1', 'segment_1'),
('123', 'stage_1', 'segment_2'),
('123', 'stage_only_segment', 'segment_3');

INSERT INTO cashback_levels.missions_completed
(id, yandex_uid, task_description_id, stage_id, version, completions)
VALUES
('1aa98544-eca2-4d8a-9866-909fc3a47836', '123', 'task_id_1', 'stage_1', 1, 10),
('1aa98544-eca2-4d8a-9866-909fc3a47837', '123', 'task_id_only_in_completed', 'stage_only_competed', 1, 10);

INSERT INTO cashback_levels.missions_notifications
    (id, yandex_uid, task_description_id, stage_id, version, event_id, completions, created, updated, client_status)
VALUES
('cd0b3384-fcf1-466e-9d33-9b1866bd0a51', '123', 'task_id_1', 'stage_1', 1, 'event_id_1', 20, '2021-12-05T20:15:50.000000+0000', '2021-12-05T20:15:40.000000+0000', 'new'),
('cd0b3384-fcf1-466e-9d33-9b1866bd0a52', '123', 'task_id_1', 'stage_1', 2, 'event_id_2', 30, '2021-12-05T20:15:50.000000+0000', '2021-12-05T20:15:40.000000+0000', 'new'),
('cd0b3384-fcf2-466e-9d33-9b1866bd0a53', '123', 'task_id_only_in_notification', 'stage_only_notification', 30, 'event_id_0', 40, '2021-12-05T20:15:51.000000+0000', '2021-12-05T20:15:41.000000+0000', 'seen');
