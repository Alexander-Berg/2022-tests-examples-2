import pytest
from nile.api.v1 import filters as nf
from dmp_suite.yt.loaders import YqlEtlQuery, RotationInsertLoader
import dmp_suite.nile.cluster_utils as cu

from dmp_suite.yt import YTTable, Date, Int, YTMeta, etl
from connection.yt import get_yt_client
from test_dmp_suite.yt.utils import fixture_random_yt_table


class TestTable(YTTable):
    dt = Date()
    value = Int()


test_table = fixture_random_yt_table(TestTable)


@pytest.mark.slow
def test_nile_yql_yt_wrapper_under_one_transaction(test_table):
    initial_data = [
        dict(dt='2018-01-01', value=10),
        dict(dt='2018-01-02', value=25)
    ]

    first_stage_expected_result = [
        dict(dt='2018-01-01', value=110),
        dict(dt='2018-01-02', value=125)
    ]

    second_stage_expected_result = [
        dict(dt='2018-01-02', value=125)
    ]

    def complex_loader(meta, transaction_id=None):
        """Runs yql query and nile job"""
        etl.init_buffer_table(meta)
        get_yt_client().write_table(
            meta.buffer_path(),
            initial_data
        )

        # First Stage
        query = (
            YqlEtlQuery
            .from_string(
                query_string='INSERT INTO `{dst_table}` WITH TRUNCATE \n'
                             'SELECT dt, value + 100 as value \n'
                             'from `{src_table}`',
                meta=meta,
                loader=RotationInsertLoader(transaction_id=transaction_id)
            )
            .use_native_query()
            .add_params(src_table=meta.buffer_path())
        )
        query.execute_with_loader()

        first_stage_result = list(get_yt_client().read_table(meta.target_path()))
        assert first_stage_expected_result == first_stage_result

        # Second Stage
        job = etl.cluster_job(meta)

        stream = (
            job
            .table(meta.target_path())
            .filter(nf.equals('value', 125))
            .put(meta.target_path())
        )

        cu.run_with_transaction(job, external_tx=transaction_id)

        second_stage_result = list(get_yt_client().read_table(meta.target_path()))
        assert second_stage_expected_result == second_stage_result

    meta = YTMeta(test_table)

    with get_yt_client().Transaction() as transaction:
        complex_loader(
            meta=meta,
            transaction_id=transaction.transaction_id
        )
