#include <gtest/gtest.h>

#include <sstream>

#include <ml/common/filesystem.hpp>
#include <ml/surge_statistics/v1/features_extractor.hpp>
#include <ml/surge_statistics/v1/objects.hpp>
#include <ml/surge_statistics/v1/predictor.hpp>
#include <ml/surge_statistics/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::surge_statistics::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("surge_statistics_v1");
}  // namespace

TEST(SurgeStatisticsV1, parse_request) {
  auto request = ml::common::FromJsonString<ml::surge_statistics::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));

  const auto& by_category = request.by_category;
  ASSERT_FLOAT_EQ(*request.distance, 219.45032811164856);
  ASSERT_FLOAT_EQ(request.point_a.lat, 56.865073541732436);
  ASSERT_FLOAT_EQ(request.point_a.lon, 60.649541616439826);
  ASSERT_FLOAT_EQ(request.point_b->lat, 56.802805124543575);
  ASSERT_FLOAT_EQ(request.point_b->lon, 60.63423156738282);
  ASSERT_EQ(*request.payment_type, "cash");
  ASSERT_EQ(by_category.at("econom").pins, 38);
  ASSERT_EQ(by_category.at("econom").category, "econom");
  ASSERT_FLOAT_EQ(*by_category.at("business").prev_eta, 252.48197438767522);
  ASSERT_FLOAT_EQ(by_category.at("econom").reposition->total, 0);

  ml::common::ToJsonString<Request>(request);
}

TEST(SurgeStatisticsV1, serialize_response) {
  auto response =
      ml::common::FromJsonString<ml::surge_statistics::v1::Response>(
          ml::common::ReadFileContents(kTestDataDir + "/response.json"));
  ml::common::ToJsonString<ml::surge_statistics::v1::Response>(response);
}

TEST(SurgeStatisticsV1, backward_compatibility) {
  auto request = ml::common::FromJsonString<ml::surge_statistics::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  FeaturesConfig features_config = ml::common::FromJsonString<FeaturesConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/old_config.json"));
  ASSERT_EQ(features_config.time_shifts_count, 3);
  ASSERT_EQ(features_config.geo_combinations_count, 5);
  ASSERT_EQ(features_config.add_absolute_features, true);
  ASSERT_EQ(features_config.add_relative_features, true);
  ASSERT_EQ(features_config.add_non_common_features, true);
  ASSERT_EQ(features_config.add_absolute_diffs_features, true);
  ASSERT_EQ(features_config.add_absolute_diffs_features, true);
  ASSERT_EQ(features_config.add_surge_counters, true);
  ASSERT_EQ(features_config.add_value_smooth_a, false);
  ASSERT_EQ(features_config.add_value_smooth_b, false);
  ASSERT_EQ(features_config.add_point_b, false);
  const auto features_extractor =
      ml::surge_statistics::v1::FeaturesExtractor(features_config);
  size_t categorical_size = features_extractor.GetCatFeaturesSize();
  size_t numerical_size = features_extractor.GetNumFeaturesSize();
  ASSERT_EQ(categorical_size, 2ul);
  ASSERT_EQ(numerical_size, 446ul);
}

TEST(SurgeStatisticsV1, features_extractor) {
  auto request = ml::common::FromJsonString<ml::surge_statistics::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  FeaturesConfig features_config = ml::common::FromJsonString<FeaturesConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  ASSERT_EQ(features_config.time_shifts_count, 3);
  ASSERT_EQ(features_config.geo_combinations_count, 5);
  ASSERT_EQ(features_config.add_absolute_features, false);
  ASSERT_EQ(features_config.add_relative_features, true);
  ASSERT_EQ(features_config.add_non_common_features, false);
  ASSERT_EQ(features_config.add_absolute_diffs_features, true);
  ASSERT_EQ(features_config.add_surge_counters, true);
  ASSERT_EQ(features_config.add_value_smooth_a, false);
  ASSERT_EQ(features_config.add_value_smooth_b, false);
  ASSERT_EQ(features_config.add_point_b, false);
  ASSERT_EQ(features_config.category_list.size(), 2ul);
  const auto features_extractor =
      ml::surge_statistics::v1::FeaturesExtractor(features_config);
  const auto features = features_extractor.Apply(request);
  const auto& categorical = features.categorical;
  const auto& numerical = features.numerical;
  const auto& category_order = features.category_order;
  size_t rows_size = request.by_category.size();
  size_t categorical_size = features_extractor.GetCatFeaturesSize();
  size_t numerical_size = features_extractor.GetNumFeaturesSize();
  ASSERT_EQ(categorical_size, 2ul);
  ASSERT_EQ(numerical_size, 278ul);
  ASSERT_EQ(numerical.size(), rows_size);
  ASSERT_EQ(numerical[0].size(), numerical_size);
  ASSERT_EQ(category_order.size(), rows_size);
  ASSERT_EQ(request.by_category.size(), numerical.size());
  for (size_t i = 0; i < numerical.size(); i++) {
    const auto& categorical_row = categorical.at(i);
    ASSERT_EQ(categorical_row.at(1), category_order.at(i));
  }
}

