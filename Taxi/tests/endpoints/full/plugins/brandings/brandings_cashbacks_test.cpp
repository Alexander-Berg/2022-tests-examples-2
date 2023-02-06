#include <gtest/gtest.h>

#include "endpoints/full/plugins/brandings/subplugins/brandings_cashbacks.hpp"

#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context_mock_test.hpp>

#include <experiments3/cashback_brandings.hpp>
#include <userver/dynamic_config/fwd.hpp>
#include <userver/dynamic_config/value.hpp>

#include <taxi_config/variables/DISCOUNT_DESCRIPTION_TO_TAG_MAPPING.hpp>

namespace routestats::full::brandings {

namespace {
using MarketingCashbacks = std::vector<std::string>;
using ValueBuilder = formats::json::ValueBuilder;

struct ServiceLevelsOptions {
  std::optional<core::Discount> discount;
  std::optional<MarketingCashbacks> marketing_cashbacks;
};

const std::string kCashbackType = "cashback";
const std::string kFintechSponsor = "fintech";
const std::string kMastercardSponsor = "mastercard";
const std::string_view kDefaultBrandingInfo(R"({
  "ultima": {
    "enabled": true,
    "type": "cashback",
    "title_key": "default_title_key",
    "subtitle_key": "default_subtitle_key",
    "banner_id": "banner_id",
    "icon": "default_icon"
  }
})");
const std::string_view kFintechBrandingInfo(R"({
  "ultima": {
    "enabled": true,
    "type": "cashback",
    "title_key": "fintech_title_key",
    "subtitle_key": "fintech_subtitle_key",
    "banner_id": "fintech_banner_id",
    "icon": "fintech_icon"
  },
  "econom": {
    "enabled": true,
    "type": "cashback",
    "title_key": "fintech_title_key",
    "subtitle_key": "fintech_subtitle_key",
    "banner_id": "fintech_banner_id",
    "icon": "fintech_icon"
  }
})");
const std::string_view kMastercardBrandingInfo(R"({
  "econom": {
    "enabled": true,
    "type": "cashback",
    "title_key": "mastercard_title_key",
    "subtitle_key": "mastercard_subtitle_key",
    "banner_id": "mastercard_banner_id",
    "icon": "mastercard_icon"
  }
})");

formats::json::Value MakeCashbackBrandingsExp3(
    const std::optional<MarketingCashbacks>& marketing_sponsors) {
  ValueBuilder sponsor_builder{};
  ValueBuilder exp_builder{};

  sponsor_builder["default"] = formats::json::FromString(kDefaultBrandingInfo);
  sponsor_builder[kFintechSponsor] =
      formats::json::FromString(kFintechBrandingInfo);
  sponsor_builder[kMastercardSponsor] =
      formats::json::FromString(kMastercardBrandingInfo);

  std::vector<std::string> possible_sponsors{kFintechSponsor,
                                             kMastercardSponsor};

  if (marketing_sponsors) {
    const auto given_sponsor = marketing_sponsors->front();
    for (const auto& sponsor : possible_sponsors) {
      if (sponsor == given_sponsor) {
        exp_builder = sponsor_builder[sponsor];
      }
    }
  } else {
    exp_builder = sponsor_builder["default"];
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

core::ExpMappedData MockExperiments(
    const std::optional<MarketingCashbacks>& marketing_sponsors) {
  core::ExpMappedData experiment;
  using BrandingExp = experiments3::CashbackBrandingsExp;

  experiment[BrandingExp::kName] = {
      BrandingExp::kName, MakeCashbackBrandingsExp3(marketing_sponsors), {}};

  return experiment;
}

core::TaxiConfigsPtr MockConfigs() {
  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::DISCOUNT_DESCRIPTION_TO_TAG_MAPPING,
       {{{"econom_discount_description", kMastercardSponsor}}}},
  });

  return std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));
}

