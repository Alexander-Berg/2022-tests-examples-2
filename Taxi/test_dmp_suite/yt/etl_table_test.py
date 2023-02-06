from dmp_suite.yt import etl_table, YTTable, ETLTable, Datetime, String


def test_is_etl_table():
    class NonEtl(YTTable):
        pass

    assert not etl_table.is_etl_table(NonEtl)

    class Etl(ETLTable):
        pass

    assert etl_table.is_etl_table(Etl)

    class DuckTypingEtl(YTTable):
        etl_updated = Datetime(name=etl_table.ETL_UPDATED)

    assert etl_table.is_etl_table(DuckTypingEtl)

    class DuckTypingNonEtl(YTTable):
        etl_updated = String(name=etl_table.ETL_UPDATED)

    assert not etl_table.is_etl_table(DuckTypingNonEtl)
