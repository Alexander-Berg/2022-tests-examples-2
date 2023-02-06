#include <gtest/gtest.h>

#include "endpoints/full/plugins/brandings/subplugins/brandings_discount_badge.hpp"

#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context_mock_test.hpp>

#include <experiments3/discount_badge_brandings.hpp>

namespace routestats::full::brandings {

namespace {

const std::string_view kDefaultBrandingInfo(R"({
  "enabled": true
})");

core::ExpMappedData MockConfigs3() {
  core::ExpMappedData config;
  using BrandingExp = experiments3::DiscountBadgeBrandings;

  config[BrandingExp::kName] = {
      BrandingExp::kName, formats::json::FromString(kDefaultBrandingInfo), {}};

  return config;
}

full::ContextData PrepareDefaultContext(const core::ExpMappedData& cfg_data) {
  full::ContextData context = test::full::GetDefaultContext();

  context.experiments = {{core::ExpMappedData()},
                         {{cfg_data}}};  // context.experiments = {{{exp_data}},
                                         // {core::ExpMappedData()}};

  return context;
}

}  // namespace

TEST(TestBrandingsDiscountBadgePlugin, HappyPath) {
  BrandingsDiscountBadgePlugin plugin;
  const auto cfg_data = MockConfigs3();
  auto plugin_ctx = PrepareDefaultContext(cfg_data);

  std::vector<core::ServiceLevel> service_levels;

  std::vector<std::string> service_levels_classes{"econom", "ultima"};

  for (const auto& sl : service_levels_classes) {
    core::ServiceLevel service_level;

    service_level.final_price = core::Decimal(500);
    service_level.internal_original_price = core::Decimal(1001);
    service_level.class_ = sl;

    service_levels.push_back(service_level);
  }

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  for (const auto& sl : service_levels_classes) {
    const auto brandings = plugin.GetBrandings(sl);
    ASSERT_EQ(brandings.size(), 1);
    ASSERT_EQ(brandings[0].type, "discount_badge");
    ASSERT_EQ(brandings[0].value, "-50%");
  }
}

TEST(TestBrandingsDiscountBadgePlugin, NoDiscount) {
  BrandingsDiscountBadgePlugin plugin;
  const auto exp_data = MockConfigs3();
  auto plugin_ctx = PrepareDefaultContext(exp_data);

  core::ServiceLevel service_level;
  service_level.final_price = core::Decimal(500);
  service_level.internal_original_price = core::Decimal(500);
  service_level.class_ = "econom";

  std::vector<core::ServiceLevel> service_levels;
  service_levels.push_back(service_level);

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  const auto brandings = plugin.GetBrandings("econom");
  ASSERT_EQ(brandings.size(), 0);
}

TEST(TestBrandingsDiscountBadgePlugin, ZeroPercentDiscount) {
  BrandingsDiscountBadgePlugin plugin;
  const auto exp_data = MockConfigs3();
  auto plugin_ctx = PrepareDefaultContext(exp_data);

  core::ServiceLevel service_level;
  service_level.final_price = core::Decimal(100);
  service_level.internal_original_price = core::Decimal(101);
  service_level.class_ = "econom";

  std::vector<core::ServiceLevel> service_levels;
  service_levels.push_back(service_level);

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  const auto brandings = plugin.GetBrandings("econom");
  ASSERT_EQ(brandings.size(), 0);
}

TEST(TestBrandingsDiscountBadgePlugin, RoundPolicy) {
  BrandingsDiscountBadgePlugin plugin;
  const auto exp_data = MockConfigs3();
  auto plugin_ctx = PrepareDefaultContext(exp_data);

  core::ServiceLevel service_level;
  service_level.final_price = core::Decimal(295);
  service_level.internal_original_price = core::Decimal(300);
  service_level.class_ = "econom";

  std::vector<core::ServiceLevel> service_levels;
  service_levels.push_back(service_level);

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  const auto brandings = plugin.GetBrandings("econom");
  ASSERT_EQ(brandings.size(), 1);
  ASSERT_EQ(brandings[0].value, "-1%");
}

}  // namespace routestats::full::brandings
