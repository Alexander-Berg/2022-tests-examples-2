#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/taximeter_config.hpp>

TEST(TestTaximeterConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::Taximeter& taximeter_config = config.Get<config::Taximeter>();
  ASSERT_FALSE(taximeter_config.use_subventions_for_drivercost.Get());
}
