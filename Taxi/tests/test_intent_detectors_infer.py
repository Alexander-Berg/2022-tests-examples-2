import json

from supportai_ml.inference.intent_detectors import applier_factory
from supportai_ml.inference.intent_detectors import base_model
from supportai_ml.inference.intent_detectors import thresholds


def test_inheritance() -> None:
    for slug in applier_factory.applier_slug_to_class:
        applier_class = applier_factory.applier_slug_to_class[slug]
        assert issubclass(applier_class, base_model.BaseModel)


def create_const_model_topics_config(
    value: float,
) -> thresholds.Config:
    with open("tests/static/model_topics_config.json", "r") as fin:
        config_serialized = json.load(fin)
    for item in config_serialized:
        item["thresholds"][0]["threshold_based_on_precision"] = value
    return thresholds.Config.deserialize(config_serialized)


def test_thresholds() -> None:
    all_zeros_topic_config = create_const_model_topics_config(0)
    all_ones_topic_config = create_const_model_topics_config(1.0)

    output_probas = [0.0 for _ in range(len(all_zeros_topic_config._config))]
    output_probas[0] = 0.99

    output = all_zeros_topic_config(output_probas)
    assert output.sure_topic == all_zeros_topic_config.get_topic_slug_by(0)
    assert (
        output.most_probable_topic
        == all_zeros_topic_config.get_topic_slug_by(0)
    )
    assert output.probabilities[0].probability == 0.99

    output = all_ones_topic_config(output_probas)
    assert output.sure_topic is None
    assert (
        output.most_probable_topic
        == all_zeros_topic_config.get_topic_slug_by(0)
    )
    assert output.probabilities[0].probability == 0.99
