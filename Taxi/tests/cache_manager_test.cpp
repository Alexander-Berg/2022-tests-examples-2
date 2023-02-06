#include <testing/source_path.hpp>
#include <userver/utest/utest.hpp>
#include <userver/utils/mock_now.hpp>

#include "utils.hpp"

#include <experiments3/models/experiment_type.hpp>
#include <experiments3/models/for_lib/cache_manager_full.hpp>

namespace exp3 = experiments3::models;

const std::string kConsumer = "test_consumer";
const std::string kFilesDir =
    utils::CurrentSourcePath("src/tests/static/cache_manager_test/");

const std::string kUserId = "user_id";
const std::string kKeyInt = "key_int";

const auto mocked_time = utils::datetime::Stringtime("2022-01-17T12:00:00+03");

class TestKwargsBuilder : public exp3::KwargsBuilderMap,
                          public exp3::KwargsBuilderWithConsumer {
  const exp3::KwargsSchema& GetSchema() const override {
    static const auto kSchema = []() {
      exp3::KwargsSchema schema = {
          {kUserId, {typeid(std::string), false, true}},
          {kKeyInt, {typeid(std::int64_t), false, true}}};
      schema.insert(
          experiments3::models::schema_extensions::kDefaultSchemaExtension
              .begin(),
          experiments3::models::schema_extensions::kDefaultSchemaExtension
              .end());
      return schema;
    }();
    return kSchema;
  }
  const std::string& GetConsumer() const override {
    static const std::string consumer = "test_consumer";
    return consumer;
  }
};

struct TestValue {
  TestValue(bool b, const std::string& s, int i)
      : value_bool(b), value_string(s), value_int(i) {}

  bool value_bool;
  std::string value_string;
  int value_int;
};

bool operator==(const TestValue& lhs, const TestValue& rhs) {
  return std::tie(lhs.value_bool, lhs.value_string, lhs.value_int) ==
         std::tie(rhs.value_bool, rhs.value_string, rhs.value_int);
}

std::ostream& operator<<(std::ostream& os, const TestValue& value) {
  return os << value.value_bool << " " << value.value_string << " "
            << value.value_int;
}

TestValue Parse(const formats::json::Value& value,
                formats::parse::To<TestValue>) {
  return {value["value_bool"].As<bool>(),
          value["value_string"].As<std::string>(),
          value["value_int"].As<int>()};
}

struct TestValue2 {
  double value_double;
};

TestValue2 Parse(const formats::json::Value& value,
                 formats::parse::To<TestValue2>) {
  return {value["value_double"].As<double>()};
}

struct TestExperiment {
  using Value = TestValue;
  using Type = experiments3::models::ExperimentType;
  constexpr static auto kType = exp3::ExperimentType::kExperiment;
  constexpr static bool kCacheResult = true;
  constexpr static auto kName = "test_experiment";
};

struct WrongExperiment {
  using Value = TestValue2;
  using Type = experiments3::models::ExperimentType;
  constexpr static auto kType = exp3::ExperimentType::kExperiment;
  constexpr static bool kCacheResult = true;
  constexpr static auto kName = "test_experiment";
};

struct TestConfig {
  using Value = TestValue;
  using Type = experiments3::models::ExperimentType;
  constexpr static auto kType = exp3::ExperimentType::kConfig;
  constexpr static bool kCacheResult = true;
  constexpr static auto kName = "test_config";
};

struct WrongConfig {
  using Value = TestValue2;
  using Type = experiments3::models::ExperimentType;
  constexpr static auto kType = exp3::ExperimentType::kConfig;
  constexpr static bool kCacheResult = true;
  constexpr static auto kName = "test_config";
};

struct NoncacheableExperiment {
  using Value = TestValue;
  using Type = experiments3::models::ExperimentType;
  constexpr static auto kType = exp3::ExperimentType::kExperiment;
  constexpr static bool kCacheResult = false;
  constexpr static auto kName = "test_experiment";
};

exp3::CacheManagerFull GetCacheManager() {
  return exp3::CacheManagerFull(engine::current_task::GetTaskProcessor());
}

void UpdateCacheFromFile(exp3::CacheManagerFull& cache_manager,
                         const std::string& file, exp3::ExperimentType type) {
  experiments3::impl::test_utils::CacheManagerHelper cache_manager_helper(
      kFilesDir);
  cache_manager_helper.UpdateCacheFromFile(cache_manager, kConsumer, file,
                                           type);
}

UTEST_MT(CacheManagerTest, ReadExperiment, 2) {
  utils::datetime::MockNowSet(mocked_time);
  auto experiments = GetCacheManager();
  UpdateCacheFromFile(experiments, "test_experiments.json",
                      exp3::ExperimentType::kExperiment);

  TestKwargsBuilder builder;
  auto value = experiments.GetValue<TestExperiment>(builder);
  ASSERT_FALSE(value);

  builder.Update(kUserId, std::string("wrong_id"));
  value = experiments.GetValue<TestExperiment>(builder);
  ASSERT_FALSE(value);

  // default value
  builder.Update(kUserId, std::string("test_id"));
  value = experiments.GetValue<TestExperiment>(builder);
  ASSERT_TRUE(value);
  EXPECT_EQ(*value, TestValue(true, "default", -1));

  // clause #1
  builder.Update(kKeyInt, std::int64_t{1});
  value = experiments.GetValue<TestExperiment>(builder);
  ASSERT_TRUE(value);
  EXPECT_EQ(*value, TestValue(true, "clause#1", 1));

  // clause #3
  builder.Update(kKeyInt, std::int64_t{3});
  value = experiments.GetValue<TestExperiment>(builder);
  ASSERT_TRUE(value);
  EXPECT_EQ(*value, TestValue(true, "clause#3", 3));
}

