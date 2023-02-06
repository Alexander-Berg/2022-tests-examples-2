#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include "driver_tags_diagnostics_description.hpp"

TEST(TestDriverTagsDiagnosticsDescription, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& tag_diagnostic_cfg =
      config.Get<config::DriverTagsDiagnosticsDescription>();

  const auto& zones_info = tag_diagnostic_cfg.zones_info.GetMap();
  ASSERT_EQ(zones_info.size(), 1ul);

  const auto& default_zone_it = zones_info.find("__default__");
  ASSERT_NE(default_zone_it, zones_info.end());
  ASSERT_EQ(default_zone_it->second.GetMap().empty(), true);
}
