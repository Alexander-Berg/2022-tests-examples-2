#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>

#include <config/modifications_without_name.hpp>

TEST(TestModificationsWithoutName, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& test_config = config.Get<config::ModificationsWithoutName>();
  ASSERT_EQ(false, test_config.enabled);
  ASSERT_EQ("--", test_config.log_default_name);
}
