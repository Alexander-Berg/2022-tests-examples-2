#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/fleet_api_get_grants_mode.hpp>

TEST(TestGetGrantsModeConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::FleetApiGetGrants>();
  ASSERT_EQ(config::FleetApiGetGrants::GetGrantsMode::kTaximeter,
            test_config.get_grants_mode);
}
