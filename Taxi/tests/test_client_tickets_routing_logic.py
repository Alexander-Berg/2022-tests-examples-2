import numpy as np

from taxi_pyml.client_tickets_routing import probs_postprocessor


def test_urgent_keywords(load_json):
    class_names_config = load_json('class_names_config.json')
    keywords_config = load_json('keywords_config.json')
    postprocessor_config = load_json('postprocessor_config.json')
    test_data = load_json('test_urgent_keywords.json')
    class_probs = np.array(list(test_data['class_probs'].values()))

    preprocessed_result = probs_postprocessor.apply_business_logic(
        test_data['comment'],
        class_probs,
        class_names_config,
        keywords_config,
        postprocessor_config['thresholds'],
    )
    assert (
        preprocessed_result.predicted_class == probs_postprocessor.URGENT_CLASS
    )
    assert preprocessed_result.ml_class == probs_postprocessor.OTHER_CLASS
    assert preprocessed_result.urgent_keywords_triggered == 1
    assert preprocessed_result.lost_item_second_keywords_triggered == 0


def test_urgent_strong(load_json):
    class_names_config = load_json('class_names_config.json')
    keywords_config = load_json('keywords_config.json')
    postprocessor_config = load_json('postprocessor_config.json')
    test_data = load_json('test_urgent_strong.json')
    class_probs = np.array(list(test_data['class_probs'].values()))

    preprocessed_result = probs_postprocessor.apply_business_logic(
        test_data['comment'],
        class_probs,
        class_names_config,
        keywords_config,
        postprocessor_config['thresholds'],
    )
    assert (
        preprocessed_result.predicted_class
        == probs_postprocessor.URGENT_STRONG_CLASS
    )
    assert (
        preprocessed_result.ml_class == probs_postprocessor.URGENT_STRONG_CLASS
    )
    assert preprocessed_result.urgent_keywords_triggered == 0
    assert preprocessed_result.lost_item_second_keywords_triggered == 0


def test_lost_item_second_keywords(load_json):
    class_names_config = load_json('class_names_config.json')
    keywords_config = load_json('keywords_config.json')
    postprocessor_config = load_json('postprocessor_config.json')
    test_data = load_json('test_lost_item_second_keywords.json')
    class_probs = np.array(list(test_data['class_probs'].values()))

    preprocessed_result = probs_postprocessor.apply_business_logic(
        test_data['comment'],
        class_probs,
        class_names_config,
        keywords_config,
        postprocessor_config['thresholds'],
    )
    assert (
        preprocessed_result.predicted_class
        == probs_postprocessor.LOST_ITEM_SECOND_CLASS
    )
    assert (
        preprocessed_result.ml_class
        == probs_postprocessor.LOST_ITEM_FIRST_CLASS
    )
    assert preprocessed_result.urgent_keywords_triggered == 0
    assert preprocessed_result.lost_item_second_keywords_triggered == 1


def test_not_urgent_keywords(load_json):
    class_names_config = load_json('class_names_config.json')
    keywords_config = load_json('keywords_config.json')
    postprocessor_config = load_json('postprocessor_config.json')
    test_data = load_json('test_not_urgent_keywords.json')
    class_probs = np.array(list(test_data['class_probs'].values()))

    preprocessed_result = probs_postprocessor.apply_business_logic(
        test_data['comment'],
        class_probs,
        class_names_config,
        keywords_config,
        postprocessor_config['thresholds'],
    )
    assert (
        preprocessed_result.predicted_class
        == probs_postprocessor.CAR_ACCIDENT_CLASS
    )
    assert (
        preprocessed_result.ml_class == probs_postprocessor.CAR_ACCIDENT_CLASS
    )
    assert preprocessed_result.urgent_keywords_triggered == 0
    assert preprocessed_result.lost_item_second_keywords_triggered == 0


def test_lost_item_second(load_json):
    class_names_config = load_json('class_names_config.json')
    keywords_config = load_json('keywords_config.json')
    postprocessor_config = load_json('postprocessor_config.json')
    test_data = load_json('test_lost_item_second.json')
    class_probs = np.array(list(test_data['class_probs'].values()))

    preprocessed_result = probs_postprocessor.apply_business_logic(
        test_data['comment'],
        class_probs,
        class_names_config,
        keywords_config,
        postprocessor_config['thresholds'],
    )
    assert (
        preprocessed_result.predicted_class
        == probs_postprocessor.LOST_ITEM_SECOND_CLASS
    )
    assert (
        preprocessed_result.ml_class
        == probs_postprocessor.LOST_ITEM_SECOND_CLASS
    )
    assert preprocessed_result.urgent_keywords_triggered == 0
    assert preprocessed_result.lost_item_second_keywords_triggered == 0
