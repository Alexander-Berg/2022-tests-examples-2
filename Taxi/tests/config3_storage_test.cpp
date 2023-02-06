#include <userver/fs/blocking/read.hpp>
#include <userver/logging/log.hpp>
#include <userver/utest/utest.hpp>

#include <testing/source_path.hpp>

#include "exp3_light_client.hpp"
#include "models/config3_storage.hpp"

namespace cfg = configs_from_configs3;

namespace {
const std::string kFilesDir =
    utils::CurrentSourcePath("src/tests/static/config3_storage_test/");

dynamic_config::DocsMap ReadFallbackValues() {
  auto fallback_config_contents =
      fs::blocking::ReadFileContents(kFilesDir + "fallback_configs.json");
  dynamic_config::DocsMap fallback_config;
  fallback_config.Parse(fallback_config_contents, false);
  return fallback_config;
}

formats::json::Value ConfigValue(int i) {
  formats::json::ValueBuilder builder;
  builder["value"] = i;
  return builder.ExtractValue();
}

std::vector<formats::json::Value> ReadTestConfigs(
    const std::string& filename = "test_configs.json") {
  auto configs = formats::json::blocking::FromFile(kFilesDir + filename);
  return configs["configs"].As<std::vector<formats::json::Value>>();
}

cfg::Config3Storage MakeConfigStorage() {
  return cfg::Config3Storage(ReadFallbackValues(), "test-service", "test-host");
}

formats::json::Value IncreaseConfigValue(formats::json::Value config,
                                         int value) {
  formats::json::ValueBuilder builder(config);
  builder["default_value"]["value"] =
      config["default_value"]["value"].As<int>() + value;
  builder["last_modified_at"] = config["last_modified_at"].As<int>() + 3;
  return builder.ExtractValue();
}

void CheckSnapshot(std::unordered_map<std::string, int> values,
                   const dynamic_config::DocsMap& snapshot) {
  ASSERT_EQ(snapshot.Size(), 3);
  for (const auto& [name, value] : values) {
    ASSERT_EQ(snapshot.Get(name), ConfigValue(value));
  }
}

}  // namespace

UTEST(Config3Storage, FallbackValuesOnly) {
  auto storage = MakeConfigStorage();

  ASSERT_FALSE(storage.UpdateValues("test_consumer", {}, true));
  auto snapshot1 = storage.GetSnapshot();
  ASSERT_EQ(snapshot1.Get("TEST_CONFIG1"), ConfigValue(1));
  ASSERT_EQ(snapshot1.Get("TEST_CONFIG2"), ConfigValue(2));
  ASSERT_EQ(snapshot1.Get("TEST_CONFIG3"), ConfigValue(3));

  ASSERT_FALSE(storage.UpdateValues("test_consumer", {}, true));
  auto snapshot2 = storage.GetSnapshot();
  ASSERT_TRUE(snapshot1.AreContentsEqual(snapshot2));
}

UTEST(Config3Storage, FullUpdate) {
  auto configs = ReadTestConfigs();

  auto storage = MakeConfigStorage();
  ASSERT_TRUE(storage.UpdateValues("test_consumer", configs, true));
  auto snapshot1 = storage.GetSnapshot();
  CheckSnapshot({{"TEST_CONFIG1", 4}, {"TEST_CONFIG2", 5}, {"TEST_CONFIG3", 6}},
                snapshot1);

  ASSERT_TRUE(storage.UpdateValues("test_consumer", configs, true));
  auto snapshot2 = storage.GetSnapshot();
  ASSERT_TRUE(snapshot1.AreContentsEqual(snapshot2));
}

