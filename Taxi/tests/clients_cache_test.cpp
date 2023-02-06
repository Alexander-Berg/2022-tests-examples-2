#include <algorithm>
#include <fstream>
#include <iostream>
#include <memory>
#include <unordered_set>
#include <utility>

#include <fmt/format.h>

#include <userver/logging/level.hpp>
#include <userver/utest/utest.hpp>

#include <testing/source_path.hpp>

#include <ua_parser/application.hpp>

#include <experiments3/models/clients_cache_impl.hpp>
#include <experiments3/models/errors.hpp>
#include <experiments3/models/experiment_data.hpp>
#include <experiments3/models/experiment_result.hpp>
#include <experiments3/models/files_manager.hpp>
#include <experiments3/models/host_info.hpp>
#include <experiments3/models/match_metrics_storage.hpp>
#include <experiments3/models/runtime_info_sender.hpp>
#include <experiments3/utils/files.hpp>
#include <experiments3_common/models/kwargs.hpp>

#include <tests/utils.hpp>

namespace exp3 = experiments3::models;
using LogExtra = logging::LogExtra;

namespace {

const std::string kFilesDir =
    utils::CurrentSourcePath("src/tests/static/clients_cache_test/");

const std::string kDumpDir = "/tmp/clients_cache_test_dir";

void UpdateCacheFromFile(
    exp3::ClientsCacheImpl& experiments_cache, const std::string& file_name,
    bool is_updates_valid = true,
    exp3::FilesManager& files_manager = exp3::kMockFilesManager) {
  auto updates = formats::json::blocking::FromFile(kFilesDir + file_name);
  switch (experiments_cache.GetType()) {
    case exp3::ExperimentType::kExperiment:
      updates = updates["experiments"];
      break;
    case exp3::ExperimentType::kConfig:
      updates = updates["configs"];
      break;
  }
  for (const auto& update : updates) {
    auto is_update_ok = experiments_cache.UpdateEntry(update, files_manager);
    ASSERT_EQ(is_update_ok, is_updates_valid);
  }
}

experiments3::models::impl::ClientsCacheDeps EmptyClientsCacheDeps() {
  return {{},
          {},
          std::make_shared<exp3::MatchMetricsStorage>(),
          ::logging::DefaultLogger(),
          true,
          ::logging::Level::kInfo,
          engine::current_task::GetTaskProcessor()};
};

exp3::ClientsCacheImpl EmptyExperimentsCache() {
  return exp3::ClientsCacheImpl("", "", exp3::ExperimentType::kExperiment,
                                EmptyClientsCacheDeps());
}

exp3::ClientsCacheImpl EmptyConfigsCache() {
  return exp3::ClientsCacheImpl("", "", exp3::ExperimentType::kConfig,
                                EmptyClientsCacheDeps());
}

std::optional<exp3::ExperimentResult> GetExperimentResultByName(
    const std::vector<exp3::ExperimentResult>& experiments_list,
    const std::string& name) {
  for (const auto& result : experiments_list) {
    if (result.name == name) {
      return result;
    }
  }
  return std::nullopt;
}

const std::string kApplication = "application";
const std::string kVersion = "version";
const std::string kZone = "zone";
const std::string kKey = "key";
const std::string kKeyInt = "key_int";
const std::string kTags = "tags";
const std::string kUserId = "user_id";
const std::string kFoo = "foo";
const std::string kBar = "bar";
const std::string kPhoneId = "phone_id";
const std::string kTimeStamp = "timestamp";

const std::string kIphone = "iphone";
const std::string kTaximeter = "taximeter";

class TestKwargsBuilder : public ::experiments3::models::KwargsBuilderMap {
  const ::experiments3::models::KwargsSchema& GetSchema() const override {
    static const auto kSchema = []() {
      experiments3::models::KwargsSchema schema = {
          {kUserId, {typeid(std::string), false, true}},
          {kZone, {typeid(std::string), false, true}},
          {kKey, {typeid(std::string), false, true}},
          {kKeyInt, {typeid(std::int64_t), false, true}},
          {kApplication, {typeid(std::string), false, true}},
          {kVersion, {typeid(ua_parser::ApplicationVersion), false, true}},
          {kTags, {typeid(std::unordered_set<std::string>), false, true}},
          {kFoo, {typeid(bool), false, true}},
          {kBar, {typeid(bool), false, true}},
          {kPhoneId, {typeid(std::int64_t), false, true}},
          {kTimeStamp, {typeid(std::int64_t), false, true}}};
      schema.insert(
          experiments3::models::schema_extensions::kDefaultSchemaExtension
              .begin(),
          experiments3::models::schema_extensions::kDefaultSchemaExtension
              .end());
      return schema;
    }();
    return kSchema;
  }

