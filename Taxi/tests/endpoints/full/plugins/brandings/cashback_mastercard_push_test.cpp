#include <gtest/gtest.h>

#include <endpoints/full/plugins/brandings/subplugins/cashback_mastercard_push.hpp>

#include <experiments3/cashback_mastercard_service_levels.hpp>
#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>

#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>

#include <taxi_config/variables/CASHBACK_MASTERCARD_DISPLAY_INFO.hpp>
#include <taxi_config/variables/DISCOUNT_DESCRIPTION_TO_TAG_MAPPING.hpp>

namespace routestats::full::brandings {

namespace {

const std::string kCashbackType = "cashback";
const std::string_view kDidscountsInfo(R"({
  "__default__": {},
  "ultima": {
    "mastercard_single_cashback": {
      "notification_title": "notification_title_key",
      "notification_subtitle": "notification_subtitle_key",
      "title": "title_key",
      "subtitle": "subtitle_key",
      "banner_id": "banner_id",
      "icon": "icon"
    }
  }
})");

formats::json::Value MakeCashbackMastercardExp(
    bool enabled, const std::vector<std::string>& classes) {
  using formats::json::ValueBuilder;

  ValueBuilder exp_builder{};
  exp_builder["enabled"] = enabled;

  exp_builder["service_levels"] = ValueBuilder(formats::common::Type::kArray);
  for (const auto& class_ : classes) {
    exp_builder["service_levels"].PushBack(class_);
  }

  return exp_builder.ExtractValue();
}

User MockUser(bool ya_plus, bool cashback_plus) {
  User user;
  user.auth_context.locale = "ru";
  user.auth_context.flags.has_ya_plus = ya_plus;
  user.auth_context.flags.has_plus_cashback = cashback_plus;
  return user;
}

core::Experiments MockExperiments(
    const std::vector<std::string>& branding_classes) {
  core::ExpMappedData experiments;
  using BrandingExp = experiments3::CashbackMastercardServiceLevels;

  experiments[BrandingExp::kName] = {
      BrandingExp::kName,
      MakeCashbackMastercardExp(true, branding_classes),
      {}};

  return {std::move(experiments)};
}

core::TaxiConfigsPtr MockConfigs() {
  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::DISCOUNT_DESCRIPTION_TO_TAG_MAPPING,
       {{{"ultima_discount_description", "mastercard_single_cashback"}}}},
      {taxi_config::CASHBACK_MASTERCARD_DISPLAY_INFO,
       formats::json::FromString(kDidscountsInfo)
           .As<dynamic_config::ValueDict<
               taxi_config::cashback_mastercard_display_info::
                   DiscountsInfo>>()},
  });
  return std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));
}

std::vector<core::ServiceLevel> MockServiceLevels(
    const std::unordered_map<std::string, std::optional<core::Discount>>&
        service_levels) {
  std::vector<core::ServiceLevel> result;

  for (const auto& [class_, discount] : service_levels) {
    core::ServiceLevel service_level;
    service_level.class_ = class_;
    service_level.discount = discount;
    result.push_back(std::move(service_level));
  }
  return result;
}

std::vector<core::ServiceLevel> PrepareServiceLevels() {
  return MockServiceLevels(
      {{"econom", std::nullopt},
       {"ultima",
        core::Discount{core::Decimal{10}, "ultima_discount_description"}}});
}

full::ContextData PrepareDefaultContext() {
  full::ContextData context = test::full::GetDefaultContext();

  context.user = MockUser(true, true);
  context.experiments.uservices_routestats_exps = MockExperiments({"ultima"});
  context.taxi_configs = MockConfigs();

  return context;
}

service_level::TariffBranding MakeCashbackBranding() {
  service_level::TariffBranding result;
  result.type = "cashback";
  result.title = "cashback_title";
  result.subtitle = "cashback_subtitle";
  result.value = "42";
  return result;
}

std::unordered_map<std::string, TariffBrandingRef> MakeBrandings(
    const std::string& type, service_level::TariffBranding& branding) {
  std::unordered_map<std::string, TariffBrandingRef> result{{type, branding}};
  return result;
}

}  // namespace

