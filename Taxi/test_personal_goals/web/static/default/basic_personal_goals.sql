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
VALUES (
  '9bf5f1476c1344f2b8abbc4012a9cbc1',
  '{
      "type": "ride",

      "count": 3,
      "classes": ["econom"],

      "date_finish": "2019-08-30T12:00:00+0"
  }',
  '{
      "type": "promocode",
      "series": "bonus",

      "value": "400",
      "currency": "RUB",
      "percent": "10"
  }',
  'yandex_birthday'
),
(
  '2905eec9efcb428f8c0b1e429abde3b0',
  '{
      "type": "ride",

      "count": 5,
      "classes": ["comfortplus"],
      "payment_types": ["card"],
      "source": {
        "zones": ["moscow"]
      },
      "date_finish": "2019-07-30T12:00:00+0"
  }',
  '{
      "type": "promocode",
      "value": "150",
      "currency": "RUB",
      "series": "cool"
  }',
  'yandex_birthday'
),
(
  'b3c486935a0b4a0393538a18d89afb31',
  '{
      "type": "ride",

      "count": 5,
      "classes": ["comfortplus"],
      "payment_types": ["card"],
      "source": {
        "zones": ["moscow"]
      },
      "date_finish": "2019-07-30T12:00:00+0"
  }',
  '{
      "type": "promocode",
      "value": "150",
      "currency": "RUB",
      "series": "cool"
  }',
  'new_year'),
(
  'c25de08247ed4d32aefae91197a84345',
  '{
      "type": "ride",

      "count": 2,
      "classes": ["comfortplus"],
      "payment_types": ["card"],
      "source": {
        "zones": ["moscow"]
      },
      "date_finish": "2021-07-30T12:00:00+0"
  }',
  '{
      "type": "cashback-boost",
      "days": 15,
      "percent": 4,
      "classes": ["comfort"]
  }',
  'new_year'),
(
  'goal_id_3',
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
  '9921d89db101479ab1e476d8910d72fb',
  '9bf5f1476c1344f2b8abbc4012a9cbc1',
  '999999',
  'active',
  False,
  'yandex_birthday',
  'yandex'
),
(
  'user_goal_id_1',
  '9bf5f1476c1344f2b8abbc4012a9cbc1',
  'yandex_uid_1',
  'active',
  False,
  'yandex_birthday',
  'yandex'
),
(
  'c69e65c601c04ffdaa6277c80cafe7f8',
  '9bf5f1476c1344f2b8abbc4012a9cbc1',
  '666666',
  'done',
  False,
  'yandex_birthday',
  'yandex'
),
(
  'user_goal_id_2',
  '9bf5f1476c1344f2b8abbc4012a9cbc1',
  '647834',
  'done',
  False,
  'yandex_birthday',
  'yandex'
),
(
  'bcf19460bdc34c439842a63fadb20fa8',
  '2905eec9efcb428f8c0b1e429abde3b0',
  '666666',
  'done',
  True,
  'yandex_birthday',
  'yandex'
),
(
  '7b82121e78a84dea95f69382a1ef0817',
  'b3c486935a0b4a0393538a18d89afb31',
  'hidden_uid',
  'done',
  True,
  'new_year',
  'yandex'
),
(
  'user_goal_id_4',
  '9bf5f1476c1344f2b8abbc4012a9cbc1',
  '999999',
  'active',
  False,
  'yandex_birthday',
  'yandex'
),
(
  'user_goal_id_3',
  'goal_id_3',
  'yandex_uid_3',
  'done',
  False,
  'yandex_birthday',
  'yandex'
);

INSERT INTO personal_goals.user_goal_events
(id,event_id,event_type,user_goal,suitable,reason)
VALUES
('hash_id_1','order-id-1','taxi_order','9921d89db101479ab1e476d8910d72fb', True, NULL),
('hash_id_2','order-id-2','taxi_order','9921d89db101479ab1e476d8910d72fb', True, NULL),
('hash_id_3','order-id-3','taxi_order','9921d89db101479ab1e476d8910d72fb', True, NULL),
('hash_id_4','order-id-4','taxi_order','9921d89db101479ab1e476d8910d72fb', False, 'err1'),
('hash_id_5','order-id-5','taxi_order','9921d89db101479ab1e476d8910d72fb', False, 'err2'),
('hash_id_6','order-id-6','taxi_order','9921d89db101479ab1e476d8910d72fb', False, 'err3'),
('hash_id_7','order-id-7','taxi_order','user_goal_id_3', True, NULL),
('hash_id_8','order-id-8','taxi_order','user_goal_id_3', True, NULL),
('hash_id_9','order-id-9','taxi_order','user_goal_id_3', False, 'err4');

INSERT INTO personal_goals.user_notifications (
  id,
  event,
  user_goal,
  status
)
VALUES (
  'b7fc20328ae043fb830d4c3453331906',
  'goal_finish',
  'c69e65c601c04ffdaa6277c80cafe7f8',
  'new'
),
(
  'notification_id_2',
  'goal_finish',
  'bcf19460bdc34c439842a63fadb20fa8',
  'new'
),
(
  '8072aa213e914b00b066b5f9f83f663d',
  'goal_start',
  'c69e65c601c04ffdaa6277c80cafe7f8',
  'new'
),
(
  'c1a973eff0cf46c5b85c8535e71ff404',
  'goal_finish',
  '7b82121e78a84dea95f69382a1ef0817',
  'new'
);
