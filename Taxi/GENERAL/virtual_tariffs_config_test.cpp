#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "virtual_tariffs_config.hpp"

TEST(TestVirtualTariffsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::VirtualTariffs& vt_config =
      config.Get<config::VirtualTariffs>();

  ASSERT_EQ(vt_config.enabled, false);
  ASSERT_EQ(vt_config.virtual_tariffs_handlers.Get().timeout_ms.count(), 200);
  ASSERT_EQ(vt_config.virtual_tariffs_handlers.Get().retries, 1u);
}