TEST(TestCashbackMastercardPushPlugin, HappyPath) {
  CashbackMastercardPushPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = PrepareDefaultContext();

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  ASSERT_EQ(plugin.GetBrandings("unknown_service").size(), 0);

  const auto& econom_brandings = plugin.GetBrandings("econom");
  ASSERT_EQ(econom_brandings.size(), 0);

  const auto& ultima_brandings = plugin.GetBrandings("ultima");
  ASSERT_EQ(ultima_brandings.size(), 1);

  const auto& branding = ultima_brandings.front();
  ASSERT_EQ(branding.type, "mastercard_cashback_notification");
  ASSERT_EQ(branding.title, "notification_title_key##ru");
  ASSERT_EQ(branding.subtitle, "notification_subtitle_key##ru");
  ASSERT_EQ(branding.action, "show_banner");
  ASSERT_EQ(branding.icon, "icon");
  ASSERT_NE(branding.extra, std::nullopt);
  ASSERT_EQ(branding.extra->banner_id, "banner_id");
}

TEST(TestCashbackMastercardPushPlugin, MissingTranslations) {
  CashbackMastercardPushPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = PrepareDefaultContext();
  plugin_ctx.rendering.translator = std::make_shared<test::TranslatorMock>(
      [](const core::Translation&,
         const std::string&) -> std::optional<std::string> {
        return std::nullopt;
      });

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  const auto& ultima_brandings = plugin.GetBrandings("ultima");
  ASSERT_EQ(ultima_brandings.size(), 0);
}

TEST(TestCashbackMastercardPushPlugin, TestNotPlusSubscriber) {
  using param = std::pair<bool, bool>;
  for (auto [ya_plus, cashback_plus] :
       {param{false, false}, param{false, true}, param{true, false}}) {
    CashbackMastercardPushPlugin plugin;
    auto service_levels = PrepareServiceLevels();
    auto plugin_ctx = PrepareDefaultContext();
    plugin_ctx.user = MockUser(ya_plus, cashback_plus);

    plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                                service_levels);

    const auto& ultima_brandings = plugin.GetBrandings("ultima");
    ASSERT_EQ(ultima_brandings.size(), 0);
  }
}

TEST(TestCashbackMastercardPushPlugin, DisabledByExp) {
  CashbackMastercardPushPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = PrepareDefaultContext();
  plugin_ctx.experiments.uservices_routestats_exps = MockExperiments({});

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  const auto& ultima_brandings = plugin.GetBrandings("ultima");
  ASSERT_EQ(ultima_brandings.size(), 0);
}

TEST(TestCashbackMastercardPushPlugin, ModifyCashbackHappyPath) {
  CashbackMastercardPushPlugin plugin;
  auto plugin_ctx = PrepareDefaultContext();

  core::ServiceLevel service_level;
  service_level.class_ = "ultima";
  service_level.discount =
      core::Discount{core::Decimal{10}, "ultima_discount_description"};

  auto cashback_branding = MakeCashbackBranding();
  auto brandings = MakeBrandings(kCashbackType, cashback_branding);
  plugin.ModifyProtocolBrandings(test::full::MakeTopLevelContext(plugin_ctx),
                                 service_level, brandings);
  ASSERT_EQ(cashback_branding.type, "cashback");
  ASSERT_EQ(cashback_branding.title, "title_key##ru");
  ASSERT_EQ(cashback_branding.subtitle, "subtitle_key##ru");
  ASSERT_EQ(cashback_branding.action, "show_banner");
  ASSERT_EQ(cashback_branding.value, "42");
  ASSERT_NE(cashback_branding.extra, std::nullopt);
  ASSERT_EQ(cashback_branding.extra->banner_id, "banner_id");
}

TEST(TestCashbackMastercardPushPlugin, OverrideDiscount) {
  CashbackMastercardPushPlugin plugin;
  auto plugin_ctx = PrepareDefaultContext();
  auto service_levels = PrepareServiceLevels();

  for (auto& level : service_levels) {
    level.discount_type = "ya_plus_mastercard";
  }

  auto extensions = plugin.ExtendServiceLevels(
      test::full::MakeTopLevelContext(plugin_ctx), service_levels);
  ASSERT_FALSE(extensions.empty());

  for (auto& level : service_levels) {
    if (extensions.count(level.class_)) {
      extensions.at(level.class_)->Apply("brandings_plugin", level);
    }
  }

  for (const auto& level : service_levels) {
    if (level.class_ == "ultima") {
      ASSERT_EQ(level.discount_type, "other");
    } else {
      ASSERT_EQ(level.discount_type, "ya_plus_mastercard");
    }
  }
}

}  // namespace routestats::full::brandings
