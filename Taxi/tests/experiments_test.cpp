#include <fstream>
#include <iostream>
#include <memory>

#include <gtest/gtest.h>

#include <experiments3_common/models/errors.hpp>
#include <experiments3_common/models/types.hpp>
#include <models/configs.hpp>
#include <models/experiments3/experiment_data.hpp>
#include <models/experiments3_clients_cache.hpp>
#include <models/experiments3_clients_cache_forwards.hpp>
#include <utils/application.hpp>
#include <utils/experiments3/files.hpp>
#include <utils/file_system.cpp>
#include <utils/hash.hpp>
#include <utils/helpers/json.hpp>
#include <utils/helpers/params.hpp>
#include <utils/known_apps.hpp>

namespace exp3 = experiments3::models;

const exp3::Kwargs empty_kwargs = {};

namespace {

void UpdateCacheFromFile(
    exp3::ClientsCache& experiments_cache, const std::string& file_name,
    exp3::FilesManager& files_manager = exp3::kMockFilesManager) {
  std::ifstream input_stream(SOURCE_DIR "/tests/static/" + file_name);

  auto updates_json = ::utils::helpers::ParseJson(input_stream);

  switch (experiments_cache.GetType()) {
    case exp3::ExperimentType::kExperiment:
      updates_json = updates_json["experiments"];
      break;
    case exp3::ExperimentType::kConfig:
      updates_json = updates_json["configs"];
      break;
  }

  for (const auto& update : updates_json) {
    experiments_cache.UpdateEntry(update, files_manager, {});
  }
}

exp3::ClientsCache EmptyCache() {
  return exp3::ClientsCache("", "", exp3::ExperimentType::kExperiment, {});
}

boost::optional<exp3::ClientsCache::ExperimentResult> GetExperimentResultByName(
    const std::vector<exp3::ClientsCache::ExperimentResult>& experiments_list,
    const std::string& name) {
  for (const auto& result : experiments_list) {
    if (result.name == name) {
      return result;
    }
  }
  return boost::none;
}

class TestKwargsBuilder : public ::experiments3::models::KwargsBuilder {
  const ::experiments3::models::KwargsSchema schema_ = {
      {"application", {typeid(std::string), false, true}},
      {"version", {typeid(models::ApplicationVersion), false, true}}};

  const ::experiments3::models::KwargsSchema& GetSchema() const override {
    return schema_;
  }

 public:
  void UpdateApplication(const std::string& application) {
    UpdateCommon("application", application);
  }
  void UpdateVersion(const models::ApplicationVersion& version) {
    UpdateCommon("version", version);
  }
};

}  // namespace

TEST(ExperimentsCache, EmptyCache) {
  LogExtra log_extra;
  exp3::ClientsCache experiments_cache = EmptyCache();
  const auto& data = experiments_cache.GetData(empty_kwargs, log_extra);
  ASSERT_EQ(data.size(), static_cast<size_t>(0));
}

TEST(ExperimentsCache, InvalidUpdates) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  EXPECT_NO_THROW(
      UpdateCacheFromFile(experiments_cache, "invalid_updates.json"));
  ASSERT_EQ(experiments_cache.GetLastVersion(), -1);
}

TEST(ExperimentsCache, InFilePredicate) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  experiments3::models::MockFilesManager files_manager;
  std::unordered_set<std::string> set1 = {"abc", "bca", "cab"};

  files_manager.UpdateFile("xyz", set1);

  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "in_file.json", files_manager);
  const auto& data1 = experiments_cache.GetData(
      {{"version", models::ApplicationVersion{"9.8.7"}},
       {"application", models::applications::Iphone},
       {"key", std::string{"cab"}}},
      log_extra);
  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(1));
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
}

TEST(ExperimentsCache, DefaultValuePredicate) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "default_01.json");
  const auto& data1 = experiments_cache.GetData(
      {{"version", models::ApplicationVersion{"9.8.7"}},
       {"application", models::applications::Iphone}},
      log_extra);
  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(1));
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
}

TEST(ExperimentsCache, SignalClausesPredicates) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "signal_clauses.json");
  const auto& data1 = experiments_cache.GetData(
      {{"version", models::ApplicationVersion{"9.8.7"}},
       {"application", models::applications::Iphone}},
      log_extra);
  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(2));
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
}

