import numpy as np

from projects.supportai.learning import metrics
from taxi_pyml.supportai.common import model_topics


def test_named_precisions(load_json):
    model_topics_config = [
        model_topics.Topic.deserialize(topic)
        for topic in load_json('model_topics_config.json')
    ]
    topic_slugs = [topic.slug for topic in model_topics_config]
    data = load_json('data.json')
    true_labels = np.array(data['true_labels'])
    pred_labels = np.array(data['pred_labels'])
    probabilities = np.array(data['probabilities'])

    named_precisions = metrics.named_precisions(
        true_labels, probabilities, pred_labels, topic_slugs,
    )

    assert named_precisions['topic_one'] == 0.5
    assert named_precisions['topic_two'] == 0.5


def test_named_recalls(load_json):
    model_topics_config = [
        model_topics.Topic.deserialize(topic)
        for topic in load_json('model_topics_config.json')
    ]
    topic_slugs = [topic.slug for topic in model_topics_config]
    data = load_json('data.json')
    true_labels = np.array(data['true_labels'])
    pred_labels = np.array(data['pred_labels'])
    probabilities = np.array(data['probabilities'])

    named_precisions = metrics.named_recalls(
        true_labels, probabilities, pred_labels, topic_slugs,
    )

    assert named_precisions['topic_one'] == 0.5
    assert named_precisions['topic_two'] == 0.5
