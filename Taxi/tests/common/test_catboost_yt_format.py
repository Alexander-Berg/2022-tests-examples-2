from taxi.ml.nirvana.common.catboost import YTRecordsPoolConfig


def test_clean_feature_names():
    yt_config = YTRecordsPoolConfig(num_columns=['a', 'b'])
    assert yt_config.feature_names == yt_config.model_feature_names

    yt_config_2 = YTRecordsPoolConfig(
        num_columns=['a', 'b'], ignore_columns=['b'],
    )
    assert 'b' not in yt_config_2.model_feature_names
    assert 'b' in yt_config_2.feature_names


def test_ignore_columns():

    # baseline
    yt_config = YTRecordsPoolConfig(categorical_columns=['a', 'b'])
    assert yt_config.catboost_yt_format == '\n0\tDocId\n1\tCateg\n2\tCateg'

    # with ignore columns - check that ignore is not in categorical
    yt_config_2 = YTRecordsPoolConfig(
        categorical_columns=['a', 'b'], ignore_columns=['b'],
    )
    assert (
        yt_config_2.catboost_yt_format == '\n0\tDocId\n1\tCateg\n2\tAuxiliary'
    )

    # with tagret - check that indexing is not overlapped (offset is working)
    yt_config_3 = YTRecordsPoolConfig(
        target_column='c',
        categorical_columns=['a', 'b'],
        ignore_columns=['b'],
    )
    assert (
        yt_config_3.catboost_yt_format
        == '\n0\tDocId\n1\tLabel\n2\tCateg\n3\tAuxiliary'
    )