TEST(ExperimentsCache, PredicateFromOlegErmakov) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "crazy.json");
  const auto& data1 = experiments_cache.GetData(
      {{"version", models::ApplicationVersion{"9.8.7"}},
       {"application", models::applications::Iphone},
       {"accept_language", std::string("ru")},
       {"phone_id", std::string("5b7e9283030553e65806b18e")},
       {"personal_phone_id", std::string("5b7e9283030553e65806b18e")}},
      log_extra);
  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(1));
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
}

TEST(ExperimentsCache, LtEqBoolPredicates) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "lt_eq_bool.json");

  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(2));
  const auto& data1 = experiments_cache.GetData({{"foo", false}}, log_extra);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));

  const auto& data2 = experiments_cache.GetData({{"bar", true}}, log_extra);
  ASSERT_EQ(data2.size(), static_cast<size_t>(1));
}

TEST(ExperimentsCache, TaximeterApplication) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  UpdateCacheFromFile(experiments_cache, "taximeter_application.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 1);
  LogExtra log_extra;
  const auto& data1 = experiments_cache.GetData(
      {{"version", models::ApplicationVersion{"9.8.7"}},
       {"application", models::applications::Taximeter}},
      log_extra);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
  ASSERT_EQ(data1[0].value.asInt(), 9875);
}

TEST(ExperimentsCache, ImproperVersions) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  UpdateCacheFromFile(experiments_cache, "improper_version_handling.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 1);
  LogExtra log_extra;
  const auto& data1 = experiments_cache.GetData(
      {{"version", models::ApplicationVersion{"9.8.7"}},
       {"application", models::applications::Taximeter}},
      log_extra);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
  ASSERT_EQ(data1[0].value.asInt(), 9875);
}

TEST(ExperimentsCache, TestWithoutApplications) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  UpdateCacheFromFile(experiments_cache, "no_apps.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 1);
  LogExtra log_extra;
  const auto& data1 = experiments_cache.GetData(empty_kwargs, log_extra);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
  ASSERT_EQ(data1[0].value.asInt(), 9875);
}

TEST(ExperimentsCache, TestRemoval) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  UpdateCacheFromFile(experiments_cache, "removal_01.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 1);
  LogExtra log_extra;
  const auto& data1 = experiments_cache.GetData(
      {{"version", models::ApplicationVersion{"9.8.7"}},
       {"application", models::applications::Taximeter}},
      log_extra);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));

  UpdateCacheFromFile(experiments_cache, "removal_02.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 2);
  const auto& data2 = experiments_cache.GetData(
      {{"version", models::ApplicationVersion{"9.8.7"}},
       {"application", models::applications::Taximeter}},
      log_extra);
  ASSERT_EQ(data2.size(), static_cast<size_t>(0));
}

//тест проверяющий, что в кэш загружается валидный json и проверяется логика по
// kwargs
TEST(ExperimentsCache, LoadOnce) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  UpdateCacheFromFile(experiments_cache, "load_once_updates.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4426);
  LogExtra log_extra;

  ASSERT_EQ(experiments_cache.GetData(empty_kwargs, log_extra).size(),
            static_cast<size_t>(0));
  const auto& data1 = experiments_cache.GetData(
      {{"zone", std::string{"msk"}},
       {"version", models::ApplicationVersion{"9.8.7"}},
       {"application", models::applications::Iphone}},
      log_extra);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));
  ASSERT_EQ(data1[0].value.asInt(), 100);
  const auto& data2 = experiments_cache.GetData(
      {{"zone", std::string{"spb"}},
       {"version", models::ApplicationVersion{"9.8.7"}},
       {"application", models::applications::Iphone}},
      log_extra);
  ASSERT_EQ(data2.size(), static_cast<size_t>(1));
  ASSERT_EQ(data2[0].value.asInt(), 100);
  const auto& data3 = experiments_cache.GetData(
      {{"zone", std::string{"izhevsk"}},
       {"version", models::ApplicationVersion{"9.8.7"}},
       {"application", models::applications::Iphone}},
      log_extra);
  ASSERT_EQ(data3.size(), static_cast<size_t>(1));
  ASSERT_EQ(data3[0].value.asInt(), 50);
}

//тест в котором в одном из экспериментов меняются приоритеты clause'ов (их
//порядок) и за счет этого - один запрос после изменения возвращает другой
//результат
TEST(ExperimentsCache, ChangePriority) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "change_priority_first_updates.json");
  exp3::Kwargs kwargs = {{"zone", std::string{"msk"}},
                         {"version", models::ApplicationVersion{"9.8.7"}},
                         {"application", models::applications::Iphone}};
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4426);
  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra)[0].value.asInt(), 100);
  UpdateCacheFromFile(experiments_cache, "change_priority_second_updates.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4427);
  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra)[0].value.asInt(), 50);
}

