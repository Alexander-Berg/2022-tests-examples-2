from operator import itemgetter
import pytest

from connection.yt import Pool, get_pool_value
from dmp_suite.file_utils import from_same_directory
from dmp_suite.yql import add_backquote
from dmp_suite.yt import YTMeta, etl, operation as op
from dmp_suite.yt.loaders import YqlEtlQuery, RotationInsertLoader

from taxi_etl.layer.yt.raw.googledocs import InspectionAnswers, InspectionTariffCodes
from taxi_etl.layer.yt.ods.forms import OdsFormsInspection
from taxi_etl.layer.yt.ods.mdb import OdsOrder
from taxi_etl.layer.yt.ods.taxi_photocontrol import OdsTaxiPhotocontrolInspectionAssessment
from taxi_etl.layer.yt.summary import SummaryAggInspectionAllChecks, agg_inspection_all_checks

from .impl import *
from .data import *


@pytest.fixture(scope='module')
def given_source_tables(slow_test_settings):
    with slow_test_settings():
        ods_order_path = YTMeta(OdsOrder).target_folder_path + "/2020-06-01"
        op.init_yt_table(ods_order_path, YTMeta(OdsOrder).attributes())
        op.write_yt_table(
            ods_order_path,
            ods_order_rows(CASES)
        )

        etl.init_target_table(OdsFormsInspection)
        op.write_yt_table(
            YTMeta(OdsFormsInspection).target_path(),
            ods_forms_inspection_rows(CASES)
        )

        etl.init_target_table(OdsTaxiPhotocontrolInspectionAssessment)
        op.write_yt_table(
            YTMeta(OdsTaxiPhotocontrolInspectionAssessment).target_path(),
            ods_toloka_rows(CASES)
        )

        etl.init_target_table(InspectionAnswers)
        op.write_yt_table(
            YTMeta(InspectionAnswers).target_path(),
            INSPECTION_ANSWERS
        )

        etl.init_target_table(InspectionTariffCodes)
        op.write_yt_table(
            YTMeta(InspectionTariffCodes).target_path(),
            INSPECTION_TARIFF_CODES
        )


@pytest.fixture(scope='module')
def actual_all_checks_all_cases(given_source_tables, slow_test_settings):
    # FixMe: After https://st.yandex-team.ru/TAXIDWH-7869 replace this with query from loader:
    with slow_test_settings():
        query = YqlEtlQuery \
            .from_file(
                from_same_directory(agg_inspection_all_checks.__file__, 'query.yql'),
                meta=YTMeta(SummaryAggInspectionAllChecks),
                loader=RotationInsertLoader(),
                dst_backquote=True
            ) \
            .add_params(
                start_dttm="2020-06-01 00:00:00",
                end_dttm="2020-06-30 23:59:59",
                start_month="2020-06-01",
                pool=get_pool_value(Pool.TAXI_DWH_PRIORITY),
                ods_order_path=add_backquote(YTMeta(OdsOrder).target_folder_path),
                forms_inspection_path=add_backquote(YTMeta(OdsFormsInspection).target_path()),
                inspection_assessment_path=add_backquote(YTMeta(OdsTaxiPhotocontrolInspectionAssessment).target_path()),
                googledocs_answers_path=add_backquote(YTMeta(InspectionAnswers).target_path()),
                googledocs_tariff_codes_path=add_backquote(YTMeta(InspectionTariffCodes).target_path())
            ) \
            .use_native_query()
        query.execute()

        result = list(op.read_yt_table(YTMeta(SummaryAggInspectionAllChecks).rotation_path()))
    yield result


@pytest.mark.slow
@pytest.mark.parametrize("case", [pytest.param(case, id=case["id"]) for case in CASES])
def test_agg_inspection_all_checks(case, actual_all_checks_all_cases):
    expected = sorted(expected_inspections(case), key=itemgetter('inspection_id', 'question_id'))
    actual = sorted(actual_inspections(case, actual_all_checks_all_cases), key=itemgetter('inspection_id', 'question_id'))
    assert len(expected) == len(actual)
    for i in range(len(expected)):
        assert expected[i] == {k: actual[i][k] for k in expected[i].keys()}
