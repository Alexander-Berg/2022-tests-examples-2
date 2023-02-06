INSERT INTO "operation_calculations"."operations" (
    "id",
    "params_type",
    "status",
    "params",
    "meta",
    "draft_id",
    "updated_at",
    "updated_by",
    "created_at",
    "created_by"
) VALUES
(
    'be109b72119e37321188f84717646b96',
    'nmfg-subventions',
    'FINISHED',
    '{
        "type": "brand-nmfg-subventions",
        "commission": 10,
        "end_date": "01.01.2021",
        "maxtrips": 1,
        "price_increase": 1.5,
        "start_date": "01.01.2020",
        "tariff_zone": "moscow",
        "tariffs": [
            "econom"
        ],
        "sub_brand": 170317,
        "a1": 5,
        "a2": 0,
        "m": 20,
        "hours": [1,2,3,5,7,10,11,12],
        "week_days": ["mon"],
        "subvenion_start_date": "2020-01-01",
        "subvenion_end_date": "2021-01-01"
    }',
    '{
    "brand": {
        "charts": [],
        "guarantees": [
            {
                "count_trips": 1,
                "guarantee": 0.0
            },
            {
                "count_trips": 2,
                "guarantee": 20.0
            }
        ],
        "result": {
            "do_x_get_y_subs_fact": 0.0,
            "fact_nmfg_subs": 0.856,
            "fact_subs": 0.856,
            "geo_subs_fact": 34223.0,
            "gmv": 1635.0,
            "plan_nmfg_subs": 32423.0,
            "plan_subs": 23134.0
        }
    }
}',
    NULL,
    '2020-01-01T12:00:00+03:00',
    'robot',
    '2020-01-01T12:00:00+03:00',
    'robot'
)