 public:
  void UpdateApplication(const std::string& application) {
    Update(kApplication, application);
  }
  void UpdateVersion(const ua_parser::ApplicationVersion& version) {
    Update(kVersion, version);
  }
};

const TestKwargsBuilder empty_kwargs_builder;

const ua_parser::ApplicationVersion default_version("9.8.7");

void CleanupDumpDir() { boost::filesystem::remove_all(kDumpDir); }

}  // namespace

UTEST_MT(ExperimentsCache, EmptyExperimentsCache, 2) {
  auto logger = ::logging::DefaultLogger();
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  const auto& data = experiments_cache.GetData(empty_kwargs_builder);
  ASSERT_EQ(data.size(), static_cast<size_t>(0));
}

UTEST_MT(ExperimentsCache, InvalidUpdates, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  EXPECT_NO_THROW(
      UpdateCacheFromFile(experiments_cache, "invalid_updates.json", false));
  ASSERT_EQ(experiments_cache.GetLastVersion(), -1);
}

UTEST_MT(ExperimentsCache, InFilePredicate, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  exp3::MockFilesManager files_manager;
  std::unordered_set<std::string> set1 = {"abc", "bca", "cab"};
  files_manager.UpdateFile("xyz", set1);
  UpdateCacheFromFile(experiments_cache, "in_file.json", true, files_manager);
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);
  builder.Update(kKey, std::string{"cab"});
  const auto& data1 = experiments_cache.GetData(builder);
  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(1));
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
}

UTEST_MT(ExperimentsCache, InFileIntPredicate, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  exp3::MockFilesManager files_manager;
  std::unordered_set<std::int64_t> s = {1, 228, 1000};
  files_manager.UpdateFile("xyz", s);

  UpdateCacheFromFile(experiments_cache, "in_file_int.json", true,
                      files_manager);
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);
  builder.Update(kKeyInt, std::int64_t{228});
  const auto data = experiments_cache.GetData(builder);
  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(1));
  ASSERT_EQ(data.size(), static_cast<size_t>(1));
}

UTEST_MT(ExperimentsCache, DefaultValuePredicate, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "default_01.json");
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);
  const auto& data1 = experiments_cache.GetData(builder);
  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(1));
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
}

UTEST_MT(ExperimentsCache, SignalClausesPredicates, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "signal_clauses.json");
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);
  const auto& data1 = experiments_cache.GetData(builder);
  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(2));
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
}

UTEST_MT(ExperimentsCache, LtEqBoolPredicates, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "lt_eq_bool.json");

  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(2));
  TestKwargsBuilder builder1;
  builder1.Update(kFoo, false);
  const auto& data1 = experiments_cache.GetData(builder1);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));

  TestKwargsBuilder builder2;
  builder2.Update(kBar, true);
  const auto& data2 = experiments_cache.GetData(builder2);
  ASSERT_EQ(data2.size(), static_cast<size_t>(1));
}

UTEST_MT(ExperimentsCache, TaximeterApplication, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "taximeter_application.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 1);
  TestKwargsBuilder builder;
  builder.UpdateApplication(kTaximeter);
  builder.UpdateVersion(default_version);
  const auto& data1 = experiments_cache.GetData(builder);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
  ASSERT_EQ(data1[0].value.As<int>(), 9875);
}

UTEST_MT(ExperimentsCache, ImproperVersions, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "improper_version_handling.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 1);
  TestKwargsBuilder builder;
  builder.UpdateApplication(kTaximeter);
  builder.UpdateVersion(default_version);
  const auto& data1 = experiments_cache.GetData(builder);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
  ASSERT_EQ(data1[0].value.As<int>(), 9875);
}

UTEST_MT(ExperimentsCache, TestWithoutApplications, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "no_apps.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 1);
  const auto& data1 = experiments_cache.GetData(empty_kwargs_builder);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
  ASSERT_EQ(data1[0].value.As<int>(), 9875);
}

