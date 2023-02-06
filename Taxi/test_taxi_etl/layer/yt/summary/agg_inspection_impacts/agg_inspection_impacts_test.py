# pylint: disable=redefined-outer-name
import pytest
from init_py_env import settings

from connection.yt import Pool, get_pool_value
from dmp_suite.file_utils import from_same_directory
from dmp_suite.yql import add_backquote
from dmp_suite.yt import YTMeta, etl, operation as op
from dmp_suite.yt.loaders import YqlEtlQuery, RotationInsertLoader

from taxi_etl.layer.yt.summary import SummaryDMInspection, SummaryAggInspectionImpacts, agg_inspection_impacts
from taxi_etl.layer.yt.raw.googledocs import InspectionActions, InspectionTariffSettings

from .impl import (
    INSPECTION_ACTIONS,
    INSPECTION_TARIFF_SETTINGS,
    get_given_agg_inspection_impacts_rows,
    get_given_dm_inspection_rows,
    get_actual_impacts,
    get_expected_new_impact,
)


CASES = [
    {
        "id": "low_tariff_due_to_last_inspection",
        "given": {
            "old_impacts": [],
            "new_inspections": [
                {
                    "utc_controller_complete_dttm": "2020-03-01 13:00:00",
                    "utc_toloka_assigned_dttm": "2020-03-01 17:00:00",
                    "inspection_id": "i1",
                    "order_id": "o1",
                    "order_tariff": "comfortplus",
                    "city": "Москва",
                    "utc_order_dt": "2020-03-01",
                    "questions": [
                        {"question_code": "dresscode", "value": -1},
                        {"question_code": "car_exterior", "value": -1},
                        {"question_code": "driving_style", "value": -1},
                    ],
                }
            ]
        },
        "expected_new_impact": {
            "utc_controller_complete_dttm": "2020-03-01 13:00:00",
            "utc_toloka_assigned_dttm": "2020-03-01 17:00:00",
            "inspection_id": "i1",
            "order_id": "o1",
            "order_tariff": "comfortplus",
            "action_code": 1,
            "exam_cnt": 2,
            "penalty_sum": 0,
            "problem_list": ["car_exterior", "dresscode", "driving_style"],
        },
    },
    {
        "id": "low_tariff_due_to_last_inspection_and_violation",
        "given": {
            "old_impacts": [],
            "new_inspections": [
                {
                    "utc_controller_complete_dttm": "2020-03-01 13:00:00",
                    "utc_toloka_assigned_dttm": "2020-03-01 17:00:00",
                    "inspection_id": "i1",
                    "order_id": "o1",
                    "order_tariff": "comfortplus",
                    "city": "Москва",
                    "utc_order_dt": "2020-03-01",
                    "questions": [
                        {"question_code": "car_interior", "value": -1},
                        {"question_code": "car_exterior", "value": -1},
                        {"question_code": "driving_style", "value": -1},
                    ],
                }
            ]
        },
        "expected_new_impact": {
            "utc_controller_complete_dttm": "2020-03-01 13:00:00",
            "utc_toloka_assigned_dttm": "2020-03-01 17:00:00",
            "inspection_id": "i1",
            "order_id": "o1",
            "order_tariff": "comfortplus",
            "action_code": 1,
            "exam_cnt": 2,
            "penalty_sum": 0,
            # There is both 'car_interior' violation and error count violation.
            # We choose the former as the impact reason.
            "problem_list": ["car_interior"],
        },
    },
    {
        "id": "penalty",
        "given": {
            "old_impacts": [],
            "new_inspections": [
                {
                    "utc_controller_complete_dttm": "2020-03-01 13:00:00",
                    "utc_toloka_assigned_dttm": "2020-03-01 17:00:00",
                    "inspection_id": "i1",
                    "order_id": "o1",
                    "order_tariff": "vip",
                    "city": "Москва",
                    "utc_order_dt": "2020-03-01",
                    "questions": [
                        {"question_code": "car_exterior", "value": -1},
                    ],
                }
            ]
        },
        "expected_new_impact": {
            "utc_controller_complete_dttm": "2020-03-01 13:00:00",
            "utc_toloka_assigned_dttm": "2020-03-01 17:00:00",
            "inspection_id": "i1",
            "order_id": "o1",
            "order_tariff": "vip",
            "action_code": 2,
            "exam_cnt": 2,
            "penalty_sum": 1000,
            "problem_list": ["car_exterior"],
        },
    },
    {
        "id": "warning_long_after_warning",
        "given": {
            "old_impacts": [
                {
                    "utc_created_dttm": "2019-06-02 12:00:00",
                    "utc_controller_complete_dttm": "2019-06-01 13:00:00",
                    "utc_toloka_assigned_dttm": "2019-06-01 17:00:00",
                    "inspection_id": "i0",
                    "order_id": "o0",
                    "order_tariff": "comfortplus",
                    "action_code": 3,
                    "exam_cnt": 1,
                    "penalty_sum": 0,
                    "problem_list": ["dresscode"],
                }
            ],
            "new_inspections": [
                {
                    "utc_controller_complete_dttm": "2020-03-01 13:00:00",
                    "utc_toloka_assigned_dttm": "2020-03-01 17:00:00",
                    "inspection_id": "i1",
                    "order_id": "o1",
                    "order_tariff": "comfortplus",
                    "city": "Москва",
                    "utc_order_dt": "2020-03-01",
                    "questions": [
                        {"question_code": "dresscode", "value": -1},
                    ],
                }
            ]
        },
        "expected_new_impact": {
            "utc_controller_complete_dttm": "2020-03-01 13:00:00",
            "utc_toloka_assigned_dttm": "2020-03-01 17:00:00",
            "inspection_id": "i1",
            "order_id": "o1",
            "order_tariff": "comfortplus",
            "action_code": 3,  # That is, 'warning'. If the old impact was more recent, it would've been 'low_tariff'.
            "exam_cnt": 1,
            "penalty_sum": 0,
            "problem_list": ["dresscode"],
        },
    },
    {
        "id": "newer_order_before_older_order",
        "given": {
            "old_impacts": [
                {
                    "utc_created_dttm": "2020-02-29 12:00:00",
                    "utc_controller_complete_dttm": "2020-02-28 13:00:00",
                    "utc_toloka_assigned_dttm": "2020-02-28 17:00:00",
                    "inspection_id": "i0",
                    "order_id": "o0",
                    "order_tariff": "vip",
                    "action_code": 3,
                    "exam_cnt": 1,
                    "penalty_sum": 0,
                    "problem_list": ["dresscode"],
                }
            ],
            "new_inspections": [
                {
                    "utc_controller_complete_dttm": "2020-02-27 18:00:00",
                    "utc_toloka_assigned_dttm": "2020-03-02 18:00:00",
                    "inspection_id": "i1",
                    "order_id": "o1",
                    "order_tariff": "vip",
                    "city": "Москва",
                    "utc_order_dt": "2020-03-01",
                    "questions": [
                        {"question_code": "dresscode", "value": -1},
                    ],
                }
            ]
        },
        "expected_new_impact": {
            "utc_controller_complete_dttm": "2020-02-27 18:00:00",
            "utc_toloka_assigned_dttm": "2020-03-02 18:00:00",
            "inspection_id": "i1",
            "order_id": "o1",
            "order_tariff": "vip",
            "action_code": 1,
            "exam_cnt": 0,
            "penalty_sum": 0,
            "problem_list": ["dresscode"],
        },
    },
    {
        "id": "cross_tariff_impact",
        "given": {
            "old_impacts": [
                {
                    "utc_created_dttm": "2020-02-29 12:00:00",
                    "utc_controller_complete_dttm": "2020-02-28 13:00:00",
                    "utc_toloka_assigned_dttm": "2020-02-28 17:00:00",
                    "inspection_id": "i0",
                    "order_id": "o0",
                    "order_tariff": "comfortplus",
                    "action_code": 3,
                    "exam_cnt": 1,
                    "penalty_sum": 0,
                    "problem_list": ["dresscode"],
                }
            ],
            "new_inspections": [
                {
                    "utc_controller_complete_dttm": "2020-03-01 15:00:00",
                    "utc_toloka_assigned_dttm": "2020-03-02 18:00:00",
                    "inspection_id": "i1",
                    "order_id": "o1",
                    "order_tariff": "vip",
                    "city": "Москва",
                    "utc_order_dt": "2020-03-01",
                    "questions": [
                        {"question_code": "dresscode", "value": -1},
                    ],
                }
            ]
        },
        "expected_new_impact": {
            "utc_controller_complete_dttm": "2020-03-01 15:00:00",
            "utc_toloka_assigned_dttm": "2020-03-02 18:00:00",
            "inspection_id": "i1",
            "order_id": "o1",
            "order_tariff": "vip",
            "action_code": 1,
            "exam_cnt": 0,
            "penalty_sum": 0,
            "problem_list": ["dresscode"],
        },
    }
]


