#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "config/driver_weariness_client_config.hpp"

TEST(TestDriverWearinessClientConfig, FallbackConfig) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::DriverWearinessClientConfig>();

  ASSERT_EQ(test_config.driver_weariness_backend_url(),
            "http://driver-weariness.taxi.yandex.net");
  ASSERT_FALSE(test_config.driver_weariness_service_enabled);
  ASSERT_TRUE(test_config.driver_weariness_consumers().empty());

  const auto& requests_settings =
      test_config.driver_weariness_requests_settings;
  ASSERT_EQ(requests_settings().size(), 3u);
  ASSERT_EQ(requests_settings["some_handler"].timeout_ms.count(), 100u);
  ASSERT_EQ(requests_settings["some_handler"].retries, 3);
  ASSERT_EQ(requests_settings["/v1/tired-drivers"].timeout_ms.count(), 200u);
  ASSERT_EQ(requests_settings["/v1/driver-weariness"].retries, 2);
}