full::ContextData PrepareDefaultContext(const core::ExpMappedData& exp_data) {
  full::ContextData context = test::full::GetDefaultContext();

  context.user = MockUser(true, true);
  context.taxi_configs = MockConfigs();
  context.get_experiments_mapped_data =
      [&exp_data](const experiments3::models::KwargsBuilderWithConsumer& kwargs)
      -> core::ExpMappedData {
    kwargs.Build();
    return exp_data;
  };

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

TEST(TestBrandingsCashbacksPlugin, FintechHappyPath) {
  BrandingsCashbacksPlugin plugin;
  const MarketingCashbacks marketing_sponsors{kFintechSponsor};
  const auto exp_data = MockExperiments(marketing_sponsors);
  auto plugin_ctx = PrepareDefaultContext(exp_data);

  core::ServiceLevel service_level;
  service_level.marketing_cashbacks = marketing_sponsors;

  std::vector<std::string> service_levels{"econom", "ultima"};

  for (const auto& sl : service_levels) {
    service_level.class_ = sl;
    auto cashback_branding = MakeCashbackBranding();
    auto brandings = MakeBrandings(kCashbackType, cashback_branding);
    std::vector<service_level::TariffBranding> cashback_brandings{
        cashback_branding};

    plugin.ModifyProtocolBrandings(test::full::MakeTopLevelContext(plugin_ctx),
                                   service_level, brandings);

    ASSERT_EQ(cashback_branding.type, "cashback");
    ASSERT_EQ(cashback_branding.title, "fintech_title_key##ru");
    ASSERT_EQ(cashback_branding.subtitle, "fintech_subtitle_key##ru");
    ASSERT_EQ(cashback_branding.action, "show_banner");
    ASSERT_EQ(cashback_branding.value, "42");
    ASSERT_EQ(cashback_branding.icon, "fintech_icon");
    ASSERT_NE(cashback_branding.extra, std::nullopt);
    ASSERT_EQ(cashback_branding.extra->banner_id, "fintech_banner_id");
  }
}

TEST(TestBrandingsCashbacksPlugin, MastercardHappyPath) {
  BrandingsCashbacksPlugin plugin;
  const MarketingCashbacks marketing_sponsors{kMastercardSponsor};
  const auto exp_data = MockExperiments(marketing_sponsors);
  auto plugin_ctx = PrepareDefaultContext(exp_data);

  core::ServiceLevel service_level;
  service_level.class_ = "econom";
  service_level.marketing_cashbacks = marketing_sponsors;

  auto cashback_branding = MakeCashbackBranding();
  auto brandings = MakeBrandings(kCashbackType, cashback_branding);
  std::vector<service_level::TariffBranding> cashback_brandings{
      cashback_branding};

  plugin.ModifyProtocolBrandings(test::full::MakeTopLevelContext(plugin_ctx),
                                 service_level, brandings);

  ASSERT_EQ(cashback_branding.type, "cashback");
  ASSERT_EQ(cashback_branding.title, "mastercard_title_key##ru");
  ASSERT_EQ(cashback_branding.subtitle, "mastercard_subtitle_key##ru");
  ASSERT_EQ(cashback_branding.action, "show_banner");
  ASSERT_EQ(cashback_branding.value, "42");
  ASSERT_EQ(cashback_branding.icon, "mastercard_icon");
  ASSERT_NE(cashback_branding.extra, std::nullopt);
  ASSERT_EQ(cashback_branding.extra->banner_id, "mastercard_banner_id");
}

TEST(TestBrandingsCashbacksPlugin, MastercardDiscountHappyPath) {
  BrandingsCashbacksPlugin plugin;
  const MarketingCashbacks discount_sponsors{kMastercardSponsor};
  const auto exp_data = MockExperiments(discount_sponsors);
  auto plugin_ctx = PrepareDefaultContext(exp_data);

  core::ServiceLevel service_level;
  service_level.class_ = "econom";
  service_level.discount =
      core::Discount{core::Decimal{10}, "econom_discount_description"};

  auto cashback_branding = MakeCashbackBranding();
  auto brandings = MakeBrandings(kCashbackType, cashback_branding);
  std::vector<service_level::TariffBranding> cashback_brandings{
      cashback_branding};

  plugin.ModifyProtocolBrandings(test::full::MakeTopLevelContext(plugin_ctx),
                                 service_level, brandings);

  ASSERT_EQ(cashback_branding.type, "cashback");
  ASSERT_EQ(cashback_branding.title, "mastercard_title_key##ru");
  ASSERT_EQ(cashback_branding.subtitle, "mastercard_subtitle_key##ru");
  ASSERT_EQ(cashback_branding.action, "show_banner");
  ASSERT_EQ(cashback_branding.value, "42");
  ASSERT_EQ(cashback_branding.icon, "mastercard_icon");
  ASSERT_NE(cashback_branding.extra, std::nullopt);
  ASSERT_EQ(cashback_branding.extra->banner_id, "mastercard_banner_id");
}

TEST(TestBrandingsCashbacksPlugin, MissingTranslations) {
  BrandingsCashbacksPlugin plugin;
  const MarketingCashbacks marketing_sponsors{kFintechSponsor};
  const auto exp_data = MockExperiments(marketing_sponsors);
  auto plugin_ctx = PrepareDefaultContext(exp_data);
  plugin_ctx.rendering.translator = std::make_shared<test::TranslatorMock>(
      [](const core::Translation&,
         const std::string&) -> std::optional<std::string> {
        return std::nullopt;
      });
  core::ServiceLevel service_level;
  service_level.class_ = "ultima";
  service_level.marketing_cashbacks = marketing_sponsors;

  auto cashback_branding = MakeCashbackBranding();
  auto brandings = MakeBrandings(kCashbackType, cashback_branding);
  std::vector<service_level::TariffBranding> cashback_brandings{
      cashback_branding};

  plugin.ModifyProtocolBrandings(test::full::MakeTopLevelContext(plugin_ctx),
                                 service_level, brandings);

  ASSERT_EQ(cashback_branding.type, "cashback");
  ASSERT_EQ(cashback_branding.title, "cashback_title");
  ASSERT_EQ(cashback_branding.subtitle, "cashback_subtitle");
  ASSERT_EQ(cashback_branding.action, std::nullopt);
  ASSERT_EQ(cashback_branding.value, "42");
  ASSERT_EQ(cashback_branding.icon, std::nullopt);
  ASSERT_EQ(cashback_branding.extra, std::nullopt);
}

TEST(TestBrandingsCashbacksPlugin, ModifyCashbackDefaultBranding) {
  BrandingsCashbacksPlugin plugin;
  const auto exp_data = MockExperiments(std::nullopt);
  auto plugin_ctx = PrepareDefaultContext(exp_data);

  core::ServiceLevel service_level;
  service_level.class_ = "ultima";

  auto cashback_branding = MakeCashbackBranding();
  auto brandings = MakeBrandings(kCashbackType, cashback_branding);
  std::vector<service_level::TariffBranding> cashback_brandings{
      cashback_branding};

  plugin.ModifyProtocolBrandings(test::full::MakeTopLevelContext(plugin_ctx),
                                 service_level, brandings);

  ASSERT_EQ(cashback_branding.type, "cashback");
  ASSERT_EQ(cashback_branding.title, "default_title_key##ru");
  ASSERT_EQ(cashback_branding.subtitle, "default_subtitle_key##ru");
  ASSERT_EQ(cashback_branding.action, "show_banner");
  ASSERT_EQ(cashback_branding.value, "42");
  ASSERT_EQ(cashback_branding.icon, "default_icon");
  ASSERT_NE(cashback_branding.extra, std::nullopt);
  ASSERT_EQ(cashback_branding.extra->banner_id, "banner_id");
}
}  // namespace routestats::full::brandings
