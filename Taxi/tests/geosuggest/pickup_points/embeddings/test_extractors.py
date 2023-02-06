from projects.geosuggest.common import kernels
from projects.geosuggest.pickup_points.embeddings import features
from projects.geosuggest.pickup_points.embeddings import priority_extractors
from projects.geosuggest.pickup_points.embeddings import targets_extractors
from projects.geosuggest.pickup_points.embeddings import stats_extractors
import helpers


def test_features_extractors():
    point = helpers.create_point()
    kernels_list = [kernels.GaussianKernel() for _ in range(3)]

    pin_features_extractor = features.PinFeaturesExtractor(
        distance_kernels=kernels_list,
        angle_kernels=kernels_list,
        rotations_count=4,
    )
    order_stop_features_extractor = features.OrderStopFeaturesExtractor(
        time_kernels=kernels_list,
        edge_kernels=kernels_list,
        distance_kernels=kernels_list,
        angle_kernels=kernels_list,
        rotations_count=4,
    )

    pin_features_extractor(pin=helpers.create_pin(), point=point)
    order_stop_features_extractor(
        order_stop=helpers.create_order_stop(),
        point=point,
        reference_timestamp=0,
    )
    maps_objects_features = features.MapsObjectsFeaturesExtractor(
        distance_kernels=kernels_list,
        angle_kernels=kernels_list,
        rotations_count=4,
    )
    maps_objects_features(
        point=point, maps_object=helpers.create_maps_object(),
    )


def test_priority_extractors():
    point = helpers.create_point()

    priority_extractors.OrderStopPriorityExtractor()(
        request=point, candidate=helpers.create_order_stop(), record=None,
    )
    priority_extractors.MapsObjectDistanceExtractor()(
        request=point, candidate=helpers.create_maps_object(), record=None,
    )


def test_stats_extractors():
    point = helpers.create_point()
    stats_extractors.PopularityStatsExtractor()(
        points_list=[point],
        order_stop=helpers.create_order_stop(),
        reference_timestamp=0,
    )


def test_targets_extractors():
    point = helpers.create_point()
    candidates = [point for _ in range(5)]
    extractor = targets_extractors.EdgeTargetsExtractor(max_edge_distance=10)
    extractor(
        request=helpers.create_order_stop(),
        candidates=candidates,
        record=None,
    )
