from nile.api.v1 import Record
from projects.discounts.feature_extractors.v1 import FeaturesExtractor


def test_feature_extractor():
    features_extractors_params = {
        'num_features': {
            'features': [
                'num_a_{window}_{num_aggr_option}',
                'num_b_{window}',
                'num_c',
                'last_absent_days',
                'last_absent_days_some_text',
            ],
            'options': {'window': [1], 'num_aggr_option': ['aggr1', 'aggr2']},
        },
        'cat_features': {
            'features': [
                'cat_a_{window}_{cat_aggr_option}',
                'cat_b_{window}',
                'cat_c',
            ],
            'options': {'window': [2], 'cat_aggr_option': ['aggr3']},
        },
        'distr_features': {
            'features': [
                'distr_1_{window}_cat_distribution{param1}',
                'distr_2_{window}_cat_distribution{param2}',
            ],
            'options': {'window': [3]},
            'distr_dict': {
                'param1': ['value1', 'value2'],
                'param2': ['value3', 'value4', '_others_'],
            },
        },
    }

    fe = FeaturesExtractor(features_extractors_params)

    assert fe(Record({})) == {
        'cat_c': '',
        'cat_a_2_aggr3': '',
        'cat_b_2': '',
        'num_c': 0,
        'num_a_1_aggr2': 0,
        'num_a_1_aggr1': 0,
        'num_b_1': 0,
        'last_absent_days_some_text': 1,
        'last_absent_days': 1,
        'distr_1_3_cat_distributionvalue1': 0,
        'distr_1_3_cat_distributionvalue2': 0,
        'distr_2_3_cat_distributionvalue3': 0,
        'distr_2_3_cat_distributionvalue4': 0,
        'distr_2_3_cat_distribution_others_': 0,
    }

    assert fe(Record({'cat_c': 'cat_value', 'num_a_1_aggr2': 13})) == {
        'cat_c': 'cat_value',
        'cat_a_2_aggr3': '',
        'cat_b_2': '',
        'num_c': 0,
        'num_a_1_aggr2': 13,
        'num_a_1_aggr1': 0,
        'num_b_1': 0,
        'last_absent_days_some_text': 1,
        'last_absent_days': 1,
        'distr_1_3_cat_distributionvalue1': 0,
        'distr_1_3_cat_distributionvalue2': 0,
        'distr_2_3_cat_distributionvalue3': 0,
        'distr_2_3_cat_distributionvalue4': 0,
        'distr_2_3_cat_distribution_others_': 0,
    }

    assert (
        fe(Record({'distr_1_3_cat_distribution': {'value1': 1, 'value3': 1}}))
        == {
            'cat_c': '',
            'cat_a_2_aggr3': '',
            'cat_b_2': '',
            'num_c': 0,
            'num_a_1_aggr2': 0,
            'num_a_1_aggr1': 0,
            'num_b_1': 0,
            'last_absent_days_some_text': 1,
            'last_absent_days': 1,
            'distr_1_3_cat_distributionvalue1': 0.5,
            'distr_1_3_cat_distributionvalue2': 0,
            'distr_2_3_cat_distributionvalue3': 0,
            'distr_2_3_cat_distributionvalue4': 0,
            'distr_2_3_cat_distribution_others_': 0,
        }
    )

    assert (
        fe(Record({'distr_2_3_cat_distribution': {'value3': 1, 'value5': 1}}))
        == {
            'cat_c': '',
            'cat_a_2_aggr3': '',
            'cat_b_2': '',
            'num_c': 0,
            'num_a_1_aggr2': 0,
            'num_a_1_aggr1': 0,
            'num_b_1': 0,
            'last_absent_days_some_text': 1,
            'last_absent_days': 1,
            'distr_1_3_cat_distributionvalue1': 0,
            'distr_1_3_cat_distributionvalue2': 0,
            'distr_2_3_cat_distributionvalue3': 0.5,
            'distr_2_3_cat_distributionvalue4': 0,
            'distr_2_3_cat_distribution_others_': 0.5,
        }
    )
