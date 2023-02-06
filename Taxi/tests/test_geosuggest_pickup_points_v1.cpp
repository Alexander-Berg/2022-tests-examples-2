#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/geosuggest/pickup_points/v1/fallback.hpp>
#include <ml/geosuggest/pickup_points/v1/objects.hpp>
#include <ml/geosuggest/pickup_points/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::geosuggest;
using namespace ml::geosuggest::pickup_points::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("geosuggest_pickup_points_v1");
}  // namespace

TEST(PickupPointsV1, recommender) {
  const Resource resource{kTestDataDir + "/resource", true};
  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  params.max_size = 10;
  params.min_probability = 0;
  params.max_distance = 200;
  params.merge_distance = 0;
  const auto response = resource.GetRecommender()->Apply(request, params);
  ASSERT_EQ(response.points.size(), 2ul);
}

TEST(PickupPointsV1, fallback) {
  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  RecommenderFallback recommender;
  const auto response = recommender.Apply(request, {});
  ASSERT_EQ(response.points.size(), 0ul);
}

TEST(PickupPointsV1, points_storage) {
  const Resource resource{kTestDataDir + "/resource", true};
  const auto& storage = resource.GetPointsStorage();
  ASSERT_EQ(storage->points.size(), 2ul);
  const auto str = ml::common::ToCompressedJsonString<PointsStorage>(*storage);
  const auto new_storage =
      ml::common::FromCompressedJsonString<PointsStorage>(str);
  ASSERT_EQ(new_storage.points.size(), 2ul);
  ASSERT_EQ(new_storage.points[0].edge_category, 1);
  ASSERT_EQ(new_storage.points[0].segment_direction, 0.3);
  ASSERT_EQ(new_storage.points[1].edge_category, 0);
  ASSERT_EQ(new_storage.points[1].segment_direction, 0.);
}

TEST(PickupPointsV1, tags) {
  const Resource resource{kTestDataDir + "/resource", true};
  const auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  params.max_size = 10;
  params.min_probability = 0;
  params.max_distance = 200;
  params.merge_distance = 0;
  params.add_top_relevance_tag = true;
  const auto response = resource.GetRecommender()->Apply(request, params);
  ASSERT_EQ(response.points.at(0).tags.size(), 1ul);
  ASSERT_EQ(response.points.at(0).tags.at(0), "best");
}
