#include "match_orders_timeout.hpp"

#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

TEST(BulkMatchOrdersDriversTimeout, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& timeout_config =
      config.Get<config::reposition::BulkMatchOrdersDriversTimeout>()();
  ASSERT_EQ(std::chrono::milliseconds(200), timeout_config);
}
