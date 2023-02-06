INSERT INTO personal_goals.selections (
  selection_id,
  status
)
VALUES (
  'yandex_birthday',
  'active'
),
(
  'new_year',
  'rollback'
);

INSERT INTO personal_goals.goals (
  id,
  conditions,
  bonus,
  selection_id
)
VALUES
       ('goal_1','{}','{}','new_year'),
       ('goal_2','{}','{}','new_year'),
       ('goal_3','{}','{}','new_year'),
       ('goal_4','{}','{}','yandex_birthday')
;


INSERT INTO personal_goals.user_goals
(id,goal_id,yandex_uid,status,rewarded,application,selection_id)
VALUES
('user_goal_id_1','goal_1','yandex_uid_1','active',False,'yandex','yandex_birthday'),
('user_goal_id_2','goal_1','yandex_uid_2','done',False,'yandex','new_year'),
('user_goal_id_3','goal_1','yandex_uid_2','done',False,'yandex','new_year'),
('user_goal_id_4','goal_1','yandex_uid_2','done',True,'yandex','new_year'),
('user_goal_id_5','goal_1','yandex_uid_2','missed',True,'yandex','new_year');
