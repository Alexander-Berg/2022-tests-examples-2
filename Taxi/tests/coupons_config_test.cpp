#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include "config/coupons_config.hpp"

TEST(TestCouponsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& coupons_config = config.Get<config::Coupons>();

  ASSERT_EQ(coupons_config.timeout_ms.Get(), 2000u);
  ASSERT_EQ(coupons_config.retries.Get(), 3);
}