UTEST_MT(ExperimentsCache, TestRemoval, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "removal_01.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 1);
  TestKwargsBuilder builder;
  builder.UpdateApplication(kTaximeter);
  builder.UpdateVersion(default_version);
  const auto& data1 = experiments_cache.GetData(builder);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));

  UpdateCacheFromFile(experiments_cache, "removal_02.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 2);
  const auto& data2 = experiments_cache.GetData(builder);
  ASSERT_EQ(data2.size(), static_cast<size_t>(0));
}

//тест проверяющий, что в кэш загружается валидный json и проверяется логика по
// kwargs
UTEST_MT(ExperimentsCache, LoadOnce, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "load_once_updates.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4426);

  ASSERT_EQ(experiments_cache.GetData(empty_kwargs_builder).size(),
            static_cast<size_t>(0));

  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);
  builder.Update(kZone, std::string{"msk"});

  const auto& data1 = experiments_cache.GetData(builder);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
  ASSERT_EQ(data1[0].value.As<int>(), 100);
  builder.Update(kZone, std::string{"spb"});
  const auto& data2 = experiments_cache.GetData(builder);
  ASSERT_EQ(data2.size(), static_cast<size_t>(1));
  ASSERT_EQ(data2[0].value.As<int>(), 100);

  builder.Update(kZone, std::string{"izhevsk"});
  const auto& data3 = experiments_cache.GetData(builder);
  ASSERT_EQ(data3.size(), static_cast<size_t>(1));
  ASSERT_EQ(data3[0].value.As<int>(), 50);
}

//тест в котором в одном из экспериментов меняются приоритеты clause'ов (их
//порядок) и за счет этого - один запрос после изменения возвращает другой
//результат
UTEST_MT(ExperimentsCache, ChangePriority, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "change_priority_first_updates.json");
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);
  builder.Update(kZone, std::string{"msk"});
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4426);
  ASSERT_EQ(experiments_cache.GetData(builder)[0].value.As<int>(), 100);
  UpdateCacheFromFile(experiments_cache, "change_priority_second_updates.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4427);
  ASSERT_EQ(experiments_cache.GetData(builder)[0].value.As<int>(), 50);
}

//один из экспериментов выключается, проверка, что запрос ничего не возвращает,
//если enabled == false
UTEST_MT(ExperimentsCache, RemoveOne, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "remove_one_first_updates.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4426);
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);
  builder.Update(kZone, std::string{"msk"});
  ASSERT_EQ(experiments_cache.GetData(builder).size(), static_cast<size_t>(1));
  UpdateCacheFromFile(experiments_cache, "remove_one_second_updates.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4427);
  ASSERT_EQ(experiments_cache.GetData(builder).size(), static_cast<size_t>(0));
}

//тест, который проверяет, что ничего не изменится, если придет апдейт с более
//старой версией
UTEST_MT(ExperimentsCache, UpdateWithOlderVersion, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "older_version_first_updates.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4426);
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);
  builder.Update(kZone, std::string{"msk"});
  ASSERT_EQ(experiments_cache.GetData(builder)[0].value.As<int>(), 100);
  UpdateCacheFromFile(experiments_cache, "older_version_second_updates.json",
                      false);
  ASSERT_EQ(experiments_cache.GetData(builder)[0].value.As<int>(), 100);
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4426);
}

UTEST_MT(ExperimentsCache, ContainsPredicate, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "contains_predicates_updates.json");
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);

  builder.Update(kTags, std::unordered_set<std::string>{"male"});

  ASSERT_EQ(GetExperimentResultByName(experiments_cache.GetData(builder),
                                      "CONTAINS_CONFIG")
                ->value.As<int>(),
            1);
  builder.Update(kTags, std::unordered_set<std::string>{"female"});
  ASSERT_EQ(GetExperimentResultByName(experiments_cache.GetData(builder),
                                      "CONTAINS_CONFIG")
                ->value.As<int>(),
            0);
  builder.Update(kTags, std::unordered_set<std::string>{"other"});
  ASSERT_EQ(GetExperimentResultByName(experiments_cache.GetData(builder),
                                      "CONTAINS_CONFIG")
                ->value.As<int>(),
            0);
  ASSERT_FALSE(GetExperimentResultByName(
      experiments_cache.GetData(empty_kwargs_builder), "CONTAINS_CONFIG"));

  builder.Update(kTags, std::unordered_set<std::string>{"123"});
  ASSERT_EQ(GetExperimentResultByName(experiments_cache.GetData(builder),
                                      "CONTAINS_INT_CONFIG")
                ->value.As<int>(),
            1);
  builder.Update(kTags, std::unordered_set<std::string>{"1"});
  ASSERT_EQ(GetExperimentResultByName(experiments_cache.GetData(builder),
                                      "CONTAINS_INT_CONFIG")
                ->value.As<int>(),
            0);
  builder.Update(kTags, std::unordered_set<std::string>{});
  ASSERT_EQ(GetExperimentResultByName(experiments_cache.GetData(builder),
                                      "CONTAINS_INT_CONFIG")
                ->value.As<int>(),
            0);
}

