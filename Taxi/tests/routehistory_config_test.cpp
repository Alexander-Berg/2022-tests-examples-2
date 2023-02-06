#include <gtest/gtest.h>
#include <common/test_config.hpp>
#include <config/config.hpp>
#include "clients/routehistory/config.hpp"

TEST(RouteHistory, Config) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);

  const auto& qos =
      config::GetClientQos<clients::routehistory::Config>(config, "something");
  EXPECT_EQ(qos.attempts, 3);
  EXPECT_EQ(qos.timeout_ms, std::chrono::milliseconds(200));
}
