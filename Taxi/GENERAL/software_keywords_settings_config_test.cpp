#include <gtest/gtest.h>

#include <common/test_config.hpp>
#include <config/config.hpp>
#include <config/software_keywords_settings_config.hpp>

TEST(TestSoftwareKeywordSettingsConfig, Fallback) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const config::SoftwareKeywordSettings& software_keywords_settings_config =
      config.Get<config::SoftwareKeywordSettings>();

  std::vector<std::string> allowed = software_keywords_settings_config.allowed;
  std::vector<std::string> forbidden =
      software_keywords_settings_config.forbidden;

  ASSERT_EQ(allowed.size(), 6u);
  ASSERT_EQ(forbidden.size(), 87u);
}