//один из экспериментов выключается, проверка, что запрос ничего не возвращает,
//если enabled == false
TEST(ExperimentsCache, RemoveOne) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "remove_one_first_updates.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4426);
  exp3::Kwargs kwargs = {{"zone", std::string{"msk"}},
                         {"version", models::ApplicationVersion{"9.8.7"}},
                         {"application", models::applications::Iphone}};
  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra).size(),
            static_cast<size_t>(1));
  UpdateCacheFromFile(experiments_cache, "remove_one_second_updates.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4427);
  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra).size(),
            static_cast<size_t>(0));
}

//тест, который проверяет, что ничего не изменится, если придет апдейт с более
//старой версией
TEST(ExperimentsCache, UpdateWithOlderVersion) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "older_version_first_updates.json");
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4426);
  exp3::Kwargs kwargs = {{"zone", std::string{"msk"}},
                         {"version", models::ApplicationVersion{"9.8.7"}},
                         {"application", models::applications::Iphone}};
  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra)[0].value.asInt(), 100);
  UpdateCacheFromFile(experiments_cache, "older_version_second_updates.json");
  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra)[0].value.asInt(), 100);
  ASSERT_EQ(experiments_cache.GetLastVersion(), 4426);
}

TEST(ExperimentsCache, ContainsPredicate) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "contains_predicates_updates.json");
  exp3::Kwargs kwargs = {{"version", models::ApplicationVersion{"9.8.7"}},
                         {"application", models::applications::Iphone}};
  kwargs["tags"] = std::unordered_set<std::string>{"male"};
  ASSERT_EQ(GetExperimentResultByName(
                experiments_cache.GetData(kwargs, log_extra), "CONTAINS_CONFIG")
                ->value.asInt(),
            1);
  kwargs["tags"] = std::unordered_set<std::string>{"female"};
  ASSERT_EQ(GetExperimentResultByName(
                experiments_cache.GetData(kwargs, log_extra), "CONTAINS_CONFIG")
                ->value.asInt(),
            0);
  kwargs["tags"] = std::unordered_set<std::string>{"other"};
  ASSERT_EQ(GetExperimentResultByName(
                experiments_cache.GetData(kwargs, log_extra), "CONTAINS_CONFIG")
                ->value.asInt(),
            0);
  ASSERT_FALSE(GetExperimentResultByName(
      experiments_cache.GetData(empty_kwargs, log_extra), "CONTAINS_CONFIG"));
  kwargs["tags"] = std::unordered_set<std::int64_t>{123};
  ASSERT_EQ(
      GetExperimentResultByName(experiments_cache.GetData(kwargs, log_extra),
                                "CONTAINS_INT_CONFIG")
          ->value.asInt(),
      1);
  kwargs["tags"] = std::unordered_set<std::int64_t>{1};
  ASSERT_EQ(
      GetExperimentResultByName(experiments_cache.GetData(kwargs, log_extra),
                                "CONTAINS_INT_CONFIG")
          ->value.asInt(),
      0);
  kwargs["tags"] = std::unordered_set<std::int64_t>{};
  ASSERT_EQ(
      GetExperimentResultByName(experiments_cache.GetData(kwargs, log_extra),
                                "CONTAINS_INT_CONFIG")
          ->value.asInt(),
      0);
}

TEST(ExperimentsCache, AllOfPredicate) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "all_of_predicates_updates.json");
  exp3::Kwargs kwargs = {
      {"version", models::ApplicationVersion{"9.8.7"}},
      {"application", models::applications::Iphone},

  };
  kwargs["phone_id"] = static_cast<std::int64_t>(1);
  kwargs["zone"] = std::string("msk");

  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra).size(),
            static_cast<size_t>(1));

  kwargs.erase("zone");
  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra).size(),
            static_cast<size_t>(0));

  kwargs["zone"] = std::string("spb");
  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra).size(),
            static_cast<size_t>(0));

  kwargs["zone"] = std::string("msk");
  kwargs.erase("phone_id");
  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra).size(),
            static_cast<size_t>(0));
}

