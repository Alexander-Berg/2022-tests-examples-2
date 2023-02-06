INSERT INTO personal_goals.selections (
  selection_id,
  status
)
VALUES (
  'yandex_birthday',
  'active'
);


INSERT INTO personal_goals.goals (
  id,
  conditions,
  bonus,
  selection_id
)
VALUES (
  'goal_id_1',
  '{
      "type": "ride",

      "count": 2,
      "classes": ["econom"],

      "date_finish": "2019-08-30T12:00:00+0"
  }',
  '{
      "type": "cashback-fixed",
      "value": "100",
      "currency": "RUB"
  }',
  'yandex_birthday'
);

INSERT INTO personal_goals.user_goals (
  id,
  goal_id,
  yandex_uid,
  status,
  rewarded,
  selection_id,
  application
)
VALUES (
  '100_RUB_cashback',
  'goal_id_1',
  'yandex_uid_1',
  'done',
  False,
  'yandex_birthday',
  'yandex'
);