@pytest.fixture(scope="module")
def given_source_tables(slow_test_settings):
    # The settings are patched automatically only in function-scoped fixtures.
    # So here we patch them explicitly.
    with slow_test_settings():
        # Fill the target table.
        etl.init_target_table(SummaryAggInspectionImpacts)
        op.write_yt_table(
            YTMeta(SummaryAggInspectionImpacts).target_path(),
            get_given_agg_inspection_impacts_rows(CASES),
        )
        # Fill dm_inspection.
        etl.init_target_table(SummaryDMInspection)
        op.write_yt_table(
            YTMeta(SummaryDMInspection).target_path(),
            get_given_dm_inspection_rows(CASES),
        )
        # Fill inspection_actions.
        etl.init_target_table(InspectionActions)
        op.write_yt_table(YTMeta(InspectionActions).target_path(), INSPECTION_ACTIONS)
        # Fill inspection_tariff_settings.
        etl.init_target_table(InspectionTariffSettings)
        op.write_yt_table(
            YTMeta(InspectionTariffSettings).target_path(), INSPECTION_TARIFF_SETTINGS
        )


@pytest.fixture(scope="module")
def actual_impacts_all_cases(given_source_tables, slow_test_settings):
    # pylint: disable=unused-argument
    with slow_test_settings():
        # FixMe: After https://st.yandex-team.ru/TAXIDWH-7869 replace this with query from loader:
        query = YqlEtlQuery \
            .from_file(
                from_same_directory(agg_inspection_impacts.__file__, 'query.yql'),
                meta=YTMeta(SummaryAggInspectionImpacts),
                loader=RotationInsertLoader(),
                dst_backquote=True
            ).add_params(
                start_dttm='2020-03-01 10:00:00',
                current_dttm='2020-04-01 10:00:00',
                min_dttm='2020-02-01 00:00:00',
                min_unix_dttm='1970-01-01 00:00:00',
                pool=get_pool_value(Pool.TAXI_DWH_PRIORITY),
                inspection_actions=add_backquote(YTMeta(InspectionActions).target_path()),
                inspection_tariff_settings=add_backquote(YTMeta(InspectionTariffSettings).target_path()),
                dm_inspection=add_backquote(YTMeta(SummaryDMInspection).target_path()),
                agg_inspection_impacts=add_backquote(YTMeta(SummaryAggInspectionImpacts).target_path())
            ) \
            .use_native_query()
        query.execute()

        result = list(op.read_yt_table(YTMeta(SummaryAggInspectionImpacts).rotation_path()))
    yield result


@pytest.mark.slow
@pytest.mark.parametrize("case", [pytest.param(case, id=case["id"]) for case in CASES])
def test_agg_inspection_impacts(case, actual_impacts_all_cases):
    expected_new_impact = get_expected_new_impact(case)

    actual_impacts = get_actual_impacts(case, actual_impacts_all_cases)

    old_impact_ids = {impact["order_id"] for impact in case["given"]["old_impacts"]}
    actual_new_impacts = [
        impact for impact in actual_impacts if impact["impact_id"] not in old_impact_ids
    ]

    assert 1 == len(actual_new_impacts), "Expected exactly one new impact"
    actual_new_impact = actual_new_impacts[0]

    assert expected_new_impact == {
        k: actual_new_impact.get(k) for k in expected_new_impact
    }
