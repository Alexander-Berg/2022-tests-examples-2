#include "clustering.hpp"

#include <cmath>
#include <iterator>
#include <limits>
#include <utility>

#include <gtest/gtest.h>

#include <fmt/format.h>

#include <testing/taxi_config.hpp>
#include <userver/dynamic_config/storage_mock.hpp>
#include <userver/formats/json.hpp>
#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <defs/all_definitions.hpp>
#include <models/place.hpp>
#include <taxi_config/taxi_config.hpp>
#include <taxi_config/variables/EATS_CATALOG_PLACES_CLUSTERING.hpp>
#include "test_utils.hpp"

namespace eats_catalog::algo {

namespace {

constexpr std::string_view kPlacesClustering = R"({
  "min_intercluster_distance": 30,
  "min_points_in_cluster": 2,
  "bucket_side_length": 1000
})";

using eats_catalog::models::Place;
using eats_catalog::models::PlaceId;
using eats_catalog::models::PlaceInfo;
using ::geometry::BoundingBox;
using ::geometry::Position;

struct IdPosition {
  PlaceId id;
  Position position;
};

IdPosition MakeIdPosition(const int64_t id, const double lon,
                          const double lat) {
  return {PlaceId{id}, MakePosition(lon, lat)};
}

PlacesCluster MakeCluster(const double lon, const double lat,
                          const std::vector<int>& raw_ids) {
  PlacesCluster cluster;
  cluster.centroid = MakePosition(lon, lat);
  cluster.place_ids.resize(raw_ids.size());
  std::transform(raw_ids.begin(), raw_ids.end(), cluster.place_ids.begin(),
                 [](const auto id) { return PlaceId{id}; });
  return cluster;
}

auto PatchConfig(const std::string_view clustering = kPlacesClustering) {
  return dynamic_config::MakeDefaultStorage(
      {{taxi_config::EATS_CATALOG_PLACES_CLUSTERING,
        formats::json::FromString(clustering)}});
}

bool operator==(const PlacesCluster& lhs, const PlacesCluster& rhs) {
  if (!ApproxEqual(lhs.centroid, rhs.centroid)) {
    return false;
  }
  return lhs.place_ids == rhs.place_ids;
}

void PresortIds(std::vector<PlacesCluster>& clusters) {
  for (auto& entry : clusters) {
    std::sort(entry.place_ids.begin(), entry.place_ids.end());
  }
}

bool AreEqual(std::vector<PlacesCluster>& lhs,
              std::vector<PlacesCluster>& rhs) {
  if (lhs.size() != rhs.size()) {
    return false;
  }
  PresortIds(lhs);
  PresortIds(rhs);

  for (const auto& cluster : lhs) {
    auto iter = std::find_if(
        rhs.begin(), rhs.end(),
        [&cluster](const auto& entry) { return cluster == entry; });
    if (iter == rhs.end()) {
      return false;
    }
  }
  return true;
}

struct ClusterTestCase {
  BoundingBox box;
  std::vector<IdPosition> points;
  std::vector<PlacesCluster> expected;
  std::string clustering{kPlacesClustering};
};

void TestFindClusters(ClusterTestCase& tc) {
  std::vector<PlaceInfo> place_infos;
  // reserve нужен, чтобы ссылки на PlaceInfo не инвалидировались
  place_infos.reserve(tc.points.size());
  std::vector<Place> places;
  for (const auto& point : tc.points) {
    auto& place_info = place_infos.emplace_back();
    place_info.id = point.id;
    place_info.location.position = point.position;
    places.emplace_back(place_info);
  }

  std::vector<const Place*> pointers(places.size());
  std::transform(places.begin(), places.end(), pointers.begin(),
                 [](const auto& place) { return &place; });

  auto storage = PatchConfig(tc.clustering);
  auto config = storage.GetSnapshot();

  auto clusters = FindClusters(
      pointers, tc.box, config[taxi_config::EATS_CATALOG_PLACES_CLUSTERING]);
  LOG_WARNING() << "clusters size " << clusters.size();

  EXPECT_TRUE(AreEqual(tc.expected, clusters));
}

}  // namespace

// Places with identical coordiantes are grouped into one cluster
UTEST(FindClusters, IdenticalCoordinates) {
  ClusterTestCase tc{
      {MakePosition(37.556, 55.721),
       MakePosition(37.659, 55.90)},  // box, Third Ring
      {MakeIdPosition(1, 37.592, 55.737), MakeIdPosition(2, 37.592, 55.737),
       MakeIdPosition(3, 37.503, 55.745), MakeIdPosition(4, 37.603, 55.745),
       MakeIdPosition(5, 37.603, 55.745)},  // points
      {MakeCluster(37.592, 55.737, {1, 2}),
       MakeCluster(37.603, 55.745, {4, 5})}  // expected
  };
  TestFindClusters(tc);
}

// Keep only clusters with density greater than threshold min_points_in_cluster
UTEST(FindClusters, DensityThreshold) {
  ClusterTestCase tc{
      {MakePosition(37.556, 55.721),
       MakePosition(37.659, 55.90)},  // box, Third Ring
      {MakeIdPosition(1, 37.592, 55.737), MakeIdPosition(2, 37.592, 55.737),
       MakeIdPosition(3, 37.603, 55.745), MakeIdPosition(4, 37.603, 55.745),
       MakeIdPosition(5, 37.603, 55.745)},       // points
      {MakeCluster(37.603, 55.745, {3, 4, 5})},  // expected
      R"({
      "min_intercluster_distance": 30,
      "min_points_in_cluster": 3,
      "bucket_side_length": 1000
    })"                                          // clustering
  };
  TestFindClusters(tc);
}

