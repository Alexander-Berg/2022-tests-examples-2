#include <gtest/gtest.h>

#include <sstream>

#include <ml/common/filesystem.hpp>
#include <ml/logistics_performer_availability/v1/features_extractor.hpp>
#include <ml/logistics_performer_availability/v1/objects.hpp>
#include <ml/logistics_performer_availability/v1/predictor.hpp>
#include <ml/logistics_performer_availability/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::logistics_performer_availability::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("logistics_performer_availability_v1");
}  // namespace

TEST(LogisticsV1, features_extractor_backward_compatibility) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto features_config =
      ml::common::FromJsonString<FeaturesConfig>(ml::common::ReadFileContents(
          kTestDataDir + "/resource/config_wo_candidates.json"));
  ASSERT_EQ(features_config.add_candidates_features, false);
  ASSERT_EQ(features_config.router_types_list.size(), 0ul);
  const auto features_extractor = FeaturesExtractor(features_config);
  const auto features = features_extractor.Apply(request);
}

TEST(LogisticsV1, features_extractor) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto features_config = ml::common::FromJsonString<FeaturesConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  ASSERT_EQ(features_config.time_shifts_count, 3);
  ASSERT_EQ(features_config.geo_combinations_count, 6);
  ASSERT_EQ(features_config.router_types_list.size(), 3ul);
  const auto features_extractor = FeaturesExtractor(features_config);
  const auto features = features_extractor.Apply(request);
}

TEST(LogisticsV1, custom_features) {
  auto request =
      ml::common::FromJsonString<Request>(ml::common::ReadFileContents(
          kTestDataDir + "/request_w_custom_features.json"));
  const auto features_config =
      ml::common::FromJsonString<FeaturesConfig>(ml::common::ReadFileContents(
          kTestDataDir + "/resource/config_w_custom_features.json"));
  const auto features_extractor = FeaturesExtractor(features_config);
  const auto features = features_extractor.Apply(request);
}

TEST(LogisticsV1, resource) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  Resource resource(kTestDataDir + "/resource", true);
  const auto response = resource.GetPredictor()->Apply(request, params);
  ASSERT_EQ(response.response_items.size(), 2ul);
  ASSERT_EQ(request.tariff_classes.size(), response.response_items.size());
  for (size_t i = 0; i < request.tariff_classes.size(); ++i) {
    const auto& response_item = response.response_items.at(i);
    ASSERT_EQ(response_item.tariff_class, request.tariff_classes.at(i));
  }
}
