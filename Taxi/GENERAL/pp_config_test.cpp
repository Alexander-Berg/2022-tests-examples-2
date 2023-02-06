#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include "pp_config.hpp"

TEST(TestPPClientsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::PickupPointsClientsConfig& pp_config =
      config.Get<config::PickupPointsClientsConfig>();

  ASSERT_EQ(pp_config.client_request_settings.GetMap().size(), 1u);
  ASSERT_EQ(pp_config.client_request_settings.Get("/points").retries, 3);
  ASSERT_EQ(pp_config.client_request_settings.Get("/points").timeout_ms,
            std::chrono::milliseconds{1000});
}
