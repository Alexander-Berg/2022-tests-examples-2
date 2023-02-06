#include <gtest/gtest.h>

#include <testing/taxi_config.hpp>

#include <pro_app_parser/app_family.hpp>
#include <ua_parser/taximeter_application.hpp>

#include <taxi_config/variables/TAXIMETER_BRAND_TO_APP_FAMILY_MAPPING.hpp>

namespace {
dynamic_config::StorageMock GetStorage() {
  return dynamic_config::StorageMock{
      {taxi_config::TAXIMETER_BRAND_TO_APP_FAMILY_MAPPING,
       {{
           {"yandex", "taximeter"},
           {"yango", "taximeter"},
           {"az", "taximeter"},
           {"uber", "uberdriver"},
           {"vezet", "vezet"},
           {"rida", "rida"},
           {"turla", "modus"},
       }}}};
}

}  // namespace

TEST(AppFamilyTest, FromBrandViaConfig) {
  using namespace pro_app_parser;
  const auto storage = GetStorage();
  const auto snapshot = storage.GetSnapshot();

  // 1. brand
  // 2. expect app_family
  using TestCase = std::tuple<std::string, std::string>;
  const TestCase kTestCases[] = {
      {"yandex", "taximeter"}, {"yango", "taximeter"}, {"az", "taximeter"},
      {"uber", "uberdriver"},  {"vezet", "vezet"},     {"rida", "rida"},
      {"turla", "modus"}};

  for (const auto& testCase : kTestCases) {
    const auto& [brand, expect_app_family] = testCase;

    const auto app_family = GetAppFamilyFromBrand(brand, snapshot);
    ASSERT_EQ(app_family, expect_app_family);
  }

  ASSERT_THROW(GetAppFamilyFromBrand("bad_brand", snapshot),
               AppFamilyParsingError);
}

TEST(AppFamilyTest, FromAppViaConfig) {
  using namespace pro_app_parser;
  const auto storage = GetStorage();
  const auto snapshot = storage.GetSnapshot();

  // 1. User-Agent
  // 2. expect app_family
  using TestCase = std::tuple<std::string, std::string>;
  const TestCase kTestCases[] = {{"Taximeter 9.99 (1111)", "taximeter"},
                                 {"Taximeter-YANGO 9.99 (1111)", "taximeter"},
                                 {"Taximeter-AZ 9.99 (1111)", "taximeter"},
                                 {"Taximeter-UBER 9.99 (1111)", "uberdriver"},
                                 {"Taximeter-VEZET 9.99 (1111)", "vezet"},
                                 {"Taximeter-RIDA 9.99 (1111)", "rida"},
                                 {"Taximeter-TURLA 9.99 (1111)", "modus"}};

  for (const auto& testCase : kTestCases) {
    const auto& [user_agent, expect_app_family] = testCase;

    const auto app_family = GetAppFamily(
        ua_parser::TaximeterApp::FromUserAgent(user_agent), snapshot);
    ASSERT_EQ(app_family, expect_app_family);
  }
}
