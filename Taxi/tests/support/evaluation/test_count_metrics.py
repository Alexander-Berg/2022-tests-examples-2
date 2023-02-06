from ciso8601 import parse_datetime_as_naive
import numpy as np
import pandas as pd

from projects.support.evaluation import count_metrics
from projects.support.factory import SupportFactory


def test_clustering(load_json):
    factory = SupportFactory(
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-05T00:00:00Z'),
        resources_dir='projects/tests/support/static/test_factory',
        response_load='embedding_clustering_response',
    )

    data_df = pd.DataFrame(load_json('data_clustering.json'))

    assert np.isclose(
        count_metrics.clustering_adjusted_rand_score(
            data_df=data_df,
            response_column='response_body_clustered',
            topic_column='true_topics',
            response_parser=factory.create_response_parser,
            round_decimals=3,
        )[0].value,
        -0.055,
    )

    result = count_metrics.clustering_homogeneity_completeness_v_measure(
        data_df=data_df,
        response_column='response_body_clustered',
        topic_column='true_topics',
        response_parser=factory.create_response_parser,
        round_decimals=3,
        beta=0.5,
    )
    assert np.isclose(result[0].value, 0.577)
    assert np.isclose(result[1].value, 0.376)
    assert np.isclose(result[2].value, 0.49)

    result = count_metrics.clustering_purity_inv_purity_purity_f_measure(
        data_df=data_df,
        response_column='response_body_clustered',
        topic_column='true_topics',
        response_parser=factory.create_response_parser,
        round_decimals=3,
        beta=0.5,
    )
    assert np.isclose(result[0].value, 0.5)
    assert np.isclose(result[1].value, 0.333)
    assert np.isclose(result[2].value, 0.429)

    result = count_metrics.clustering_bcubed(
        data_df=data_df,
        response_column='response_body_clustered',
        topic_column='true_topics',
        response_parser=factory.create_response_parser,
        round_decimals=3,
        beta=0.5,
    )
    assert np.isclose(result[0].value, 0.714)
    assert np.isclose(result[1].value, 0.429)
    assert np.isclose(result[2].value, 0.584)

    assert np.isclose(
        count_metrics.clustering_ami(
            data_df=data_df,
            response_column='response_body_clustered',
            topic_column='true_topics',
            response_parser=factory.create_response_parser,
            round_decimals=3,
        )[0].value,
        -0.063,
    )

    assert np.isclose(
        count_metrics.clustering_ksenia_metric(
            data_df=data_df,
            response_column='response_body_clustered',
            topic_column='true_topics',
            response_parser=factory.create_response_parser,
            round_decimals=3,
        )[0].value,
        0.375,
    )


def test_classification(load_json):
    factory = SupportFactory(
        begin_dttm=parse_datetime_as_naive('2020-02-02T00:00:00Z'),
        end_dttm=parse_datetime_as_naive('2020-02-05T00:00:00Z'),
        resources_dir='projects/tests/support/static/test_factory',
        response_load='common_response',
    )

    data_df = pd.DataFrame(load_json('data_classification.json'))

    result = count_metrics.classification_pearson(
        data_df=data_df,
        response_column='response_body_clustered',
        topic_column='true_topics',
        response_parser=factory.create_response_parser,
        round_decimals=3,
    )
    assert result[0].metric == 'pearson_coefficient'
    assert result[1].metric == 'pearson_p_value'

    result = count_metrics.classification_spearman(
        data_df=data_df,
        response_column='response_body_clustered',
        topic_column='true_topics',
        response_parser=factory.create_response_parser,
        round_decimals=3,
    )
    assert result[0].metric == 'spearman_coefficient'
    assert result[1].metric == 'spearman_p_value'
