#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/fixed_price_params.hpp>

TEST(TestFixedPriceParams, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& fixed_price_params = config.Get<config::FixedPriceParams>();
  ASSERT_FALSE(fixed_price_params.receipt_show_meters);
}
