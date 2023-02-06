from operator import itemgetter


INSPECTION_ACTIONS = [
    {
        "question_code": "car_exterior",
        "tariff": "comfortplus",
        "region": "Москва",
        "update_dttm": "2020-02-26 00:00:00",
        "low_tariff": 2,
        "penalty": 9999,
        "sum_penalty": 0,
        "warning": 1,
    },
    {
        "question_code": "car_exterior",
        "tariff": "vip;ultimate;maybach;premium_van",
        "region": "Москва;Санкт-Петербург",
        "update_dttm": "2020-03-17 00:00:00",
        "low_tariff": 2,
        "penalty": 1,
        "sum_penalty": 1000,
        "warning": 9999,
    },
    {
        "question_code": "car_interior",
        "tariff": "comfortplus",
        "region": "Москва",
        "update_dttm": "2020-02-26 00:00:00",
        "low_tariff": 1,
        "penalty": 9999,
        "sum_penalty": 0,
        "warning": 9999,
    },
    {
        "question_code": "car_interior",
        "tariff": "vip;ultimate;maybach;premium_van",
        "region": "Москва;Санкт-Петербург",
        "update_dttm": "2020-03-17 00:00:00",
        "low_tariff": 2,
        "penalty": 1,
        "sum_penalty": 1000,
        "warning": 9999,
    },
    {
        "question_code": "distracted_by_the_phone",
        "tariff": "vip;ultimate;maybach;premium_van",
        "region": "Москва;Санкт-Петербург",
        "update_dttm": "2020-03-17 00:00:00",
        "low_tariff": 2,
        "penalty": 9999,
        "sum_penalty": 0,
        "warning": 1,
    },
    {
        "question_code": "dresscode",
        "tariff": "comfortplus;vip",
        "region": "Москва",
        "update_dttm": "2020-03-17 00:00:00",
        "low_tariff": 2,
        "penalty": 9999,
        "sum_penalty": 0,
        "warning": 1,
    },
    {
        "question_code": "driving_style",
        "tariff": "comfortplus",
        "region": "Москва",
        "update_dttm": "2020-03-17 00:00:00",
        "low_tariff": 2,
        "penalty": 9999,
        "sum_penalty": 0,
        "warning": 1,
    },
]
INSPECTION_TARIFF_SETTINGS = [
    {
        "tariff": "comfortplus",
        "exams": 2,
        "history_in_days": 180,
        "last_orders": 2,
        "errors_to_low_tariff": 3,
    },
    {
        "tariff": "vip",
        "exams": 2,
        "history_in_days": 180,
        "last_orders": 2,
        "errors_to_low_tariff": 2,
    },
]


def _agg_inspection_impacts_rows(case):
    for old_impact in case["given"]["old_impacts"]:
        yield {
            "driver_license": case["id"],
            "utc_created_dttm": old_impact["utc_created_dttm"],
            "utc_controller_complete_dttm": old_impact["utc_controller_complete_dttm"],
            "utc_toloka_assigned_dttm": old_impact["utc_toloka_assigned_dttm"],
            "impact_id": case["id"] + old_impact["order_id"],
            "inspection_id": case["id"] + old_impact["inspection_id"],
            "order_id": case["id"] + old_impact["order_id"],
            "order_tariff": old_impact["order_tariff"],
            "action_code": old_impact["action_code"],
            "exam_cnt": old_impact["exam_cnt"],
            "penalty_sum": old_impact["penalty_sum"],
            "problem_list": old_impact["problem_list"],
        }


def get_given_agg_inspection_impacts_rows(cases):
    return sorted(
        (row for case in cases for row in _agg_inspection_impacts_rows(case)),
        key=itemgetter("impact_id"),
    )


_question_id = 0


def _dm_inspection_rows(case):
    global _question_id
    for new_inspection in case["given"]["new_inspections"]:
        for question in new_inspection["questions"]:
            yield {
                "driver_license": case["id"],
                "question_id": _question_id,
                "utc_controller_complete_dttm": new_inspection["utc_controller_complete_dttm"],
                "utc_toloka_assigned_dttm": new_inspection["utc_toloka_assigned_dttm"],
                "inspection_id": case["id"] + new_inspection["inspection_id"],
                "order_id": case["id"] + new_inspection["order_id"],
                "order_tariff": new_inspection["order_tariff"],
                "city": new_inspection["city"],
                "utc_order_dt": new_inspection["utc_order_dt"],
                "question_code": question["question_code"],
                "value": question["value"],
            }
            _question_id += 1
    for old_impact in case["given"]["old_impacts"]:
        for question in old_impact["problem_list"]:
            yield {
                "driver_license": case["id"],
                "question_id": _question_id,
                "utc_controller_complete_dttm": old_impact["utc_controller_complete_dttm"],
                "utc_toloka_assigned_dttm": old_impact["utc_toloka_assigned_dttm"],
                "inspection_id": case["id"] + old_impact["inspection_id"],
                "order_id": case["id"] + old_impact["order_id"],
                "order_tariff": case["id"] + old_impact["order_tariff"],
                "city": "Москва",
                "utc_order_dt": old_impact["utc_controller_complete_dttm"][:10],
                "question_code": question,
                "value": -1,
            }
            _question_id += 1


def get_given_dm_inspection_rows(cases):
    return sorted(
        (row for case in cases for row in _dm_inspection_rows(case)),
        key=itemgetter("inspection_id", "question_id"),
    )


def get_actual_impacts(case, actual_impacts_all_cases):
    driver_license = case["id"]
    return [
        impact
        for impact in actual_impacts_all_cases
        if impact["driver_license"] == driver_license
    ]


def get_expected_new_impact(case):
    impact = case["expected_new_impact"]
    return {
        "utc_controller_complete_dttm": impact["utc_controller_complete_dttm"],
        "utc_toloka_assigned_dttm": impact["utc_toloka_assigned_dttm"],
        "inspection_id": case["id"] + impact["inspection_id"],
        "order_id": case["id"] + impact["order_id"],
        "order_tariff": impact["order_tariff"],
        "action_code": impact["action_code"],
        "exam_cnt": impact["exam_cnt"],
        "penalty_sum": impact["penalty_sum"],
        "problem_list": impact["problem_list"],
    }
