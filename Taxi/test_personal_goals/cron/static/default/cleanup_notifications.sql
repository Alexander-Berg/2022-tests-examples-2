INSERT INTO personal_goals.goals
(id,conditions,bonus)
VALUES
('g_id_1', '{}', '{}');

INSERT INTO personal_goals.user_goals
(id,goal_id,yandex_uid,status,rewarded,application)
VALUES
('ug_id_1','g_id_1','uid_1','active',False,'yandex');

INSERT INTO personal_goals.user_notifications
(id,event,user_goal,status, updated)
VALUES
('n_id_1', 'goal_finish', 'ug_id_1', 'new', '2019-08-15T12:00:00+0'),
('n_id_2', 'goal_finish', 'ug_id_1', 'new', '2019-08-15T11:00:00+0'),
('n_id_3', 'goal_finish', 'ug_id_1', 'new', '2019-08-15T10:00:00+0'),
('n_id_4', 'goal_finish', 'ug_id_1', 'seen', '2019-08-15T11:50:00+0'),
('n_id_5', 'goal_finish', 'ug_id_1', 'seen', '2019-08-15T11:00:00+0'),
('n_id_6', 'goal_finish', 'ug_id_1', 'seen', '2019-08-15T10:00:00+0'),
('n_id_7', 'goal_finish', 'ug_id_1', 'seen', '2019-08-15T09:00:00+0'),
('n_id_8', 'goal_finish', 'ug_id_1', 'seen', '2019-08-15T08:00:00+0');
