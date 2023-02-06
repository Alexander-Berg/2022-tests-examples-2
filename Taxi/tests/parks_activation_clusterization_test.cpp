#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <config/config.hpp>

#include <api_over_data/revise_helpers.hpp>
#include <models/park_activation.hpp>

namespace {
const std::string kConsumer = "test_consumer";
const std::string kConsumerSpecialization = "test_specialization";
const std::string kParksActivationClusterizarion =
    "parks_activation_clusterization";
const std::string kThreshold = "threshold";
const std::string kOldWayOnDefault = "old_way_on_default";
const std::string kLogHint = "log_hint";

generated::parks_activation::api::ParkObject GetParkObject(
    const std::string& park_id) {
  generated::parks_activation::api::ParkData park_data{
      false, boost::none, true, true, true, true, true};
  generated::parks_activation::api::ParkObject park_object{
      1, "1970-01-15T06:56:07.000", park_id, "city", park_data};

  return park_object;
}

config::DocsMap DocsMapForTest(double threshold, bool old_way_on_default) {
  config::DocsMap docs_map = config::DocsMapForTest();
  mongo::BSONObjBuilder threshold_settings;
  threshold_settings.append(kThreshold, threshold);
  threshold_settings.append(kOldWayOnDefault, old_way_on_default);
  mongo::BSONObjBuilder external_settings;
  external_settings.append(kParksActivationClusterizarion,
                           threshold_settings.obj());
  mongo::BSONObjBuilder test_specialization;
  test_specialization.append(kConsumerSpecialization, external_settings.obj());
  mongo::BSONObjBuilder test_consumer;
  test_consumer.append(kConsumer, test_specialization.obj());
  docs_map.Override("API_OVER_DATA_WORK_MODE_EXTERNAL_CRITERION",
                    test_consumer.obj());
  return docs_map;
}

}  // namespace

TEST(ClusterParksActivation, TestConfig) {
  auto docs_map = DocsMapForTest(100, false);
  config::Config config(docs_map);
  const auto& api_over_data_config =
      api_over_data::caches::GetApiOverDataConfig(config);
  auto parks_activation_clusterization =
      api_over_data_config.extra_criterion_settings.Get(kConsumer)
          .Get(kConsumerSpecialization)
          .parks_activation_clusterization;
  ASSERT_TRUE(bool(parks_activation_clusterization));
  ASSERT_EQ(parks_activation_clusterization->old_way_on_default, false);
  ASSERT_EQ(parks_activation_clusterization->threshold, 100);
}

TEST(ClusterParksActivation, TestSaveWorkMode) {
  auto docs_map = DocsMapForTest(40, false);
  config::Config config(docs_map);
  {
    auto park_activation = std::make_shared<parks_activation::models::Park>();
    park_activation->clusterization_value = 39.9;
    parks_activation::models::ClusterParksActivation reduce{
        config, kConsumer, kConsumerSpecialization, park_activation};

    api_over_data::work_mode::Type result = api_over_data::work_mode::kOldWay;
    auto reduce_wrapper = [&result, &reduce]() {
      result = reduce(api_over_data::work_mode::Type::kNewWay);
    };

    ASSERT_NO_THROW(reduce_wrapper());
    EXPECT_EQ(api_over_data::work_mode::Type::kNewWay, result);
  }
  {
    std::shared_ptr<parks_activation::models::Park> park_activation{};
    parks_activation::models::ClusterParksActivation reduce{
        config, kConsumer, kConsumerSpecialization, park_activation};

    api_over_data::work_mode::Type result = api_over_data::work_mode::kOldWay;
    auto reduce_wrapper = [&result, &reduce]() {
      result = reduce(api_over_data::work_mode::Type::kNewWay);
    };

    ASSERT_NO_THROW(reduce_wrapper());
    EXPECT_EQ(api_over_data::work_mode::Type::kNewWay, result);
  }
}

TEST(ClusterParksActivation, TestChangeWorkMode) {
  auto docs_map = DocsMapForTest(40.0, true);
  config::Config config(docs_map);
  {
    auto park_activation = std::make_shared<parks_activation::models::Park>();
    park_activation->clusterization_value = 40.1;
    parks_activation::models::ClusterParksActivation reduce{
        config, kConsumer, kConsumerSpecialization, park_activation};

    api_over_data::work_mode::Type result = api_over_data::work_mode::kNewWay;
    auto reduce_wrapper = [&result, &reduce]() {
      result = reduce(api_over_data::work_mode::Type::kNewWay);
    };

    ASSERT_NO_THROW(reduce_wrapper());
    EXPECT_EQ(api_over_data::work_mode::Type::kOldWay, result);
  }
  {
    std::shared_ptr<parks_activation::models::Park> park_activation{};
    parks_activation::models::ClusterParksActivation reduce{
        config, kConsumer, kConsumerSpecialization, park_activation};

    api_over_data::work_mode::Type result = api_over_data::work_mode::kOldWay;
    auto reduce_wrapper = [&result, &reduce]() {
      result = reduce(api_over_data::work_mode::Type::kNewWay);
    };

    ASSERT_NO_THROW(reduce_wrapper());
    EXPECT_EQ(api_over_data::work_mode::Type::kOldWay, result);
  }
}

TEST(ClusterParksActivation, TestValueGenerationWithPython) {
  std::map<std::string, double> park_id_clusterization{
      {"400001131210", 20.5699},
      {"400000127852", 99.1909},
      {"400302122323", 15.2011},
      {"400000127632", 82.9417}};
  for (const auto& [park_id, clusterization] : park_id_clusterization) {
    generated::parks_activation::api::ParkObject park_object;
    parks_activation::models::Park park_activation{GetParkObject(park_id)};
    EXPECT_FLOAT_EQ(clusterization, park_activation.clusterization_value);
  }
}
