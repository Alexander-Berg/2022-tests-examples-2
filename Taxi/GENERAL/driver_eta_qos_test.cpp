#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/driver_eta_qos.hpp>

TEST(TestDriverEtaClientConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);

  const auto& qos =
      config::GetClientQos<config::DriverEtaClientQos>(config, "some_path");
  ASSERT_EQ(qos.attempts, 3);
  ASSERT_EQ(qos.timeout_ms, std::chrono::milliseconds(200));
}
