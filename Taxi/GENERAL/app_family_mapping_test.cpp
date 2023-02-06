#include <gtest/gtest.h>

#include <tuple>

#include <common/test_config.hpp>
#include <config/app_family_mapping.hpp>
#include <config/config.hpp>
#include <utils/taximeter_application.hpp>

TEST(TestAppFamilyMapping, GetAppFamilyFromBrand) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& mapping = config.Get<config::AppFamilyMapping>();

  using TestCase = std::tuple<std::string, std::string>;
  const std::vector<TestCase> test_cases = {
      {"yandex", "taximeter"}, {"yango", "taximeter"}, {"az", "taximeter"},
      {"uber", "uberdriver"},  {"vezet", "vezet"},     {"rida", "rida"}};

  for (const auto test_case : test_cases) {
    const auto [brand, expect_app_family] = test_case;
    ASSERT_EQ(mapping.GetAppFamilyFromBrand(brand), expect_app_family);
  }
}

TEST(TestAppFamilyMapping, GetAppFamilyFromApp) {
  const auto& docs_map = config::DocsMapForTest();
  const auto& config = config::Config(docs_map);
  const auto& mapping = config.Get<config::AppFamilyMapping>();

  using TestCase = std::tuple<std::string, std::string>;
  const std::vector<TestCase> test_cases = {
      {"Taximeter 10.00 (1234)", "taximeter"},
      {"Taximeter-Yango 10.00 (1234)", "taximeter"},
      {"Taximeter-AZ 10.00 (1234)", "taximeter"},
      {"Taximeter-beta 10.00 (1234)", "taximeter"},
      {"Taximeter-UBER 10.00 (1234)", "uberdriver"},
      {"Taximeter-Vezet 10.00 (1234)", "vezet"},
      {"Taximeter-RIDA 12.00", "rida"},
  };

  for (const auto test_case : test_cases) {
    const auto [user_agent, expect_app_family] = test_case;
    const auto app = models::TaximeterApp::FromUserAgent(user_agent);
    ASSERT_EQ(mapping.GetAppFamily(app), expect_app_family);
  }
}
