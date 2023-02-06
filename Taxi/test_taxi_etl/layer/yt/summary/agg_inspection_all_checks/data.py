CASES = [
    {
        "id": "test_empty_source",
        "given": {
            "forms": [],
            "toloka": [],
            "orders": []
        },
        "expected": []
    },
    {
        "id": "test_toloka_filter",
        "given": {
            "forms": [
                {
                    "inspection_id": "f_i1",
                    "question_id": 1,
                    "question_tag": "dresscode",
                    "question_answer": "Да",
                    "questionary_id": 10015306,
                    "utc_created_dttm": "2020-06-01 15:30:00"
                },
                {
                    "inspection_id": "f_i1",
                    "question_id": 10,
                    "question_tag": "order",
                    "question_answer": "o4",
                    "questionary_id": 10015306,
                    "utc_created_dttm": "2020-06-01 15:30:00"
                },
                {
                    "inspection_id": "f_i2",
                    "question_id": 2,
                    "question_tag": "dresscode",
                    "question_answer": "Да",
                    "questionary_id": 10015306,
                    "utc_created_dttm": "2020-06-01 16:30:00"
                },
                {
                    "inspection_id": "f_i2",
                    "question_id": 20,
                    "question_tag": "order",
                    "question_answer": "o5",
                    "questionary_id": 10015306,
                    "utc_created_dttm": "2020-06-01 18:30:00"
                },
            ],
            "toloka": [
                {
                    "order_id": "o4",
                    "question_code": "dresscode",
                    "resolution": "Принята",
                    "answer": "Да (проверено)",
                    "utc_assigned_dttm": "2020-06-01 17:00:00",
                }
            ],
            "orders": [
                {
                    "order_id": "o4",
                    "car_number_normalized": "O666OO99",
                    "driver_license": "7777777777",
                    "driver_tariff_class": "vip",
                    "success_order_flg": True,
                    "user_phone_id": "up2",
                    "user_phone_pd_id": "up2_pd_id",
                    "utc_order_created_dttm": "2020-06-01 15:00:00",
                    "utc_start_waiting_dttm": "2020-06-01 15:10:00"
                },
                {
                    "order_id": "o5",
                    "car_number_normalized": "H999HH88",
                    "driver_license": "1111111111",
                    "driver_tariff_class": "comfortplus",
                    "success_order_flg": True,
                    "user_phone_id": "up2",
                    "user_phone_pd_id": "up2_pd_id",
                    "utc_order_created_dttm": "2020-06-01 16:00:00",
                    "utc_start_waiting_dttm": "2020-06-01 16:10:00"
                }
            ]
        },
        "expected": [
            {
                "inspection_id": "test_toloka_filter#f_i1",
                "question_id": 1,
                "question_answer": "Да (проверено)",
                "order_tariff": "vip",
                "car_number_normalized": "O666OO99",
                "user_phone_pd_id": "up2_pd_id",
                "utc_controller_complete_dttm": "2020-06-01 15:30:00",
                "order_id": "o4",
                "utc_order_dttm": "2020-06-01 15:00:00",
                "utc_toloka_assigned_dttm": "2020-06-01 17:00:00",
            },
            {
                "inspection_id": "test_toloka_filter#f_i2",
                "question_id": 2,
                "question_answer": "Да",
                "order_tariff": "comfortplus",
                "car_number_normalized": "H999HH88",
                "user_phone_pd_id": "up2_pd_id",
                "utc_controller_complete_dttm": "2020-06-01 16:30:00",
                "order_id": "o5",
                "utc_order_dttm": "2020-06-01 16:00:00",
                "utc_toloka_assigned_dttm": None,
            }
        ]
    },
]

INSPECTION_ANSWERS = [
    {
        "question_code": "q1",
        "tariff": "vip",
        "answer": "a1",
        "update_dttm": "2019-01-01",
        "value": 1,
        "weight": 0
    },
    {
        "question_code": "q2",
        "tariff": "vip;comfortplus",
        "answer": "a2",
        "update_dttm": "2019-01-01",
        "value": 1,
        "weight": 0
    },
    {
        "question_code": "q2",
        "tariff": "vip;comfortplus",
        "answer": "a2",
        "update_dttm": "2020-06-05",
        "value": -1,
        "weight": 1
    }
]

INSPECTION_TARIFF_CODES = [
    {
        "code": "comfortplus",
        "description": "Комфорт+",
        "toloka_to_check": 0
    },
    {
        "code": "vip",
        "description": "Бизнес",
        "toloka_to_check": 1
    }
]
