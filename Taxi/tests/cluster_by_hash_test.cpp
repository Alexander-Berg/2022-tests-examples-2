#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <config/config.hpp>

#include <api_over_data/revise_helpers.hpp>

namespace {
const std::string kConsumer = "test_consumer";
const std::string kConsumerSpecialization = "test_specialization";
const std::string kClustersByHash = "clusters_by_hash";
const std::string kLogHint = "log_hint";

config::DocsMap DocsMapForTest(double percentage) {
  config::DocsMap docs_map = config::DocsMapForTest();
  mongo::BSONObjBuilder external_settings;
  external_settings.append(kClustersByHash, percentage);
  mongo::BSONObjBuilder test_specialization;
  test_specialization.append(kConsumerSpecialization, external_settings.obj());
  mongo::BSONObjBuilder test_consumer;
  test_consumer.append(kConsumer, test_specialization.obj());
  docs_map.Override("API_OVER_DATA_WORK_MODE_EXTERNAL_CRITERION",
                    test_consumer.obj());
  return docs_map;
}

}  // namespace

TEST(ReduceWorkModeByModSha1, TestSaveWorkMode) {
  std::map<std::string, double> park_ids{
      {"400001131210", 8.9296},
      {"400000127852", 2.8165},
      {"400302122323", 79.9093},
      {"400000127632", 69.0172},
  };
  for (const auto& [park_id, value] : park_ids) {
    auto docs_map = DocsMapForTest(value + 0.0001);
    config::Config config(docs_map);
    api_over_data::ReduceWorkModeByModSha1 reduce{
        config, kConsumer, kConsumerSpecialization, park_id};

    api_over_data::work_mode::Type result = api_over_data::work_mode::kOldWay;
    auto reduce_wrapper = [&result, &reduce]() {
      result = reduce(api_over_data::work_mode::Type::kNewWay);
    };

    ASSERT_NO_THROW(reduce_wrapper());
    EXPECT_EQ(api_over_data::work_mode::Type::kNewWay, result);
  }
}

TEST(ReduceWorkModeByModSha1, TestChangeWorkMode) {
  std::map<std::string, double> park_ids{
      {"400001131210", 8.9296},
      {"400000127852", 2.8165},
      {"400302122323", 79.9093},
      {"400000127632", 69.0172},
  };
  for (const auto& [park_id, value] : park_ids) {
    auto docs_map = DocsMapForTest(value);
    config::Config config(docs_map);
    api_over_data::ReduceWorkModeByModSha1 reduce{
        config, kConsumer, kConsumerSpecialization, park_id};

    api_over_data::work_mode::Type result = api_over_data::work_mode::kNewWay;
    auto reduce_wrapper = [&result, &reduce]() {
      result = reduce(api_over_data::work_mode::Type::kNewWay);
    };

    ASSERT_NO_THROW(reduce_wrapper());
    EXPECT_EQ(api_over_data::work_mode::Type::kOldWay, result)
        << "for park id: " << park_id;
  }
}
