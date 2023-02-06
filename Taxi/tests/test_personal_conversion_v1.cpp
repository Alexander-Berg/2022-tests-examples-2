#include <gtest/gtest.h>

#include <ml/common/filesystem.hpp>
#include <ml/personal_conversion/v1/features_extractor.hpp>
#include <ml/personal_conversion/v1/objects.hpp>
#include <ml/personal_conversion/v1/resource.hpp>

#include "common/utils.hpp"

namespace {
using namespace ml::personal_conversion::v1;
const std::string kTestDataDir =
    tests::common::GetTestResourcePath("personal_conversion_v1");
}  // namespace

TEST(PersonalConversionV1, objects) {
  auto original_json_request =
      ml::common::ReadFileContents(kTestDataDir + "/request.json");
  auto original_request =
      ml::common::FromJsonString<Request>(original_json_request);

  ASSERT_EQ(original_request.tariff_zone, "samara");
  ASSERT_EQ(original_request.history_features["total_orders_this_monthday"], 9);
  ASSERT_EQ(original_request.history_features["mean_orders_this_monthday"],
            0.12);
  ASSERT_EQ(original_request.route_distance, 1223.2);
  ASSERT_EQ(original_request.point_a.lon, 55.77557290200576);
  ASSERT_NE(original_request.classes_info.find("econom"),
            original_request.classes_info.end());
  ASSERT_NE(original_request.classes_info.find("vip"),
            original_request.classes_info.end());
  ASSERT_NE(original_request.classes_info.find("comfort"),
            original_request.classes_info.end());
  ASSERT_EQ(original_request.classes_info.find("uberx"),
            original_request.classes_info.end());
  ASSERT_EQ(original_request.classes_info["econom"].surge_value, 1.1);
  ASSERT_EQ(original_request.classes_info["vip"].cost, 1000);

  auto serialized_json_request = ml::common::ToJsonString(original_request);
  auto deserialized_request =
      ml::common::FromJsonString<Request>(serialized_json_request);
  ASSERT_EQ(deserialized_request, original_request);
}

TEST(PersonalConversionV1, features_extractor) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto config = ml::common::FromJsonString<PredictorConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  const auto features_config = config.features_config;
  ASSERT_EQ(features_config.geo_combinations_count, 3);
  ASSERT_EQ(features_config.time_shifts_count, 2);
  const auto features_extractor = FeaturesExtractor(features_config);
  const auto features = features_extractor.Apply(request);
  auto categorical = features.categorical;
  auto numerical = features.numerical;
  ASSERT_EQ(categorical.size(), 3u);
  for (size_t i = 0; i < categorical.size(); ++i) {
    ASSERT_EQ(categorical[i].size(), 3u);
    ASSERT_EQ(categorical[i].at(0), "samara");  // tariff_zone
    ASSERT_EQ(categorical[i].at(1), "cash");    // payment_method
    ASSERT_EQ(categorical[i].at(2),
              features.tariff_class_order[i]);  // tariff_class

    ASSERT_EQ(numerical[i].size(), 28u);
    ASSERT_EQ(numerical[i].at(9), 1223.2);  // distance_m
    ASSERT_EQ(numerical[i].at(10), 982.1);  // duration_sec
    ASSERT_EQ(numerical[i].at(11), 9);      // total_orders_this_monthday
    ASSERT_EQ(numerical[i].at(12), 0.12);   // mean_orders_this_monthday
    ASSERT_EQ(numerical[i].at(13), 13.1);  // mean_orders_this_monthday_by_users
  }
}

TEST(PersonalConversionV1, features_extractor_wo_some_features) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  const auto config =
      ml::common::FromJsonString<PredictorConfig>(ml::common::ReadFileContents(
          kTestDataDir + "/resource/config_wo_some_features.json"));
  const auto features_config = config.features_config;
  ASSERT_EQ(features_config.geo_combinations_count, 3);
  ASSERT_EQ(features_config.time_shifts_count, 2);
  const auto features_extractor = FeaturesExtractor(features_config);
  const auto features = features_extractor.Apply(request);
  auto categorical = features.categorical;
  auto numerical = features.numerical;
  ASSERT_EQ(categorical.size(), 3u);
  for (size_t i = 0; i < categorical.size(); ++i) {
    ASSERT_EQ(categorical[i].size(), 1u);

    ASSERT_EQ(numerical[i].size(), 15u);
    ASSERT_EQ(numerical[i].at(12), 0);    // total_orders_this_weekday
    ASSERT_EQ(numerical[i].at(13), 0);    // mean_orders_this_weekday
    ASSERT_EQ(numerical[i].at(14), 1e9);  // mean_pin_conversion_time
  }
}

TEST(PersonalConversionV1, resource) {
  auto request = ml::common::FromJsonString<Request>(
      ml::common::ReadFileContents(kTestDataDir + "/request.json"));
  Params params;
  Resource resource(kTestDataDir + "/resource", true);
  const auto response = resource.GetPredictor()->Apply(request, params);
  ASSERT_EQ(response.predictions.size(), 3u);
  for (size_t i = 0; i < response.predictions.size(); ++i) {
    ASSERT_EQ(response.predictions[i].prediction_raw, 0.5);
  }

  const auto config = ml::common::FromJsonString<PredictorConfig>(
      ml::common::ReadFileContents(kTestDataDir + "/resource/config.json"));
  const auto features_extractor = FeaturesExtractor(config.features_config);
  const auto features = features_extractor.Apply(request);
  for (size_t i = 0; i < response.predictions.size(); ++i) {
    ASSERT_EQ(response.predictions[i].tariff_class,
              features.tariff_class_order[i]);
  }
}