TEST(ExperimentsCache, AnyOfPredicate) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "any_of_predicates_updates.json");
  exp3::Kwargs kwargs = {
      {"version", models::ApplicationVersion{"9.8.7"}},
      {"application", models::applications::Iphone},

  };

  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra).size(),
            static_cast<size_t>(0));

  kwargs["phone_id"] = static_cast<std::int64_t>(1);
  kwargs["zone"] = std::string("msk");

  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra).size(),
            static_cast<size_t>(1));
  kwargs.erase("phone_id");
  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra).size(),
            static_cast<size_t>(1));

  kwargs["phone_id"] = static_cast<std::int64_t>(1);
  kwargs["zone"] = std::string("spb");
  ASSERT_EQ(experiments_cache.GetData(kwargs, log_extra).size(),
            static_cast<size_t>(1));
}

TEST(ExperimentsCache, Sha1Predicate) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "sha1_predicates_updates.json");
  std::vector<std::string> user_ids;
  for (int i = 0; i < 100; ++i) {
    user_ids.emplace_back(std::to_string(i));
  }

  std::unordered_map<int, int> stat;
  for (const auto& user_id : user_ids) {
    int group_id = (*GetExperimentResultByName(
                        experiments_cache.GetData(
                            {{"user_id", user_id},
                             {"version", models::ApplicationVersion{"9.8.7"}},
                             {"application", models::applications::Iphone}},
                            log_extra),
                        "GROUPS"))
                       .value.asInt();

    auto it = stat.find(group_id);
    if (it == stat.end()) {
      stat[group_id] = 0;
    }
    stat[group_id] += 1;
  }

  ASSERT_EQ(stat.find(0), stat.end());
}

TEST(ExperimentsCache, Sha1PredicateWithRoundUp) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "sha1_round_up_updates.json");
  std::vector<std::int64_t> timestamps;
  const std::int64_t count_groups = 2;
  for (std::int64_t i = 0; i < count_groups * 60; ++i) {
    timestamps.emplace_back(i);
  }

  std::unordered_map<int, int> stat;
  for (const std::int64_t timestamp : timestamps) {
    int group_id = (*GetExperimentResultByName(
                        experiments_cache.GetData(
                            {{"timestamp", timestamp},
                             {"version", models::ApplicationVersion{"9.8.7"}},
                             {"application", models::applications::Iphone}},
                            log_extra),
                        "GROUPS"))
                       .value.asInt();

    auto it = stat.find(group_id);
    if (it == stat.end()) {
      stat[group_id] = 0;
    }
    stat[group_id] += 1;
  }

  ASSERT_EQ(stat.size(), static_cast<size_t>(count_groups));
  ASSERT_EQ(stat.find(0), stat.end());
}

TEST(ExperimentsCache, ConsumerKwarg) {
  exp3::ClientsCache consumer1_cache{
      "consumer1", "", exp3::ExperimentType::kExperiment, {}};
  exp3::ClientsCache consumer2_cache{
      "consumer2", "", exp3::ExperimentType::kExperiment, {}};

  UpdateCacheFromFile(consumer1_cache, "consumer_kwarg.json");
  UpdateCacheFromFile(consumer2_cache, "consumer_kwarg.json");

  exp3::Kwargs kwargs;
  LogExtra log_extra;

  auto result1 = consumer1_cache.GetData(kwargs, log_extra);
  ASSERT_EQ(1u, result1.size());

  auto result2 = consumer2_cache.GetData(kwargs, log_extra);
  ASSERT_EQ(0u, result2.size());
}

TEST(ExperimentsCache, VersionRanges) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  LogExtra log_extra;
  UpdateCacheFromFile(experiments_cache, "version_ranges.json");
  ASSERT_EQ(experiments_cache.Size(), static_cast<size_t>(1));

  TestKwargsBuilder builder1;
  builder1.UpdateApplication("iphone");
  builder1.UpdateVersion(models::ApplicationVersion("1.0.0"));
  const auto& data1 = experiments_cache.GetData(builder1, log_extra);
  ASSERT_EQ(data1.size(), static_cast<size_t>(1));

  TestKwargsBuilder builder2;
  builder1.UpdateApplication("iphone");
  builder1.UpdateVersion(models::ApplicationVersion("5.0.0"));
  const auto& data2 = experiments_cache.GetData(builder2, log_extra);
  ASSERT_TRUE(data2.empty());
}

TEST(ExperimentsCache, DisabledClause) {
  exp3::ClientsCache experiments_cache = EmptyCache();
  UpdateCacheFromFile(experiments_cache, "disabled_clause.json");
  TestKwargsBuilder builder;
  auto result = experiments_cache.GetByName("disabled_clause_exp", builder, {});

  ASSERT_TRUE(result.is_initialized());
  ASSERT_EQ(experiments3::formats::json::Value(result->value).As<std::string>(),
            "value_enabled_clause");
}