UTEST_MT(CacheManagerTest, ParsedExperimentUpdate, 2) {
  utils::datetime::MockNowSet(mocked_time);
  auto experiments = GetCacheManager();
  UpdateCacheFromFile(experiments, "test_experiments.json",
                      exp3::ExperimentType::kExperiment);

  TestKwargsBuilder builder;
  builder.Update(kUserId, std::string("test_id"));
  builder.Update(kKeyInt, std::int64_t{1});

  // fill cache
  auto value = experiments.GetValue<TestExperiment>(builder);
  ASSERT_TRUE(value);
  EXPECT_EQ(*value, TestValue(true, "clause#1", 1));

  // take value from cache
  value = experiments.GetValue<TestExperiment>(builder);
  ASSERT_TRUE(value);
  EXPECT_EQ(*value, TestValue(true, "clause#1", 1));

  UpdateCacheFromFile(experiments, "test_experiments2.json",
                      exp3::ExperimentType::kExperiment);

  // cache is refreshed
  value = experiments.GetValue<TestExperiment>(builder);
  ASSERT_TRUE(value);
  EXPECT_EQ(*value, TestValue(true, "updated_clause#1", 1));
}

UTEST_MT(CacheManagerTest, ReadConfig, 2) {
  utils::datetime::MockNowSet(mocked_time);
  auto experiments = GetCacheManager();
  UpdateCacheFromFile(experiments, "test_configs.json",
                      exp3::ExperimentType::kConfig);

  // default value
  TestKwargsBuilder builder;
  auto value = experiments.GetValue<TestConfig>(builder);
  ASSERT_TRUE(value);
  EXPECT_EQ(*value, TestValue(true, "default", -1));

  // default value
  builder.Update(kUserId, std::string("test_id"));
  value = experiments.GetValue<TestConfig>(builder);
  ASSERT_TRUE(value);
  EXPECT_EQ(*value, TestValue(true, "default", -1));

  // clause #1
  builder.Update(kKeyInt, std::int64_t{1});
  value = experiments.GetValue<TestConfig>(builder);
  ASSERT_TRUE(value);
  EXPECT_EQ(*value, TestValue(true, "clause#1", 1));

  // clause #3
  builder.Update(kKeyInt, std::int64_t{3});
  value = experiments.GetValue<TestConfig>(builder);
  ASSERT_TRUE(value);
  EXPECT_EQ(*value, TestValue(true, "clause#3", 3));
}

UTEST_MT(CacheManagerTest, ReadParsedExperimentUsingWrongType, 2) {
  utils::datetime::MockNowSet(mocked_time);
  auto experiments = GetCacheManager();
  UpdateCacheFromFile(experiments, "test_experiments.json",
                      exp3::ExperimentType::kExperiment);

  // cache value
  TestKwargsBuilder builder;
  builder.Update(kUserId, std::string("test_id"));
  auto value1 = experiments.GetValue<TestExperiment>(builder);
  ASSERT_TRUE(value1);
  EXPECT_EQ(*value1, TestValue(true, "default", -1));

  // read the same exp using another type
  auto value2 = experiments.GetValue<WrongExperiment>(builder);
  ASSERT_FALSE(value2);
}

UTEST_MT(CacheManagerTest, ReadParsedConfigUsingWrongType, 2) {
  utils::datetime::MockNowSet(mocked_time);
  auto experiments = GetCacheManager();
  UpdateCacheFromFile(experiments, "test_configs.json",
                      exp3::ExperimentType::kConfig);

  // cache value
  TestKwargsBuilder builder;
  builder.Update(kUserId, std::string("test_id"));
  auto value1 = experiments.GetValue<TestConfig>(builder);
  ASSERT_TRUE(value1);
  EXPECT_EQ(*value1, TestValue(true, "default", -1));

  // read the same config using another type
  EXPECT_THROW(experiments.GetValue<WrongConfig>(builder),
               formats::json::Exception);
}

UTEST_MT(CacheManagerTest, ReadExperimentWithoutCache, 2) {
  utils::datetime::MockNowSet(mocked_time);
  auto experiments = GetCacheManager();
  experiments3::impl::test_utils::CacheManagerHelper cache_manager_helper(
      kFilesDir);

  TestKwargsBuilder kwargs;
  kwargs.Update(kUserId, std::string("test_id"));
  kwargs.Update(kKeyInt, std::int64_t{1});

  auto updates =
      formats::json::blocking::FromFile(kFilesDir + "test_experiments.json");
  updates = updates["experiments"];
  for (auto i = 1; i <= 5; ++i) {
    for (const auto& update : updates) {
      formats::json::ValueBuilder builder(update);
      // update value, but do no update version
      builder["clauses"][0]["value"]["value_int"] = i;
      // clear storage before update to workaround version check,
      // although cache of parsed structures is not cleared
      cache_manager_helper.ClearStorage(experiments);
      cache_manager_helper.UpdateCacheFromJson(
          experiments, "test_consumer", exp3::ExperimentType::kExperiment,
          builder.ExtractValue());

      // read clause #1
      auto value = experiments.GetValue<NoncacheableExperiment>(kwargs);
      ASSERT_TRUE(value);
      // check that value changes, thus we make sure that caching is turned off
      EXPECT_EQ(*value, TestValue(true, "clause#1", i));
    }
  }
}
