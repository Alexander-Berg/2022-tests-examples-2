#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/offer_statistics/v1/features_extractor.hpp>
#include <ml/offer_statistics/v1/objects.hpp>
#include <ml/offer_statistics/v1/predictor.hpp>
#include <ml/offer_statistics/v1/resource.hpp>
#include <ml/offer_statistics/v1/score_extractor.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::offer_statistics::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("offer_statistics_v1");
}  // namespace

TEST(OfferStatisticsV1, parse_request) {
  auto request = ml::common::FromJsonString<ml::offer_statistics::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));

  ASSERT_EQ(request.timestamp, ml::common::Double2TimePoint(1623842873.0));
  ASSERT_EQ(request.tariff_zone, "moscow");

  ASSERT_EQ(request.offer_points.size(), 2ul);
  ASSERT_FLOAT_EQ(request.offer_points.front().lon, 55.742901);
  ASSERT_FLOAT_EQ(request.offer_points.front().lat, 37.527636);
  ASSERT_FLOAT_EQ(request.offer_points.back().lon, 55.750275);
  ASSERT_FLOAT_EQ(request.offer_points.back().lat, 37.534223);

  ASSERT_FLOAT_EQ(request.route_distance, 5300);
  ASSERT_FLOAT_EQ(request.route_duration, 600);

  ml::common::ToJsonString<Request>(request);
}

TEST(OfferStatisticsV1, serialize_response) {
  auto response =
      ml::common::FromJsonString<ml::offer_statistics::v1::Response>(
          ml::common::ReadFileContents(kTestDataDir + "/response.json"));
  ml::common::ToJsonString<ml::offer_statistics::v1::Response>(response);
}

TEST(OfferStatisticsV1, features_extractor) {
  auto request = ml::common::FromJsonString<ml::offer_statistics::v1::Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  PredictorConfig config = ml::common::FromJsonString<PredictorConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  ASSERT_EQ(config.features_config.time_shifts_count, 3);
  ASSERT_EQ(config.features_config.geo_combinations_count, 5);
  ASSERT_EQ(config.features_config.use_tariff_zone, false);
  ASSERT_EQ(config.features_config.use_log_diff, true);

  const auto features_extractor =
      ml::offer_statistics::v1::FeaturesExtractor(config.features_config);
  const auto features = features_extractor.Apply(request);
  const auto& categorical = features.categorical;
  const auto& numerical = features.numerical;

  size_t categorical_size = features_extractor.GetCatFeaturesSize();
  size_t numerical_size = features_extractor.GetNumFeaturesSize();
  ASSERT_EQ(categorical_size, 0ul);
  ASSERT_EQ(numerical_size, 25ul);

  ASSERT_EQ(numerical.size(), numerical_size);
  ASSERT_EQ(categorical.size(), categorical_size);
}

TEST(OfferStatisticsV1, predictor) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  PredictorConfig config = ml::common::FromJsonString<PredictorConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  Mapping mapping = ml::common::FromJsonString<Mapping>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/mapping.json"));
  const auto features_extractor =
      std::make_shared<FeaturesExtractor>(config.features_config);
  std::shared_ptr<ml::common::CatboostModel> predictions_extractor;
  predictions_extractor = ml::common::CatboostModelMock::FromExpectedSizes(
      features_extractor->GetNumFeaturesSize(),
      features_extractor->GetCatFeaturesSize());
  auto score_extractors =
      std::unordered_map<std::string, std::shared_ptr<IScoreExtractor>>();
  score_extractors["prediction"] = std::make_shared<CatBoostScoreExtractor>(
      features_extractor, predictions_extractor);
  const auto post_processor = std::make_shared<MappingPostProcessor>(mapping);
  const auto predictor =
      std::make_shared<Predictor>(score_extractors, post_processor);
  const auto response = predictor->Apply(request);
  ASSERT_EQ(response.value, 1);
}

TEST(OfferStatisticsV1, resource) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Resource resource(kTestDataDir + "/resource", true);
  const auto response = resource.GetPredictor()->Apply(request);
  ASSERT_EQ(response.value, 1);
}

TEST(OfferStatisticsV1, resource_without_mapping) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Resource resource(kTestDataDir + "/resource_without_mapping", true);
  const auto response = resource.GetPredictor()->Apply(request);
  ASSERT_EQ(response.value, 0);
}
