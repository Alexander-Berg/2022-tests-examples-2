#include <endpoints/full/plugins/brandings/subplugins/summary_scenarios.hpp>
#include <experiments3/summary_scenarios.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/full/plugins/brandings/summary_scenarios/utils_test.hpp>

#include <userver/utest/utest.hpp>

#include <userver/formats/json/string_builder.hpp>

namespace routestats::full::brandings {

namespace {
const core::Surge surge{core::Decimal::FromBiased(130, 2)};
const core::Discount discount{core::Decimal::FromBiased(30, 2), ""};
const core::Coupon coupon{core::CouponAppliedType::kLimit,
                          core::Decimal::FromBiased(100, 9)};

std::vector<core::ServiceLevel> PrepareServiceLevels() {
  auto econom = test::MockDefaultServiceLevel("econom");
  econom.final_price = std::nullopt;

  auto comfort = test::MockDefaultServiceLevel("comfort");
  comfort.eta = std::nullopt;
  comfort.final_price = decimal64::Decimal<4>{1000};

  auto business = test::MockDefaultServiceLevel("business");
  business.eta = std::nullopt;
  business.coupon = coupon;

  auto vip = test::MockDefaultServiceLevel("vip");
  vip.eta = std::nullopt;
  vip.final_price = decimal64::Decimal<4>{2000};
  vip.surge = surge;

  auto ultima = test::MockDefaultServiceLevel("ultima");
  ultima.eta = std::nullopt;
  ultima.final_price = decimal64::Decimal<4>{2000};
  ultima.discount = discount;
  return {std::move(econom), std::move(comfort), std::move(business),
          std::move(vip), std::move(ultima)};
}
}  // namespace

TEST(SummaryScenariosPlugin, HappyPath) {
  SummaryScenariosPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = PrepareContext({"cheapest"});

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
  ASSERT_EQ(plugin.GetBrandings("comfort").size(), 0);

  const auto& business_brandings = plugin.GetBrandings("business");
  ASSERT_EQ(business_brandings.size(), 1);

  const auto& branding = business_brandings.front();
  ASSERT_EQ(branding.type, "modifier_field");
  ASSERT_FALSE(branding.attributed_info->show_modes.empty());

  std::vector<routestats::service_level::ShowMode> expected_show_modes = {
      routestats::service_level::ShowMode::kSelected,
      routestats::service_level::ShowMode::kUnselected,
  };
  ASSERT_EQ(branding.attributed_info->show_modes, expected_show_modes);
  ASSERT_EQ(branding.attributed_info->attributed_text.items.size(), 1);

  const auto text_property = std::get<extended_template::ATTextProperty>(
      branding.attributed_info->attributed_text.items[0]);
  ASSERT_EQ(text_property.text, "client_messages##cheapest##");
}

TEST(SummaryScenariosPlugin, TestPriority) {
  SummaryScenariosPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  {
    auto plugin_ctx =
        PrepareContext({"cheapest", "fastest", "coupon", "discount", "surge"});
    plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                                service_levels);
    ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("comfort").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("business").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("ultima").size(), 0);

    const auto& brandings = plugin.GetBrandings("vip");
    ASSERT_EQ(brandings.size(), 1);

    const auto& branding = brandings.front();
    const auto text_property = std::get<extended_template::ATTextProperty>(
        branding.attributed_info->attributed_text.items[0]);
    ASSERT_EQ(text_property.text, "client_messages##surge##");
  }
  {
    auto plugin_ctx =
        PrepareContext({"cheapest", "fastest", "coupon", "discount"});
    plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                                service_levels);
    ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("comfort").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("vip").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("ultima").size(), 0);

    const auto& brandings = plugin.GetBrandings("business");
    ASSERT_EQ(brandings.size(), 1);

    const auto& branding = brandings.front();
    const auto text_property = std::get<extended_template::ATTextProperty>(
        branding.attributed_info->attributed_text.items[0]);
    ASSERT_EQ(text_property.text, "client_messages##coupon##");
  }
  {
    auto plugin_ctx = PrepareContext({"cheapest", "fastest", "discount"});
    plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                                service_levels);
    ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("comfort").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("business").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("vip").size(), 0);

    const auto& brandings = plugin.GetBrandings("ultima");
    ASSERT_EQ(brandings.size(), 1);

    const auto& branding = brandings.front();
    const auto text_property = std::get<extended_template::ATTextProperty>(
        branding.attributed_info->attributed_text.items[0]);
    ASSERT_EQ(text_property.text, "client_messages##discount##");
  }
  {
    auto plugin_ctx = PrepareContext({"cheapest", "fastest"});
    plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                                service_levels);
    ASSERT_EQ(plugin.GetBrandings("business").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("comfort").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("vip").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("ultima").size(), 0);

    const auto& brandings = plugin.GetBrandings("econom");
    ASSERT_EQ(brandings.size(), 1);

    const auto& branding = brandings.front();
    const auto text_property = std::get<extended_template::ATTextProperty>(
        branding.attributed_info->attributed_text.items[0]);
    ASSERT_EQ(text_property.text, "client_messages##fastest##");
  }
  {
    auto plugin_ctx = PrepareContext({"cheapest"});
    plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                                service_levels);
    ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("comfort").size(), 0);
    ASSERT_EQ(plugin.GetBrandings("vip").size(), 0);

    const auto& brandings = plugin.GetBrandings("business");
    ASSERT_EQ(brandings.size(), 1);

    const auto& branding = brandings.front();
    const auto text_property = std::get<extended_template::ATTextProperty>(
        branding.attributed_info->attributed_text.items[0]);
    ASSERT_EQ(text_property.text, "client_messages##cheapest##");
  }
}

TEST(SummaryScenariosPlugin, TestSupportedClasses) {
  SummaryScenariosPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = PrepareContext({"cheapest", "fastest"}, {"comfort"});

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);
  ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
  ASSERT_EQ(plugin.GetBrandings("comfort").size(), 1);
  ASSERT_EQ(plugin.GetBrandings("business").size(), 0);

  const auto& comfort_brandings = plugin.GetBrandings("comfort");
  const auto& branding = comfort_brandings.front();
  const auto text_property = std::get<extended_template::ATTextProperty>(
      branding.attributed_info->attributed_text.items[0]);
  ASSERT_EQ(text_property.text, "client_messages##cheapest##");
}

}  // namespace routestats::full::brandings
