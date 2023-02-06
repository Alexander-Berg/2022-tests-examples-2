INSERT INTO personal_goals.goals
(id,conditions,bonus)
VALUES (
  'goal_id_1',
  '{
      "type": "ride",
      "count": 2,
      "date_finish": "2019-08-30T12:00:00+0",
      "payment_types": ["card"]
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
);

INSERT INTO personal_goals.goals
(id,conditions,bonus)
VALUES (
  'goal_id_2',
  '{
      "type": "ride",

      "count": 3,
      "classes": ["vip"],

      "date_finish": "2019-08-30T12:00:00+0"
  }',
  '{
      "type": "promocode",
      "series": "bonus",

      "value": "400",
      "currency": "RUB",
      "ride_count": 1
  }'
);

INSERT INTO personal_goals.goals
(id,conditions,bonus)
VALUES (
  'goal_id_3',
  '{
      "type": "ride",

      "count": 4,
      "classes": ["econom", "comfort"],

      "date_finish": "2019-08-30T12:00:00+0"
  }',
  '{
      "type": "promocode",
      "series": "bonus",

      "value": "400",
      "currency": "RUB",
      "classes": ["econom"],
      "ride_count": 1
  }'
);

INSERT INTO personal_goals.goals
(id,conditions,bonus)
VALUES (
  'goal_id_4',
  '{
      "type": "ride",

      "count": 4,
      "classes": ["econom", "comfort"],
      "payment_types": ["card"],

      "date_finish": "2019-08-30T12:00:00+0"
  }',
  '{
      "type": "promocode",
      "series": "bonus",

      "value": "400",
      "currency": "RUB",
      "classes": ["vip"],
      "ride_count": 1
  }'
);

INSERT INTO personal_goals.goals
(id,conditions,bonus)
VALUES (
  'goal_id_5',
  '{
      "type": "ride",
      "count": 2,
      "date_finish": "2019-08-30T12:00:00+0",
      "payment_types": ["card"]
  }',
  '{
      "type": "cashback-fixed",
      "value": "100",
      "currency": "RUB"
  }'
);
