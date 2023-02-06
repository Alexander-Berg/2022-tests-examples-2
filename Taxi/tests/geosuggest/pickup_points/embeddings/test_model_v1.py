import pytest
import torch
from nile.api.v1 import Record

from projects.geosuggest.pickup_points.embeddings.models import v1 as model
from projects.geosuggest.pickup_points.embeddings.models.v1.objects import (
    PointRequest,
    PointFeatures,
    PointFeaturesBatch,
    PinRequest,
    PinFeatures,
    PinFeaturesBatch,
)
import helpers


def test_features_extractors():
    point = helpers.create_point()
    pin = helpers.create_pin()
    order_stop = helpers.create_order_stop()
    maps_object = helpers.create_maps_object()
    graph_info = helpers.create_graph_info()

    point_request = PointRequest(
        point=point,
        popularity_statistics=[1, 2, 34],
        history_stops=[order_stop for _ in range(2)],
        maps_objects=[maps_object for _ in range(2)],
        graph_info=graph_info,
        reference_timestamp=1,
    )
    point_extractor = model.PointFeaturesExtractor()
    point_extractor(point_request)

    pin_request = PinRequest(pin=pin, point=point)
    pin_extractor = model.PinFeaturesExtractor()
    pin_extractor(pin_request)


def create_features_batches(batch_size=1, history_size=1, maps_objects_size=1):
    point_batch, pin_batch = PointFeaturesBatch(), PinFeaturesBatch()
    pin_features = [0]
    history_stops_features = [[1, 1] for _ in range(history_size)]
    maps_objects_features = [[1, 1, 1] for _ in range(maps_objects_size)]
    popularity_stats_features = [2, 3]
    graph_features = [4, 5]
    for _ in range(batch_size):
        point_batch.add(
            PointFeatures(
                history_stops_features=history_stops_features,
                maps_objects_features=maps_objects_features,
                popularity_stats_features=popularity_stats_features,
                graph_features=graph_features,
            ),
        )
        pin_batch.add(PinFeatures(features=pin_features))
    return point_batch, pin_batch


@pytest.mark.parametrize('history_size', [0, 2])
@pytest.mark.parametrize('maps_objects_size', [0, 1])
def test_net(history_size, maps_objects_size, batch_size=2):
    point_batch, pin_batch = create_features_batches(
        batch_size=batch_size,
        history_size=history_size,
        maps_objects_size=maps_objects_size,
    )
    net = model.Net(
        popularity_stats_hidden_sizes=[2, 3, 5],
        history_stops_hidden_sizes=[2, 3, 4],
        maps_objects_hidden_sizes=[3, 4, 5],
        graph_hidden_sizes=[2, 4, 5],
        point_embedding_hidden_sizes=[19, 11],
        pin_hidden_sizes=[1, 4],
        popularity_w_pin_hidden_sizes=[15, 5, 5],
        popularity_point_only_hidden_sizes=[14, 10, 5],
        popularity_pin_only_hidden_sizes=[4, 5],
    ).eval()

    result = net.predict_popularity_w_pin(
        point_batch=point_batch, pin_batch=pin_batch,
    )
    assert list(result.size()) == [batch_size, 2]
    assert torch.exp(result).sum().item() == pytest.approx(batch_size)


def test_net_trainers(iterations=4, batch_size=2, records_count=10):
    point_features = PointFeatures(
        popularity_stats_features=[2, 3, 4, 5],
        history_stops_features=[[1, 2], [2, 3], [3, 4]],
        maps_objects_features=[[3, 4, 5], [4, 5, 6]],
        graph_features=[1, 2, 3],
    )
    record = Record(
        target=1,
        weight=1,
        point_features=point_features.to_json(),
        pin_features=PinFeatures(features=[1, 2, 3]).to_json(),
    )
    records_generator = (record for _ in range(records_count))
    net = model.Net(
        popularity_stats_hidden_sizes=[4, 3, 4, 5],
        history_stops_hidden_sizes=[2, 3, 4],
        maps_objects_hidden_sizes=[3, 4, 5],
        graph_hidden_sizes=[3, 4, 5],
        point_embedding_hidden_sizes=[19, 10],
        pin_hidden_sizes=[3, 4],
        popularity_w_pin_hidden_sizes=[14, 5, 5],
        popularity_point_only_hidden_sizes=[10, 10, 5],
        popularity_pin_only_hidden_sizes=[4, 5],
    )
    training_net = model.PopularityNetTrainer(
        iterations=iterations, batch_size=batch_size, print_every=1,
    )
    for net, training_logs in training_net(
            net=net, records_generator=records_generator,
    ):
        assert len(training_logs) == iterations
