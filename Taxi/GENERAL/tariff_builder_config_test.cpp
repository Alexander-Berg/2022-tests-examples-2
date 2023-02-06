#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/tariff_builder_config.hpp>

TEST(TestTariffBuilderConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& tariff_builder_config = config.Get<config::TariffBuilderConfig>();
  ASSERT_TRUE(tariff_builder_config.relative_prices_enabled.Get());
}
