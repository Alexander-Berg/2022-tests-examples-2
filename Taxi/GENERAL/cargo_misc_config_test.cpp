#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "cargo_misc_config.hpp"

TEST(TestCargoMiscConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::CargoMisc& cargo_misc_config = config.Get<config::CargoMisc>();

  ASSERT_EQ(cargo_misc_config.GetQos("some/url").timeout_ms.count(), 200);
  ASSERT_EQ(cargo_misc_config.GetQos("some/url").attempts, 3);
}
