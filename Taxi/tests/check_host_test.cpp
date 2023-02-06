#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <config/config.hpp>

#include <api_over_data/revise_helpers.hpp>

namespace {
const std::string kConsumer = "test_consumer";
const std::string kConsumerSpecialization = "test_specialization";
const std::string kHost = "hosts";
const std::string kLogHint = "log_hint";

config::DocsMap DocsMapForTest(
    std::string query,
    const std::string& specialization = kConsumerSpecialization) {
  config::DocsMap docs_map = config::DocsMapForTest();
  mongo::BSONObjBuilder external_settings;
  external_settings.append(kHost, std::vector<std::string>{query});
  mongo::BSONObjBuilder test_specialization;
  test_specialization.append(specialization, external_settings.obj());
  mongo::BSONObjBuilder test_consumer;
  test_consumer.append(kConsumer, test_specialization.obj());
  docs_map.Override("API_OVER_DATA_WORK_MODE_EXTERNAL_CRITERION",
                    test_consumer.obj());
  return docs_map;
}

}  // namespace

TEST(ReduceWorkModeByHost, TestDefaultConfig) {
  auto docs_map = config::DocsMapForTest();
  config::Config config(docs_map);
  const auto& api_over_data_config =
      api_over_data::caches::GetApiOverDataConfig(config);
  auto hosts = api_over_data_config.extra_criterion_settings.Get(kConsumer)
                   .Get(kConsumerSpecialization)
                   .hosts;
  ASSERT_EQ(hosts, std::vector<std::string>{".*"});
}

TEST(ReduceWorkModeByHost, TestDefaultForConsumerSpecializationConfig) {
  auto docs_map = DocsMapForTest(".*", "__default__");
  config::Config config(docs_map);
  const auto& api_over_data_config =
      api_over_data::caches::GetApiOverDataConfig(config);
  auto hosts = api_over_data_config.extra_criterion_settings.Get(kConsumer)
                   .Get("unknown_consumer_specialization")
                   .hosts;
  ASSERT_EQ(*hosts, std::vector<std::string>{".*"});
}

TEST(ReduceWorkModeByHost, TestAllowed) {
  auto docs_map = DocsMapForTest(".*");
  config::Config config(docs_map);

  LogExtra log_extra;
  api_over_data::ReduceWorkModeByHost reduce{
      config, kConsumer, kConsumerSpecialization, log_extra};

  api_over_data::work_mode::Type result = api_over_data::work_mode::kOldWay;
  auto reduce_wrapper = [&result, &reduce]() {
    result = reduce(api_over_data::work_mode::Type::kNewWay);
  };

  ASSERT_NO_THROW(reduce_wrapper());
  ASSERT_EQ(api_over_data::work_mode::Type::kNewWay, result);
}

TEST(ReduceWorkModeByHost, TestDisallowed) {
  auto docs_map = DocsMapForTest("unknown-test-host");
  config::Config config(docs_map);

  LogExtra log_extra;
  api_over_data::ReduceWorkModeByHost reduce{
      config, kConsumer, kConsumerSpecialization, log_extra};

  api_over_data::work_mode::Type result = api_over_data::work_mode::kNewWay;
  auto reduce_wrapper = [&result, &reduce]() {
    result = reduce(api_over_data::work_mode::Type::kNewWay);
  };

  ASSERT_NO_THROW(reduce_wrapper());
  ASSERT_EQ(api_over_data::work_mode::Type::kOldWay, result);
}