// Test for correctness in case when bucket side length is greater than bounding
// box
UTEST(FindClusters, GiantBucket) {
  ClusterTestCase tc{
      {MakePosition(37.556, 55.721),
       MakePosition(37.659, 55.90)},  // box, Third Ring
      {MakeIdPosition(1, 37.592, 55.737), MakeIdPosition(2, 37.592, 55.737),
       MakeIdPosition(3, 37.563, 55.745), MakeIdPosition(4, 37.603, 55.745),
       MakeIdPosition(5, 37.603, 55.745)},  // points
      {MakeCluster(37.592, 55.737, {1, 2}), MakeCluster(37.563, 55.745, {3}),
       MakeCluster(37.603, 55.745, {4, 5})},  // expected
      R"({
      "min_intercluster_distance": 30,
      "min_points_in_cluster": 1,
      "bucket_side_length": 100000
    })"                                       // clustering
  };
  TestFindClusters(tc);
}

// Test for correctness in case when bucket side length is 1 meter. Box is split
// roughly in 1'000'000 buckets
UTEST(FindClusters, TinyBucket) {
  ClusterTestCase tc{
      {MakePosition(37.591, 55.736), MakePosition(37.604, 55.746)},  // box
      {MakeIdPosition(1, 37.592, 55.737), MakeIdPosition(2, 37.592, 55.737),
       MakeIdPosition(3, 37.597, 55.740), MakeIdPosition(4, 37.603, 55.745),
       MakeIdPosition(5, 37.603, 55.745)},  // points
      {MakeCluster(37.592, 55.737, {1, 2}), MakeCluster(37.597, 55.740, {3}),
       MakeCluster(37.603, 55.745, {4, 5})},  // expected
      R"({
      "min_intercluster_distance": 10,
      "min_points_in_cluster": 1,
      "bucket_side_length": 1
    })"                                       // clustering
  };
  TestFindClusters(tc);
}

UTEST(FindClusters, RealData) {
  ClusterTestCase tc{
      {MakePosition(37.5971, 55.7355), MakePosition(37.6114, 55.7420)},  // box
      {MakeIdPosition(1, 37.6019, 55.7379), MakeIdPosition(2, 37.6040, 55.7381),
       MakeIdPosition(3, 37.6053, 55.7388), MakeIdPosition(4, 37.6035, 55.7388),
       MakeIdPosition(5, 37.6012, 55.7399), MakeIdPosition(6, 37.6025, 55.7407),
       MakeIdPosition(7, 37.5971, 55.7397)},  // points
      {MakeCluster(37.6037, 55.7384, {1, 2, 3, 4}),
       MakeCluster(37.6018, 55.7403, {5, 6}),
       MakeCluster(37.5971, 55.7397, {7})},  // expected
      R"({
      "min_intercluster_distance": 170,
      "min_points_in_cluster": 1,
      "bucket_side_length": 300
    })"                                      // clustering
  };
  TestFindClusters(tc);
}

UTEST(FindClusters, RealDataCornerCases) {
  const std::string clustering = R"(
      "min_intercluster_distance": 170,
      "min_points_in_cluster": 1,
      "bucket_side_length": {0})";
  ClusterTestCase tc{
      {MakePosition(37.5971, 55.7355), MakePosition(37.6114, 55.7420)},  // box
      {MakeIdPosition(1, 37.6019, 55.7379), MakeIdPosition(2, 37.6040, 55.7381),
       MakeIdPosition(3, 37.6053, 55.7388), MakeIdPosition(4, 37.6035, 55.7388),
       MakeIdPosition(5, 37.6012, 55.7399), MakeIdPosition(6, 37.6025, 55.7407),
       MakeIdPosition(7, 37.5971, 55.7397)},  // points
      {MakeCluster(37.6037, 55.7384, {1, 2, 3, 4}),
       MakeCluster(37.6018, 55.7403, {5, 6}),
       MakeCluster(37.5971, 55.7397, {7})}  // expected
  };

  std::vector<int> bucket_sides{
      // 170,   // bucket side length is equal to min_intercluster_distance
      // 1000,  // all points in one bucket
      50  // each point in separate bucket
  };
  for (const auto side : bucket_sides) {
    tc.clustering = "{" + fmt::format(clustering, side) + "}";
    TestFindClusters(tc);
  }
}

// Clustering result does not depend on initial order of points
UTEST(FindClusters, OrderIndependent) {
  ClusterTestCase tc{
      {MakePosition(37.5971, 55.7355), MakePosition(37.6114, 55.7420)},  // box
      {MakeIdPosition(1, 37.6019, 55.7379), MakeIdPosition(2, 37.6040, 55.7381),
       MakeIdPosition(3, 37.6053, 55.7388), MakeIdPosition(4, 37.6035, 55.7388),
       MakeIdPosition(5, 37.6012, 55.7399), MakeIdPosition(6, 37.6025, 55.7407),
       MakeIdPosition(7, 37.5971, 55.7397)},  // points
      {MakeCluster(37.6019, 55.7379, {1}),
       MakeCluster(37.6037, 55.7384, {2, 3, 4}),
       MakeCluster(37.6018, 55.7403, {5, 6}),
       MakeCluster(37.5971, 55.7397, {7})},  // expected
      R"({
      "min_intercluster_distance": 160,
      "min_points_in_cluster": 1,
      "bucket_side_length": 300
    })"                                      // clustering
  };

  for (size_t count = 0; count < 100; ++count) {
    std::next_permutation(
        tc.points.begin(), tc.points.end(),
        [](const auto& lhs, const auto& rhs) { return lhs.id < rhs.id; });
    TestFindClusters(tc);
  }
}

}  // namespace eats_catalog::algo