UTEST_MT(ExperimentsCache, AllOfPredicate, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "all_of_predicates_updates.json");
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);
  builder.Update(kPhoneId, static_cast<std::int64_t>(1));
  builder.Update(kZone, std::string("msk"));

  ASSERT_EQ(experiments_cache.GetData(builder).size(), static_cast<size_t>(1));

  builder.Update(kZone, std::string("spb"));
  ASSERT_EQ(experiments_cache.GetData(builder).size(), static_cast<size_t>(0));

  builder.Update(kPhoneId, static_cast<std::int64_t>(0));
  ASSERT_EQ(experiments_cache.GetData(builder).size(), static_cast<size_t>(0));
}

UTEST_MT(ExperimentsCache, AnyOfPredicate, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "any_of_predicates_updates.json");
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);

  ASSERT_EQ(experiments_cache.GetData(builder).size(), static_cast<size_t>(0));

  builder.Update(kPhoneId, static_cast<std::int64_t>(1));
  builder.Update(kZone, std::string("msk"));

  ASSERT_EQ(experiments_cache.GetData(builder).size(), static_cast<size_t>(1));
  builder.Update(kPhoneId, static_cast<std::int64_t>(0));
  ASSERT_EQ(experiments_cache.GetData(builder).size(), static_cast<size_t>(1));

  builder.Update(kPhoneId, static_cast<std::int64_t>(1));
  builder.Update(kZone, std::string("spb"));
  ASSERT_EQ(experiments_cache.GetData(builder).size(), static_cast<size_t>(1));
}

UTEST_MT(ExperimentsCache, Sha1Predicate, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "sha1_predicates_updates.json");
  std::vector<std::string> user_ids;
  for (int i = 0; i < 100; ++i) {
    user_ids.emplace_back(std::to_string(i));
  }

  std::unordered_map<int, int> stat;
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);

  for (const auto& user_id : user_ids) {
    builder.Update(kUserId, user_id);
    int group_id = (*GetExperimentResultByName(
                        experiments_cache.GetData(builder), "GROUPS"))
                       .value.As<int>();

    auto it = stat.find(group_id);
    if (it == stat.end()) {
      stat[group_id] = 0;
    }
    stat[group_id] += 1;
  }

  ASSERT_EQ(stat.find(0), stat.end());
}

UTEST_MT(ExperimentsCache, Sha1PredicateWithRoundUp, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "sha1_round_up_updates.json");

  std::vector<std::int64_t> timestamps;
  const int count_groups = 2;
  for (std::int64_t i = 0; i < count_groups * 60; ++i) {
    timestamps.emplace_back(i);
  }

  std::unordered_map<int, int> stat;
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);

  for (const std::int64_t timestamp : timestamps) {
    builder.Update(kTimeStamp, timestamp);
    int group_id = (*GetExperimentResultByName(
                        experiments_cache.GetData(builder), "GROUPS"))
                       .value.As<int>();

    auto it = stat.find(group_id);
    if (it == stat.end()) {
      stat[group_id] = 0;
    }
    stat[group_id] += 1;
  }

  ASSERT_EQ(stat.size(), count_groups);
  ASSERT_EQ(stat.find(0), stat.end());
}

