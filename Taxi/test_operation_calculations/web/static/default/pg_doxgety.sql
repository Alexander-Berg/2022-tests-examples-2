INSERT INTO doxgety.params (id, tariff_zones, params, created_at, created_by)
VALUES ('a', '{omsk}', '{
    "end_date": "2022-03-30T14:46:23.727137",
    "start_date": "2022-03-23T14:46:23.727137",
    "cities_config": [
        {
            "proportion": 40,
            "tariff_zones": [
                "omsk"
            ]
        }
    ],
    "money_multiplier": 0.8,
    "targets_complexity": "0.98"
}', '2022-03-22 16:24:22.980052 +00:00', 'dpano'),
       ('b', '{omsk}', '{
           "end_date": "2022-03-30T14:46:23.727137",
           "start_date": "2022-03-23T14:46:23.727137",
           "cities_config": [
               {
                   "id": 1,
                   "proportion": 40,
                   "tariff_zones": [
                       "omsk"
                   ]
               }
           ],
           "money_multiplierf": 0.8,
           "targets_complexity": "0.98"
       }', '2022-03-22 16:24:22.980052 +00:00', 'robot'),
       ('c', '{sochi}', '{
           "end_date": "2022-03-30T14:46:23.727137",
           "start_date": "2022-03-23T14:46:23.727137",
           "cities_config": [
               {
                   "proportion": 40,
                   "tariff_zones": [
                       "sochi"
                   ]
               }
           ],
           "money_multiplier": 0.8,
           "targets_complexity": "0.98"
       }', '2022-03-22 16:24:22.980052 +00:00', 'robot');

INSERT INTO "doxgety"."status"(id,
                               status,
                               message,
                               updated_at,
                               updated_by)
VALUES ('a', 'CREATED', '', '2022-01-03T12:00:00+00:00', 'dpano'),
       ('b', 'SUCCESS', '', '2022-01-03T14:00:00+00:00', 'stq'),
       ('c', 'CREATED', '', '2022-01-03T10:00:00+00:00', 'robot');

INSERT INTO "doxgety"."result"(id, result, draft_id, is_multidraft, error)
VALUES ('b', '{
    "cities_result": [
        {
            "aa_difficulty": 0.98,
            "aa_difficulty_active": 0.98,
            "bonus": {
                "max": 6800.0,
                "mean": 4498,
                "min": 1900
            },
            "bonus_per_goal": {
                "max": 81.8,
                "mean": 46.6,
                "min": 28.9
            },
            "currency": "RUB",
            "goal": {
                "max": 180,
                "mean": 108,
                "min": 30
            },
            "whitelist": "//home/taxi_ml/add_whitelist",
            "budget": 100,
"ttest_pvalue":0
        }
    ],
    "whitelist": "//home/taxi_ml/add_whitelist_full"
}', Null, Null, Null);

