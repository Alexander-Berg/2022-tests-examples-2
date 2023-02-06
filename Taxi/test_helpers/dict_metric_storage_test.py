from atlas.domain.metric import MetricsStorage
from test_helpers.dict_metric_storage import DictMetricsStorage


def test_dict_storage_has_same_interface_as_mongo_storage():
    assert dir(MetricsStorage) == dir(DictMetricsStorage)
