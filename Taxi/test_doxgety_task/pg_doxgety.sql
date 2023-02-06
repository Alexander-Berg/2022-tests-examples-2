INSERT INTO "doxgety"."status"(id,
                                                     status,
                                                     message,
                                                     updated_at,
                                                     updated_by)
VALUES ('1','CREATED','','2022-01-03T12:00:00+00:00', 'dpano');

INSERT INTO doxgety.params (id, tariff_zones, params, created_at, created_by)
VALUES ('1', '{omsk}', '{
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
}', '2022-03-22 16:24:22.980052 +00:00', 'dpano');
