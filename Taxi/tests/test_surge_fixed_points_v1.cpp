#include <gtest/gtest.h>

#include <sstream>

#include <ml/common/filesystem.hpp>
#include <ml/surge_statistics/surge_fixed_points/v1/features_extractor.hpp>
#include <ml/surge_statistics/surge_fixed_points/v1/objects.hpp>
#include <ml/surge_statistics/surge_fixed_points/v1/predictor.hpp>
#include <ml/surge_statistics/surge_fixed_points/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::surge_statistics::surge_fixed_points::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("surge_fixed_points_v1");
}  // namespace

TEST(SurgeFixedPointsV1, request_parser) {
  auto request = ml::common::FromJsonString<
      ml::surge_statistics::surge_fixed_points::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto features_config = ml::common::FromJsonString<
      ml::surge_statistics::surge_fixed_points::v1::FeaturesConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  ASSERT_EQ(features_config.geo_combinations_count, 5);
  ASSERT_EQ(features_config.add_ps_shift_features, true);
  ASSERT_EQ(features_config.add_absolute_features, true);
  ASSERT_EQ(features_config.add_non_common_features, true);
  ASSERT_EQ(features_config.add_relative_features, true);
  ASSERT_EQ(features_config.max_depth_relation, 2);
  ASSERT_EQ(features_config.max_time_size_relation, 5);
  const auto features_extractor =
      ml::surge_statistics::surge_fixed_points::v1::FeaturesExtractor(
          features_config);
  const auto features = features_extractor.Apply(request);
  const auto features_config_extended = ml::common::FromJsonString<
      ml::surge_statistics::surge_fixed_points::v1::FeaturesConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/config_extended.json"));
  const auto features_extractor_extended =
      ml::surge_statistics::surge_fixed_points::v1::FeaturesExtractor(
          features_config_extended);
  const auto features_extended = features_extractor_extended.Apply(request);
  ASSERT_EQ(features_extended.categorical[0].size(), 3ul);
}

TEST(SurgeFixedPointsV1, resource) {
  auto request = ml::common::FromJsonString<
      ml::surge_statistics::surge_fixed_points::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  Resource resource(kTestDataDir + "/resource", true);
  const auto response = resource.GetPredictor()->Apply(request, params);
}

TEST(SurgeFixedPointsV1, apply_predictor_bulk) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Resource resource(kTestDataDir + "/resource", true);
  std::vector<Request> requests{request, request, request};
  const auto responses = resource.GetPredictor()->ApplyBulk(requests, {});
  ASSERT_FLOAT_EQ(responses.size(), 3ul);
}