UTEST_MT(ExperimentsCache, IgnoreActionTimeInConfig, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  exp3::ClientsCacheImpl configs_cache = EmptyConfigsCache();
  UpdateCacheFromFile(experiments_cache, "expired_experiment.json");
  UpdateCacheFromFile(configs_cache, "expired_config.json");

  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);

  const auto& experiments_result = experiments_cache.GetData(builder);
  ASSERT_EQ(experiments_result.size(), static_cast<size_t>(0));
  const auto& configs_result = configs_cache.GetData(builder);
  ASSERT_EQ(configs_result.size(), static_cast<size_t>(1));
}

UTEST_MT(ExperimentsCache, TestGradualShutdown, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  exp3::ClientsCacheImpl configs_cache = EmptyConfigsCache();
  UpdateCacheFromFile(experiments_cache, "gradual_shutdown_experiment.json");
  UpdateCacheFromFile(configs_cache, "gradual_shutdown_config.json");

  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);

  const auto& experiments_result = experiments_cache.GetData(builder);
  ASSERT_EQ(experiments_result.size(), static_cast<size_t>(1));
  const auto& configs_result = configs_cache.GetData(builder);
  ASSERT_EQ(configs_result.size(), static_cast<size_t>(1));
}

UTEST_MT(ExperimentsCache, ConsumerKwarg, 2) {
  exp3::ClientsCacheImpl consumer1_cache(
      "consumer1", "", exp3::ExperimentType::kExperiment,
      {{},
       {},
       std::make_shared<exp3::MatchMetricsStorage>(),
       logging::DefaultLogger(),
       true,
       ::logging::Level::kInfo,
       engine::current_task::GetTaskProcessor()});
  exp3::ClientsCacheImpl consumer2_cache(
      "consumer2", "", exp3::ExperimentType::kExperiment,
      {{},
       {},
       std::make_shared<exp3::MatchMetricsStorage>(),
       logging::DefaultLogger(),
       true,
       ::logging::Level::kInfo,
       engine::current_task::GetTaskProcessor()});

  UpdateCacheFromFile(consumer1_cache, "consumer_kwarg.json");
  UpdateCacheFromFile(consumer2_cache, "consumer_kwarg.json");

  TestKwargsBuilder kwargs;

  auto result1 = consumer1_cache.GetData(kwargs);
  ASSERT_EQ(1u, result1.size());

  auto result2 = consumer2_cache.GetData(kwargs);
  ASSERT_EQ(0u, result2.size());
}

UTEST_MT(ExperimentsCache, GetByName, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();

  UpdateCacheFromFile(experiments_cache, "default_01.json");

  TestKwargsBuilder builder;

  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);

  auto result1 = experiments_cache.GetByName("BASIC", builder);
  ASSERT_TRUE(result1.has_value());
  auto result2 = experiments_cache.GetByName("INVALID_NAME", builder);
  ASSERT_FALSE(result2.has_value());
}

namespace {
class TestKwargsBuilderSmallSchema
    : public ::experiments3::models::KwargsBuilderMap {
  const ::experiments3::models::KwargsSchema& GetSchema() const override {
    static const auto kSchema = []() {
      ::experiments3::models::KwargsSchema schema = {
          {kUserId, {typeid(std::string), false, true}}};
      schema.insert(
          experiments3::models::schema_extensions::kDefaultSchemaExtension
              .begin(),
          experiments3::models::schema_extensions::kDefaultSchemaExtension
              .end());
      return schema;
    }();
    return kSchema;
  }
};
}  // namespace

UTEST_MT(ExperimentsCache, DifferentSchemas, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();

  UpdateCacheFromFile(experiments_cache, "default_01.json");

  TestKwargsBuilder builder1;
  builder1.UpdateApplication(kIphone);
  builder1.UpdateVersion(default_version);

  TestKwargsBuilderSmallSchema builder2;

  auto result1 = experiments_cache.GetByName("BASIC", builder1);
  ASSERT_TRUE(result1.has_value());
  auto result2 = experiments_cache.GetByName("BASIC", builder2);
  ASSERT_FALSE(result2.has_value());
}

UTEST_MT(ExperimentsCache, VersionRanges, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "version_ranges.json");
  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(1));

  TestKwargsBuilder builder1;
  builder1.UpdateApplication(kIphone);
  builder1.UpdateVersion(ua_parser::ApplicationVersion("1.0.0"));
  const auto& data1 = experiments_cache.GetData(builder1);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));

  TestKwargsBuilder builder2;
  builder1.UpdateApplication(kIphone);
  builder1.UpdateVersion(ua_parser::ApplicationVersion("5.0.0"));
  const auto& data2 = experiments_cache.GetData(builder2);
  ASSERT_TRUE(data2.empty());
}

