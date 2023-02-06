#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/country_vat_config.hpp>

TEST(TestCountryVatConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  auto country_vat_config = config.Get<config::CountryVatByDateConfig>();

  ASSERT_EQ(country_vat_config.country_vat_by_date.size(), 1u);
  ASSERT_EQ(country_vat_config.country_vat_by_date["rus"][0].value, 11800u);
  ASSERT_EQ(country_vat_config.country_vat_by_date["rus"][1].value, 12000u);
}
