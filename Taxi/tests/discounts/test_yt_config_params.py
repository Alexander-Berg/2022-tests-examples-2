from projects.discounts.common.features_parser import get_yt_config_params


def test_yt_config_params():
    fe_params = {
        'num_features': {
            'features': [
                'num_a_{window}_{num_aggr_option}',
                'num_b_{window}',
                'num_c',
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
            'features': ['distr_{window}_cat_distribution{param1}'],
            'options': {'window': [3]},
            'distr_dict': {'param1': ['value1', 'value2']},
        },
    }

    train_params = {
        'target_column': 'target',
        'weight_column': 'weight',
        'num_features': {
            'features': ['num_c'],
            'options': {'window': [1], 'num_aggr_option': ['aggr1']},
        },
        'cat_features': {
            'features': [],
            'options': {'window': [2], 'cat_aggr_option': ['aggr3']},
        },
        'distr_features': {
            'features': ['distr_{window}_cat_distribution{param1}'],
            'options': {'window': [3]},
            'distr_dict': {'param1': ['value1']},
        },
    }

    assert get_yt_config_params(fe_params, train_params) == {
        'target_column': 'target',
        'weight_column': 'weight',
        'num_columns': [
            'distr_3_cat_distributionvalue1',
            'distr_3_cat_distributionvalue2',
            'num_a_1_aggr1',
            'num_a_1_aggr2',
            'num_b_1',
            'num_c',
        ],
        'categorical_columns': ['cat_a_2_aggr3', 'cat_b_2', 'cat_c'],
        'ignore_columns': [
            'cat_a_2_aggr3',
            'cat_b_2',
            'cat_c',
            'distr_3_cat_distributionvalue2',
            'num_a_1_aggr1',
            'num_a_1_aggr2',
            'num_b_1',
        ],
    }
