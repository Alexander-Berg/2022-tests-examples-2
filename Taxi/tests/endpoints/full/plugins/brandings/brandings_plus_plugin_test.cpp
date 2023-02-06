#include <endpoints/full/plugins/brandings/subplugins/brandings_plus_promo.hpp>

#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

#include <set>

#include <userver/utest/utest.hpp>

#include <tests/context/taxi_config_mock_test.hpp>

#include <taxi_config/variables/PLUS_SUMMARY_PROMOTION_SETTING.hpp>

namespace routestats::full::brandings {

namespace {

using taxi_config::plus_summary_promotion_setting::PlusSummaryPromotionSetting;

core::ServiceLevel MockServiceLevel(
    const std::string& class_name,
    std::optional<core::Decimal> price = std::nullopt) {
  auto result = test::MockDefaultServiceLevel(class_name);
  result.final_price = price;
  return result;
}

std::vector<core::ServiceLevel> PrepareServiceLevels() {
  return std::vector<core::ServiceLevel>{
      MockServiceLevel("econom", core::Decimal{300}),
      MockServiceLevel("business", core::Decimal{400}),
      MockServiceLevel("vip", core::Decimal{500}),
      MockServiceLevel("comfortplus"),
  };
}

PlusSummaryPromotionSetting MockPromotions(
    const std::string& country, double min_price,
    const std::set<std::string> categories) {
  PlusSummaryPromotionSetting result;
  result.extra[country] = {min_price, 0.1, categories};
  return result;
}

full::ContextData PrepareContext() {
  full::ContextData context = test::full::GetDefaultContext();

  context.user.auth_context.flags.has_ya_plus = false;
  context.user.auth_context.locale = "ru";

  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::PLUS_SUMMARY_PROMOTION_SETTING,
       MockPromotions("rus", 100, {"business", "comfortplus"})},
  });

  context.taxi_configs =
      std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));

  taxi_tariffs::models::TariffSettings tariff_settings;
  client_zone_geoindex::models::Tariff tariff;
  tariff_settings.home_zone = "moscow";
  tariff_settings.country = "rus";

  models::Country country;
  country.id = "rus";
  country.currency_code = "rub";

  context.zone = core::Zone{"moscow", tariff_settings, country, tariff};
  return context;
}

}  // namespace

UTEST(TestBrandingsPlusPlugin, HappyPath) {
  BrandingsPlusPromoPlugin plugin;
  auto context = PrepareContext();
  auto plugin_ctx = test::full::MakeTopLevelContext(context);

  plugin.OnServiceLevelsReady(plugin_ctx, PrepareServiceLevels());

  auto business = plugin.GetBrandings("business");
  ASSERT_EQ(business.size(), 1);

  auto branding = business.front();
  ASSERT_EQ(branding.type, "plus_promotion");
  ASSERT_EQ(*branding.title, "routestats.brandings.plus_promo_v2.title##ru");
}

}  // namespace routestats::full::brandings
