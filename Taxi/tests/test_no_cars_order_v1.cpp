#include <gtest/gtest.h>

#include <sstream>

#include <ml/common/filesystem.hpp>
#include <ml/common/math_utils.hpp>
#include <ml/no_cars_order/v1/features_extractor.hpp>
#include <ml/no_cars_order/v1/objects.hpp>
#include <ml/no_cars_order/v1/predictor.hpp>
#include <ml/no_cars_order/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::no_cars_order::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("no_cars_order_v1");
}  // namespace

TEST(NoCarsOrderV1, parse_request) {
  auto request = ml::common::FromJsonString<ml::no_cars_order::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  ml::common::ToJsonString<ml::no_cars_order::v1::Request>(request);
}

TEST(NoCarsOrderV1, parse_response) {
  auto response = ml::common::FromJsonString<ml::no_cars_order::v1::Response>(
      ml::common::ReadFileContents(kTestDataDir + "/response.json"));
  ml::common::ToJsonString<ml::no_cars_order::v1::Response>(response);
}

TEST(NoCarsOrderV1, features_extractor) {
  auto request = ml::common::FromJsonString<ml::no_cars_order::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  FeaturesConfig features_config = ml::common::FromJsonString<FeaturesConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  ASSERT_EQ(features_config.time_shifts_count, 3);
  ASSERT_EQ(features_config.geo_combinations_count, 5);
  ASSERT_EQ(features_config.tariff_class_list.size(), 3ul);
  ASSERT_EQ(features_config.add_non_common_features, true);
  ASSERT_EQ(features_config.add_surge_info_features, true);
  const auto features_extractor =
      ml::no_cars_order::v1::FeaturesExtractor(features_config);
  const auto features = features_extractor.Apply(request);
  ASSERT_EQ(features.numerical[0].size(), 820ul);
  FeaturesConfig features_config_extended =
      ml::common::FromJsonString<FeaturesConfig>(ml::common::ReadFileContents(
          kTestDataDir + "/resource/config_extended.json"));
  ASSERT_EQ(features_config_extended.add_non_common_features, true);
  ASSERT_EQ(features_config_extended.add_all_tariffs_features, true);
  ASSERT_EQ(features_config_extended.add_surge_info_features, false);
  ASSERT_EQ(features_config_extended.add_chain_info_features, false);
  ASSERT_EQ(features_config_extended.add_surge_found_share, false);
  const auto features_extractor_extended =
      ml::no_cars_order::v1::FeaturesExtractor(features_config_extended);
  const auto features_extended = features_extractor_extended.Apply(request);
  ASSERT_EQ(features_extended.numerical[0].size(), 330ul);
  ASSERT_EQ(features_extended.categorical[0].size(), 5ul);
  FeaturesConfig features_config_chain_info =
      ml::common::FromJsonString<FeaturesConfig>(ml::common::ReadFileContents(
          kTestDataDir + "/resource/config_chain_info.json"));
  ASSERT_EQ(features_config_chain_info.add_chain_info_features, false);
  ASSERT_EQ(features_config_chain_info.add_scoring_features, true);
  ASSERT_EQ(features_config_chain_info.add_surge_found_share, true);
  const auto features_extractor_chain_info =
      ml::no_cars_order::v1::FeaturesExtractor(features_config_chain_info);
  const auto features_chain_info = features_extractor_chain_info.Apply(request);
  ASSERT_EQ(features_chain_info.numerical[0].size(), 1198ul);
  auto request_cut = ml::common::FromJsonString<ml::no_cars_order::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request_cut.json"));
  const auto features_cut = features_extractor_chain_info.Apply(request_cut);
  ASSERT_EQ(features_cut.numerical.size(), 0ul);
}

TEST(NoCarsOrderV1, features_extractor_not_use_radius) {
  auto request = ml::common::FromJsonString<ml::no_cars_order::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  FeaturesConfig features_config =
      ml::common::FromJsonString<FeaturesConfig>(ml::common::ReadFileContents(
          kTestDataDir + "/resource/config_not_use_radius.json"));
  const auto features_extractor =
      ml::no_cars_order::v1::FeaturesExtractor(features_config);
  const auto features = features_extractor.Apply(request);
  ASSERT_EQ(features.numerical[0].size(), 190ul);
  ASSERT_EQ(features.categorical[0].size(), 5ul);
}

TEST(NoCarsOrderV1, predictor) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  FeaturesConfig features_config = ml::common::FromJsonString<FeaturesConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  const auto features_extractor =
      std::make_shared<FeaturesExtractor>(features_config);
  std::shared_ptr<ml::common::CatboostModel> predictions_extractor;
  predictions_extractor = ml::common::CatboostModelMock::FromExpectedSizes(
      features_extractor->GetNumFeaturesSize(),
      features_extractor->GetCatFeaturesSize());
  const auto postprocessor =
      std::make_shared<ml::no_cars_order::v1::PostProcessor>();
  const auto predictor = std::make_shared<ml::no_cars_order::v1::Predictor>(
      features_extractor, predictions_extractor, postprocessor);
  const auto response = predictor->Apply(request, params);
  ASSERT_EQ(request.classes_info.size(), response.response_items.size());
}

TEST(NoCarsOrderV1, resource) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  Resource resource(kTestDataDir + "/resource", true);
  const auto response = resource.GetPredictor()->Apply(request, params);
  for (const auto& items : response.response_items) {
    ASSERT_EQ(items.raw_value, ml::common::Sigmoid(0.0));
  }
}