TEST(SurgeStatisticsV1, value_smooth_features) {
  auto request = ml::common::FromJsonString<ml::surge_statistics::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  FeaturesConfig features_config =
      ml::common::FromJsonString<FeaturesConfig>(ml::common::ReadFileContents(
          kTestDataDir + "/resource/config_smooth_and_point_b.json"));
  ASSERT_EQ(features_config.time_shifts_count, 3);
  ASSERT_EQ(features_config.geo_combinations_count, 5);
  ASSERT_EQ(features_config.add_absolute_features, false);
  ASSERT_EQ(features_config.add_relative_features, true);
  ASSERT_EQ(features_config.add_non_common_features, false);
  ASSERT_EQ(features_config.add_absolute_diffs_features, true);
  ASSERT_EQ(features_config.add_surge_counters, true);
  ASSERT_EQ(features_config.add_value_smooth_a, true);
  ASSERT_EQ(features_config.add_value_smooth_b, true);
  ASSERT_EQ(features_config.add_point_b, true);
  ASSERT_EQ(features_config.category_list.size(), 2ul);
  const auto features_extractor =
      ml::surge_statistics::v1::FeaturesExtractor(features_config);
  const auto features = features_extractor.Apply(request);
  const auto& categorical = features.categorical;
  const auto& numerical = features.numerical;
  const auto& category_order = features.category_order;
  size_t rows_size = request.by_category.size();
  size_t categorical_size = features_extractor.GetCatFeaturesSize();
  size_t numerical_size = features_extractor.GetNumFeaturesSize();
  ASSERT_EQ(categorical_size, 2ul);
  ASSERT_EQ(numerical_size, 383ul);
  ASSERT_EQ(numerical.size(), rows_size);
  ASSERT_EQ(numerical[0].size(), numerical_size);
  ASSERT_EQ(category_order.size(), rows_size);
  ASSERT_EQ(request.by_category.size(), numerical.size());
  for (size_t i = 0; i < numerical.size(); i++) {
    const auto& categorical_row = categorical.at(i);
    ASSERT_EQ(categorical_row.at(1), category_order.at(i));
  }
}

TEST(SurgeStatisticsV1, no_surge_counters) {
  auto request = ml::common::FromJsonString<ml::surge_statistics::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  FeaturesConfig features_config =
      ml::common::FromJsonString<FeaturesConfig>(ml::common::ReadFileContents(
          kTestDataDir + "/resource/config_no_surge_counters.json"));
  ASSERT_EQ(features_config.time_shifts_count, 3);
  ASSERT_EQ(features_config.geo_combinations_count, 5);
  ASSERT_EQ(features_config.add_absolute_features, true);
  ASSERT_EQ(features_config.add_relative_features, true);
  ASSERT_EQ(features_config.add_common_features, true);
  ASSERT_EQ(features_config.add_non_common_features, false);
  ASSERT_EQ(features_config.add_absolute_diffs_features, true);
  ASSERT_EQ(features_config.add_surge_counters, false);
  ASSERT_EQ(features_config.add_value_smooth_a, true);
  ASSERT_EQ(features_config.add_value_smooth_b, false);
  ASSERT_EQ(features_config.add_point_b, true);
  ASSERT_EQ(features_config.category_list.size(), 2ul);
  const auto features_extractor =
      ml::surge_statistics::v1::FeaturesExtractor(features_config);
  const auto features = features_extractor.Apply(request);
  const auto& categorical = features.categorical;
  const auto& numerical = features.numerical;
  const auto& category_order = features.category_order;
  size_t rows_size = request.by_category.size();
  size_t categorical_size = features_extractor.GetCatFeaturesSize();
  size_t numerical_size = features_extractor.GetNumFeaturesSize();
  ASSERT_EQ(categorical_size, 2ul);
  ASSERT_EQ(numerical_size, 21ul);
  ASSERT_EQ(numerical.size(), rows_size);
  ASSERT_EQ(numerical[0].size(), numerical_size);
  ASSERT_EQ(category_order.size(), rows_size);
  ASSERT_EQ(request.by_category.size(), numerical.size());
  for (size_t i = 0; i < numerical.size(); i++) {
    const auto& categorical_row = categorical.at(i);
    ASSERT_EQ(categorical_row.at(1), category_order.at(i));
  }
}

TEST(SurgeStatisticsV1, predictor) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  FeaturesConfig features_config;
  const auto features_extractor =
      std::make_shared<FeaturesExtractor>(features_config);
  std::shared_ptr<ml::common::CatboostModel> predictions_extractor;
  predictions_extractor = ml::common::CatboostModelMock::FromExpectedSizes(
      features_extractor->GetNumFeaturesSize(),
      features_extractor->GetCatFeaturesSize());
  const auto postprocessor = std::make_shared<PostProcessor>();
  const auto predictor = std::make_shared<Predictor>(
      features_extractor, predictions_extractor, postprocessor);
  const auto response = predictor->Apply(request, params);
  ASSERT_FLOAT_EQ(request.by_category.size(), response.by_category.size());
  ASSERT_EQ(response.by_category.at("econom"), 0);
  ASSERT_EQ(response.by_category.at("business"), 0);
}

TEST(SurgeStatisticsV1, predictor_again) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  Resource resource(kTestDataDir + "/resource", true);
  const auto response = resource.GetPredictor()->Apply(request, params);
}
