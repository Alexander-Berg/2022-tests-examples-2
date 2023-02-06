INSERT INTO personal_goals.selections (
  selection_id,
  status
)
VALUES (
  'yandex_birthday',
  'active'
);

INSERT INTO personal_goals.goals
(id,conditions,bonus)
VALUES (
  'goal_id_1',
  '{
      "type": "ride",

      "count": 5,
      "classes": ["econom", "comfort"],

      "date_finish": "2019-08-30T12:00:00+0"
  }',
  '{
      "type": "promocode",
      "series": "bonus",

      "value": "400",
      "currency": "RUB",
      "percent": "10",
      "classes": ["econom"],
      "ride_count": 1
  }'
),
(
  'goal_id_2',
  '{
      "type": "ride",

      "count": 5,
      "classes": ["econom", "comfort"],

      "date_finish": "2019-01-01T12:00:00+0"
  }',
  '{
      "type": "promocode",
      "series": "bonus",

      "value": "400",
      "currency": "RUB",
      "percent": "10",
      "classes": ["econom"],
      "ride_count": 1
  }'
),
(
  'goal_id_3',
  '{
      "type": "ride",

      "count": 2,
      "classes": ["econom", "comfort"],

      "date_finish": "2021-01-01T12:00:00+0"
  }',
  '{
      "type": "cashback-boost",
      "days": 15,
      "percent": 4,
      "classes": ["comfort"]
  }'
),
(
  'goal_id_4',
  '{
      "type": "ride",

      "count": 2,
      "classes": ["econom", "comfort"],

      "date_finish": "2021-01-01T12:00:00+0"
  }',
  '{
      "type": "cashback-fixed",
      "value": "100",
      "currency": "RUB"
  }'
);

INSERT INTO personal_goals.user_goals
(id,goal_id,yandex_uid,status,rewarded,application,selection_id)
VALUES
('user_goal_id_1','goal_id_1','yandex_uid_1','active',False,'yandex','yandex_birthday'),
('user_goal_id_2','goal_id_1','yandex_uid_2','done',False,'yandex','yandex_birthday'),
('user_goal_id_3','goal_id_1','yandex_uid_2','done',False,'yandex','yandex_birthday'),
('user_goal_id_4','goal_id_1','yandex_uid_2','done',False,'yandex','yandex_birthday'),
('user_goal_id_5','goal_id_2','yandex_uid_2','active',False,'yandex','yandex_birthday'),
('user_goal_id_6','goal_id_3','yandex_uid_2','active',False,'yandex','yandex_birthday'),
('user_goal_id_7','goal_id_4','yandex_uid_2','active',False,'yandex','yandex_birthday');

INSERT INTO personal_goals.user_goal_events
(id,event_id,event_type,user_goal,suitable,reason)
VALUES
('hash_id_1','order-id-1','taxi_order','user_goal_id_1', True, NULL),
('hash_id_4','order-id-4','taxi_order','user_goal_id_1', False, 'err1'),
('hash_id_5','order-id-5','taxi_order','user_goal_id_1', False, 'err2');


INSERT INTO personal_goals.user_notifications
(id, event, user_goal, status)
VALUES
('new_notification_1', 'goal_start', 'user_goal_id_2', 'new'),
('new_notification_2', 'goal_start', 'user_goal_id_3', 'new'),
('new_notification_3', 'goal_start', 'user_goal_id_6', 'new'),
('goal_progress_1', 'goal_progress', 'user_goal_id_2', 'new'),
('goal_progress_2', 'goal_progress', 'user_goal_id_4', 'new'),
('finish_notification_1', 'goal_finish', 'user_goal_id_2', 'new'),
('finish_notification_2', 'goal_finish', 'user_goal_id_5', 'new');