UTEST_MT(ExperimentsCache, MergedExperimentResult, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "exp_for_merging.json");
  TestKwargsBuilder builder;
  const auto& result = experiments_cache.GetData(builder);

  ASSERT_EQ(result.size(), 2);

  size_t id0 = (result[0].name < result[1].name ? 0 : 1);
  size_t id1 = id0 ^ 1;

  ASSERT_TRUE(result[id0].IsMerged());
  ASSERT_TRUE(result[id1].IsMerged());
  ASSERT_EQ(result[id0].name, "some_tag");
  ASSERT_EQ(result[id1].name, "some_tag2");
  ASSERT_EQ(result[id0].value,
            formats::json::FromString("{\"key1\":1,\"key2\":2,\"key3\":3}"));
  ASSERT_EQ(result[id1].value,
            formats::json::FromString("{\"key1\":1,\"key2\":2}"));

  auto& meta_info = std::get<exp3::MergedResultMetaInfo>(result[id0].meta_info);
  ASSERT_EQ(meta_info.data.size(), 3);
  ASSERT_EQ(meta_info.merge_method,
            exp3::MergeResultsMethod::kDictsRecursiveMerge);
}

UTEST_MT(ExperimentsCache, MergedExperimentResultBig, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "exp_for_merging_big.json");
  TestKwargsBuilder builder;
  const auto& results = experiments_cache.GetData(builder);

  ASSERT_EQ(results.size(), 2);
  for (const auto& result : results) {
    ASSERT_TRUE(result.IsMerged());
    ASSERT_EQ(result.value, formats::json::blocking::FromFile(
                                kFilesDir + result.name + "_result.json"));
  }
}

UTEST_MT(ExperimentsCache, ArgumentsInModSha1WithSalt, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "mod_sha1_with_salt_arguments.json");

  TestKwargsBuilder builder;

  builder.Update(kApplication, std::string{"str"});
  builder.Update(kZone, std::string{"str"});
  builder.Update(kUserId, std::string{"str"});

  const auto& results = experiments_cache.GetData(builder);

  ASSERT_EQ(results.size(), 1);
}

UTEST_MT(ExperimentsCache, MatchingStatistics, 2) {
  std::shared_ptr<exp3::MatchMetricsStorage> metric_storage =
      std::make_shared<exp3::MatchMetricsStorage>();
  auto experiments_cache =
      exp3::ClientsCacheImpl("", "", exp3::ExperimentType::kExperiment,
                             {{},
                              {},
                              metric_storage,
                              ::logging::DefaultLogger(),
                              true,
                              ::logging::Level::kInfo,
                              engine::current_task::GetTaskProcessor()});

  UpdateCacheFromFile(experiments_cache, "default_01.json");
  TestKwargsBuilder builder;
  builder.UpdateApplication(kIphone);
  builder.UpdateVersion(default_version);
  const auto data = experiments_cache.GetData(builder);

  auto metrics = metric_storage->GetMatchMetrics();

  ASSERT_EQ(metrics["experiments3.experiment.BASIC.default"]->load(), 1);
}

UTEST_MT(ExperimentsCache, ReadData, 2) {
  auto cache = exp3::ClientsCacheImpl(
      "consumer_name1", fmt::format("{}read_data", kFilesDir),
      exp3::ExperimentType::kExperiment, EmptyClientsCacheDeps());

  cache.ReadData(exp3::kMockFilesManager);

  auto res = cache.GetMappedData(TestKwargsBuilder{});
  ASSERT_EQ(res["test1"].value["key"].As<std::string>(), std::string{"value"});
}

UTEST_MT(ExperimentsCache, DisabledClause, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();
  UpdateCacheFromFile(experiments_cache, "disabled_clause.json");
  TestKwargsBuilder builder;
  auto result = experiments_cache.GetByName("disabled_clause_exp", builder);
  ASSERT_TRUE(result.has_value());
  ASSERT_EQ(result->value.As<std::string>(), "value_enabled_clause");
}

