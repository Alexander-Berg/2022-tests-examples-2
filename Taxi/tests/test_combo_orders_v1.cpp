#include <gtest/gtest.h>

#include <iostream>
#include <sstream>

#include <ml/combo_orders/v1/features_extractor.hpp>
#include <ml/combo_orders/v1/history_features_storage.hpp>
#include <ml/combo_orders/v1/objects.hpp>
#include <ml/combo_orders/v1/predictor.hpp>
#include <ml/combo_orders/v1/resource.hpp>
#include <ml/common/filesystem.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::combo_orders::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("combo_orders");
}  // namespace

TEST(ComboOrdersV1, features_extractor) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto predictor_config = ml::common::FromJsonString<PredictorConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  const auto features_config = predictor_config.features_config;
  ASSERT_EQ(features_config.time_shifts_count, 3);
  ASSERT_EQ(features_config.geo_combinations_count, 5);
  HistoryFeaturesStorage storage;
  const auto features_extractor = FeaturesExtractor(
      features_config, std::make_shared<HistoryFeaturesStorage>(storage));
  const auto features = features_extractor.Apply(request);
}

TEST(ComboOrdersV1, features_extractor_w_history_features) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto predictor_config = ml::common::FromJsonString<PredictorConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  const auto features_config = predictor_config.features_config;
  auto history_features_storage = CreateHistoryFeaturesStorage(
      kTestDataDir + "/resource/history_features_storage.json", true);
  const auto features_extractor =
      FeaturesExtractor(features_config, history_features_storage);
  const auto features = features_extractor.Apply(request);
  ASSERT_EQ(features.categorical.size(), 3ul);
  ASSERT_EQ(features.categorical[0], "ufa");
  ASSERT_EQ(features.categorical[1], "v1xwm4");
  ASSERT_EQ(features.categorical[2], "v1xz3k");
  ASSERT_EQ(features.numerical.size(), 30ul);
  double kAbsentFeature = 1e9;
  int non_default_features_num = 0;
  for (double value : features.numerical) {
    if (value != kAbsentFeature) non_default_features_num++;
  }
  ASSERT_EQ(non_default_features_num, 23);
}

TEST(ComboOrdersV1, resource) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  Resource resource(kTestDataDir + "/resource", true);
  const auto response = resource.GetPredictor()->Apply(request, params);
  ASSERT_EQ(response.prediction_raw, 0.5);
}