UTEST(Config3Storage, IncrementalUpdate) {
  auto configs = ReadTestConfigs();

  auto storage = MakeConfigStorage();
  ASSERT_TRUE(storage.UpdateValues("test_consumer", configs, true));
  auto snapshot = storage.GetSnapshot();
  CheckSnapshot({{"TEST_CONFIG1", 4}, {"TEST_CONFIG2", 5}, {"TEST_CONFIG3", 6}},
                snapshot);
  ASSERT_EQ(storage.GetVersion("test_consumer"), 634649);

  std::vector<formats::json::Value> new_configs;
  for (const auto& config : configs) {
    new_configs.push_back(IncreaseConfigValue(config, 3));
  }

  ASSERT_TRUE(storage.UpdateValues("test_consumer", new_configs, false));
  snapshot = storage.GetSnapshot();
  CheckSnapshot({{"TEST_CONFIG1", 7}, {"TEST_CONFIG2", 8}, {"TEST_CONFIG3", 9}},
                snapshot);
  ASSERT_EQ(storage.GetVersion("test_consumer"), 634652);

  // modify and update one config, while the others stay the same
  auto config = IncreaseConfigValue(new_configs[2], 3);
  ASSERT_TRUE(storage.UpdateValues("test_consumer", {config}, false));
  snapshot = storage.GetSnapshot();
  CheckSnapshot(
      {{"TEST_CONFIG1", 7}, {"TEST_CONFIG2", 8}, {"TEST_CONFIG3", 12}},
      snapshot);
  ASSERT_EQ(storage.GetVersion("test_consumer"), 634655);

  // full update clears the cache
  ASSERT_TRUE(storage.UpdateValues("test_consumer", new_configs, true));
  snapshot = storage.GetSnapshot();
  CheckSnapshot({{"TEST_CONFIG1", 7}, {"TEST_CONFIG2", 8}, {"TEST_CONFIG3", 9}},
                snapshot);
  ASSERT_EQ(storage.GetVersion("test_consumer"), 634652);
}

UTEST(Config3Storage, DefaultKwargsMatch) {
  auto test_configs = ReadTestConfigs("test_configs_with_conditions.json");

  auto storage1 =
      cfg::Config3Storage(ReadFallbackValues(), "test-service1", "test-host1");
  ASSERT_TRUE(storage1.UpdateValues("test_consumer", test_configs, true));
  CheckSnapshot(
      {{"TEST_CONFIG1", 444}, {"TEST_CONFIG2", 5}, {"TEST_CONFIG3", 6}},
      storage1.GetSnapshot());

  auto storage2 =
      cfg::Config3Storage(ReadFallbackValues(), "test-service2", "test-host2");
  ASSERT_TRUE(storage2.UpdateValues("test_consumer", test_configs, true));
  CheckSnapshot(
      {{"TEST_CONFIG1", 4}, {"TEST_CONFIG2", 555}, {"TEST_CONFIG3", 6}},
      storage2.GetSnapshot());
}

UTEST(Config3Storage, MultipleConsumersFullUpdate) {
  auto test_configs =
      ReadTestConfigs("test_configs_with_different_consumers.json");

  auto storage =
      cfg::Config3Storage(ReadFallbackValues(), "test-service", "test-host");
  ASSERT_TRUE(storage.UpdateValues("test_consumer1", {test_configs[0]}, true));
  CheckSnapshot({{"TEST_CONFIG1", 4}, {"TEST_CONFIG2", 2}, {"TEST_CONFIG3", 3}},
                storage.GetSnapshot());
  ASSERT_EQ(storage.GetVersion("test_consumer1"), 634647);
  ASSERT_EQ(storage.GetVersion("test_consumer2"), -1);
  ASSERT_EQ(storage.GetVersion("test_consumer3"), -1);

  ASSERT_TRUE(storage.UpdateValues("test_consumer2", {test_configs[1]}, true));
  CheckSnapshot({{"TEST_CONFIG1", 4}, {"TEST_CONFIG2", 5}, {"TEST_CONFIG3", 3}},
                storage.GetSnapshot());
  ASSERT_EQ(storage.GetVersion("test_consumer1"), 634647);
  ASSERT_EQ(storage.GetVersion("test_consumer2"), 634648);
  ASSERT_EQ(storage.GetVersion("test_consumer3"), -1);

  ASSERT_TRUE(storage.UpdateValues("test_consumer3", {test_configs[2]}, true));
  CheckSnapshot({{"TEST_CONFIG1", 4}, {"TEST_CONFIG2", 5}, {"TEST_CONFIG3", 6}},
                storage.GetSnapshot());
  ASSERT_EQ(storage.GetVersion("test_consumer1"), 634647);
  ASSERT_EQ(storage.GetVersion("test_consumer2"), 634648);
  ASSERT_EQ(storage.GetVersion("test_consumer3"), 634649);
}
