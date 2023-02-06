#include "config.hpp"

#include <gtest/gtest.h>
#include <common/test_config.hpp>

struct TestConfigStruct {
  config::Value<int> test_value;

  TestConfigStruct(const config::DocsMap& docs_map)
      : test_value("DRIVER_PROTOCOL_TIMEOUT_MS", docs_map) {}
};

TEST(Config, Register) {
  config::DocsMap docs_map = config::DocsMapForTest();
  docs_map.Override<int>("DRIVER_PROTOCOL_TIMEOUT_MS", 42);
  config::Config config(docs_map);

  ASSERT_EQ(config.Get<TestConfigStruct>().test_value, 42);
}

TEST(Config, RequestedConfigs) {
  config::DocsMap docs_map = config::DocsMapForTest();
  docs_map.Override<int>("DRIVER_PROTOCOL_TIMEOUT_MS", 42);
  config::Config config(docs_map);

  ASSERT_EQ(config.Get<TestConfigStruct>().test_value, 42);

  auto requested_configs = docs_map.GetRequestedConfigs();

  ASSERT_NE(std::find(requested_configs.begin(), requested_configs.end(),
                      "DRIVER_PROTOCOL_TIMEOUT_MS"),
            requested_configs.end());
}