TEST(ExperimentsCache, FlatDefaultKwargs) {
  using namespace experiments3::models::default_kwargs;
  experiments3::models::impl::FlatDefaultKwargs kwargs;
  kwargs.Update(kCgroups, kCgroups);
  kwargs.Update(kConsumer, kConsumer);
  kwargs.Update(kNgroups, kNgroups);
  kwargs.Update(kHost, kHost);
  kwargs.Update(kIsPrestable, kIsPrestable);
  kwargs.Update(kRequestTimestampMs, kRequestTimestampMs);
  kwargs.Update(kRequestTimestampMinutes, kRequestTimestampMinutes);

  size_t calls_cnt = 0;
  kwargs.ForEach(
      [&calls_cnt](const experiments3::models::KwargName& name,
                   const experiments3::models::KwargValue& value) mutable {
        ++calls_cnt;
        const auto& value_str = std::get<std::string>(value);
        ASSERT_EQ(name, value_str);
      });
  ASSERT_EQ(calls_cnt, 7);
}

UTEST_MT(ExperimentsCache, PrestableTest, 2) {
  auto make_cache = [](bool is_prestable) {
    auto host_info_ptr = std::make_shared<exp3::HostInfo>(
        std::unordered_set<std::string>{}, exp3::HostGroupsType::kClownductor,
        is_prestable);
    return exp3::ClientsCacheImpl(
        "", "", exp3::ExperimentType::kExperiment,
        {{},
         std::move(host_info_ptr),
         std::make_shared<exp3::MatchMetricsStorage>(),
         ::logging::DefaultLogger(),
         true,
         ::logging::Level::kInfo,
         engine::current_task::GetTaskProcessor()});
  };
  auto cache_prestable = make_cache(true);
  auto cache_stable = make_cache(false);
  UpdateCacheFromFile(cache_prestable, "only_prestable.json");
  UpdateCacheFromFile(cache_stable, "only_prestable.json");
  ASSERT_EQ(cache_prestable.GetData(TestKwargsBuilder{}).size(), 1);
  ASSERT_EQ(cache_stable.GetData(TestKwargsBuilder{}).size(), 0);

  // Test that `prestable` tag just skips update, and not removes exp
  UpdateCacheFromFile(cache_stable, "not_only_prestable.json");
  ASSERT_EQ(cache_stable.GetData(TestKwargsBuilder{}).size(), 1);
  UpdateCacheFromFile(cache_stable, "only_prestable_v2.json");
  ASSERT_EQ(cache_stable.GetData(TestKwargsBuilder{}).size(), 1);
}

// Check application without version
UTEST_MT(ExperimentsCache, Versionless, 2) {
  exp3::ClientsCacheImpl experiments_cache = EmptyExperimentsCache();

  UpdateCacheFromFile(experiments_cache, "no_version.json");

  TestKwargsBuilder builder1;
  builder1.UpdateApplication(kIphone);

  auto result1 = experiments_cache.GetByName("BASIC", builder1);
  ASSERT_TRUE(result1.has_value());
}

UTEST_MT(ExperimentsCache, RemovedTest, 2) {
  auto cache = EmptyExperimentsCache();
  UpdateCacheFromFile(cache, "removed.json");
}

UTEST(ExperimentsCache, CheckExperimentOverwriteAndDump) {
  auto cache = exp3::ClientsCacheImpl(
      "", kDumpDir, exp3::ExperimentType::kConfig, EmptyClientsCacheDeps());
  UpdateCacheFromFile(cache, "test_configs.json");
  // read the same configs once again. "Updates" have the same version, but it
  // shall no corrupt the cache
  UpdateCacheFromFile(cache, "test_configs.json");
  cache.DumpData();

  // read dump and check that configs equal to the configs from initial cache
  auto cache2 = exp3::ClientsCacheImpl(
      "", kDumpDir, exp3::ExperimentType::kConfig, EmptyClientsCacheDeps());
  cache2.ReadData(exp3::kMockFilesManager);

  TestKwargsBuilder builder;
  for (const auto& config : {"test_config1", "test_config2", "test_config3"}) {
    auto value1 = cache.GetByName(config, builder);
    ASSERT_TRUE(value1.has_value());
    auto value2 = cache2.GetByName(config, builder);
    ASSERT_TRUE(value2.has_value());
    ASSERT_EQ(value1->value, value2->value);
  }

  CleanupDumpDir();
}
