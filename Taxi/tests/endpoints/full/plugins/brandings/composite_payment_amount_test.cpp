
#include <fmt/format.h>

#include <userver/utest/utest.hpp>

#include <experiments3/composite_payment_minimal_primary_sum.hpp>
#include <experiments3/plaque_routestats_branding_composite_payment_amount.hpp>

#include <endpoints/full/plugins/brandings/subplugins/composite_payment_amount.hpp>

#include <tests/context/translator_mock_test.hpp>
#include <tests/context/wallets_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

namespace routestats::full::brandings {

namespace {

formats::json::Value MakeCompositePaymentAmountExp(
    bool enabled, bool skip_tariffs_with_plus_promo) {
  using formats::json::ValueBuilder;

  ValueBuilder value{};
  value["enabled"] = enabled;
  value["skip_tariffs_with_plus_promo"] = skip_tariffs_with_plus_promo;

  return value.ExtractValue();
}

formats::json::Value MakeMinPaymentExp() {
  using formats::json::ValueBuilder;

  ValueBuilder value{};
  value["enabled"] = true;

  return value.ExtractValue();
}

core::Configs3 MockConfigs3(bool skip_tariffs_with_plus_promo = true) {
  core::ExpMappedData experiments;
  using BrandingExp =
      experiments3::PlaqueRoutestatsBrandingCompositePaymentAmount;

  experiments[BrandingExp::kName] = {
      BrandingExp::kName,
      MakeCompositePaymentAmountExp(true, skip_tariffs_with_plus_promo),
      {}};

  return {{std::move(experiments)}};
}

core::WalletsPtr MockWallets(
    const std::unordered_map<std::string, std::string>& currency2balance) {
  return std::make_shared<test::WalletsMock>(
      [currency2balance](
          const std::string& currency) -> std::optional<core::Wallet> {
        if (!currency2balance.count(currency)) return std::nullopt;
        return core::Wallet{
            "w/123", decimal64::Decimal<4>(currency2balance.at(currency)),
            currency};
      });
}

// Translations would be returned in the form
//   key##[args]##locale
void MockTranslator(full::ContextData& ctx) {
  test::TranslationHandler handler =
      [](const core::Translation& translation,
         const std::string& locale) -> std::optional<std::string> {
    std::vector<std::string> args;
    for (const auto& [key, value] : translation->main_key.args) {
      args.push_back(fmt::format("{}:{}", key, value));
    }

    return fmt::format("{}##[{}]##{}", translation->main_key.key,
                       fmt::join(args, ","), locale);
  };
  ctx.rendering.translator = std::make_shared<test::TranslatorMock>(handler);
}

core::Experiments MockExperiments() {
  core::ExpMappedData experiments;
  using MinimalSumExp = experiments3::CompositePaymentMinimalPrimarySum;

  experiments[MinimalSumExp::kName] = {
      MinimalSumExp::kName, MakeMinPaymentExp(), {}};

  return {std::move(experiments)};
}

full::ContextData PrepareDefaultContext(std::string wallet_balance) {
  full::ContextData ctx = test::full::GetDefaultContext();
  ctx.user.auth_context.locale = "ru";
  ctx.zone->country.id = "rus";
  ctx.zone->country.currency_code = "RUB";

  ctx.experiments.uservices_routestats_configs = MockConfigs3();

  ctx.user_wallets = MockWallets({{"RUB", wallet_balance}});
  MockTranslator(ctx);

  return ctx;
}

struct ServiceLevelsConfig {
  bool fixed_price{true};
  bool add_prices{true};
};

std::unordered_map<std::string, core::ServiceLevel> PrepareServiceLevels(
    const ServiceLevelsConfig& config = ServiceLevelsConfig{}) {
  // econom final_price is zero, because it is already reduced by wallet balance
  // business final_price is reduced by cashback
  return {
      {"econom", test::MockDefaultServiceLevel(
                     "econom",
                     [&config](core::ServiceLevel& level) {
                       level.original_price = "111";
                       level.final_price = core::Decimal{0};
                       level.is_fixed_price = config.fixed_price;
                       if (config.add_prices) {
                         level.prices = core::Prices{core::Decimal{111}};
                       }
                     })},
      {"business", test::MockDefaultServiceLevel(
                       "business",
                       [&config](core::ServiceLevel& level) {
                         level.original_price = "1000";
                         level.final_price = core::Decimal{800};
                         level.is_fixed_price = config.fixed_price;
                         if (config.add_prices) {
                           level.prices = core::Prices{core::Decimal{1000}};
                         }
                       })},
      {"comfortplus", test::MockDefaultServiceLevel(
                          "comfortplus",
                          [&config](core::ServiceLevel& level) {
                            level.original_price = "2000";
                            level.final_price = core::Decimal{2000};
                            level.is_fixed_price = config.fixed_price;
                            if (config.add_prices) {
                              level.prices = core::Prices{core::Decimal{2000}};
                            }
                          })},
  };
}

}  // namespace

namespace {
static const std::string kCompositePaymentAmountType =
    "composite_payment_amount";
}

namespace {
std::optional<std::string> ExpectedValue(
    const std::optional<std::string>& value) {
  if (!value) return std::nullopt;

  return fmt::format("{}##[VALUE:{}]##{}",
                     "routestats.brandings.composite_payment_amount.value",
                     *value, "ru");
}

void AssertBrandings(CompositePaymentAmountPlugin& plugin,
                     const std::string& class_,
                     const std::optional<std::string>& value) {
  SCOPED_TRACE(testing::Message() << __FUNCTION__ << "(" << class_ << ")");

  const auto brandings = plugin.GetBrandings(class_);

  if (!value) {
    ASSERT_TRUE(brandings.empty());
    return;
  }

  ASSERT_EQ(brandings.size(), 1);

  ASSERT_EQ(brandings[0].type, kCompositePaymentAmountType);
  ASSERT_TRUE(brandings[0].value);
  ASSERT_EQ(*brandings[0].value, *value);
}
}  // namespace

TEST(TestCompositePaymentAmountBranding, AbsentWalletPluginDisabled) {
  const std::string wallet_balance = "1000";
  auto ctx = PrepareDefaultContext(wallet_balance);
  ctx.zone->country.currency_code = "USD";

  const auto plugin_ctx = test::full::MakeTopLevelContext(ctx);

  auto levels = PrepareServiceLevels();
  const std::vector<core::ServiceLevel> service_levels{
      levels["econom"],
      levels["business"],
      levels["comfortplus"],
  };

  CompositePaymentAmountPlugin plugin;
  plugin.OnOfferCreated(plugin_ctx, "some_offer", service_levels, {});

  AssertBrandings(plugin, "econom", std::nullopt);
  AssertBrandings(plugin, "business", std::nullopt);
  AssertBrandings(plugin, "comfortplus", std::nullopt);
}

TEST(TestCompositePaymentAmountBranding, WalletBalances) {
  auto levels = PrepareServiceLevels();
  const std::vector<core::ServiceLevel> service_levels{levels["econom"],
                                                       levels["business"]};

  struct Expected {
    std::optional<std::string> econom_value;
    std::optional<std::string> business_value;
  };

  std::unordered_map<std::string, Expected> tests{
      {"0", Expected{std::nullopt, std::nullopt}},
      {"100", Expected{"100", "100"}},
      {"200", Expected{"111", "200"}},
      {"1000", Expected{"111", "1000"}},
  };
  for (const auto& [wallet_balance, expected] : tests) {
    SCOPED_TRACE(testing::Message() << "wallet_balance = " << wallet_balance);

    const auto plugin_ctx =
        test::full::MakeTopLevelContext(PrepareDefaultContext(wallet_balance));

    CompositePaymentAmountPlugin plugin;
    plugin.OnOfferCreated(plugin_ctx, "some_offer", service_levels, {});

    AssertBrandings(plugin, "unknown_service", std::nullopt);
    AssertBrandings(plugin, "econom", ExpectedValue(expected.econom_value));
    AssertBrandings(plugin, "business", ExpectedValue(expected.business_value));
  }
}

TEST(TestCompositePaymentAmountBranding, BrandingsNotAdded) {
  const std::string wallet_balance = "1000";

  std::unordered_map<std::string, ServiceLevelsConfig> tests{
      {"not fixed price", {false, true}},
      {"no prices", {true, false}},
      {"not fixed price and no prices", {false, false}},
  };
  for (const auto& [test_case, config] : tests) {
    SCOPED_TRACE(test_case);

    auto levels = PrepareServiceLevels(config);
    const std::vector<core::ServiceLevel> service_levels{levels["econom"],
                                                         levels["business"]};

    const auto plugin_ctx =
        test::full::MakeTopLevelContext(PrepareDefaultContext(wallet_balance));

    CompositePaymentAmountPlugin plugin;
    plugin.OnOfferCreated(plugin_ctx, "some_offer", service_levels, {});

    AssertBrandings(plugin, "econom", std::nullopt);
    AssertBrandings(plugin, "business", std::nullopt);
  }
}

TEST(TestCompositePaymentAmountBranding, PlusPromoClassesDisabled) {
  const std::string wallet_balance = "2500";

  auto levels = PrepareServiceLevels();
  const std::vector<core::ServiceLevel> service_levels{
      levels["econom"],
      levels["business"],
      levels["comfortplus"],
  };

  std::vector<core::Alternative> alternatives_tmp{
      {"explicit_antisurge",
       "alt_offer_1",
       {},
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt},
      {"plus_promo",
       "alt_offer_2",
       {
           {"business", "alt_offer_2", core::Decimal{"123"}, std::nullopt,
            std::nullopt, std::nullopt, std::nullopt, std::nullopt,
            std::nullopt, std::nullopt, std::nullopt, std::nullopt},
           {"comfortplus", "alt_offer_2", core::Decimal{"321"}, std::nullopt,
            std::nullopt, std::nullopt, std::nullopt, std::nullopt,
            std::nullopt, std::nullopt, std::nullopt, std::nullopt},
       },
       core::AlternativePlusPromo{"11", "econom", "comfortplus"},
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt,
       std::nullopt},
  };

  core::Alternatives alternatives;
  for (auto item : alternatives_tmp) {
    alternatives.options.push_back(item);
  }

  CompositePaymentAmountPlugin plugin;

  {
    SCOPED_TRACE("plus_promo is ignored");

    const auto plugin_ctx =
        test::full::MakeTopLevelContext(PrepareDefaultContext(wallet_balance));
    plugin.OnOfferCreated(plugin_ctx, "some_offer", service_levels,
                          alternatives);

    AssertBrandings(plugin, "econom", std::nullopt);

    // business class is not affected by plus promo
    AssertBrandings(plugin, "business", ExpectedValue("1000"));
    AssertBrandings(plugin, "comfortplus", std::nullopt);
  }

  {
    SCOPED_TRACE("plus_promo is not ignored");

    const bool skip_tariffs_with_plus_promo = false;
    auto ctx_data = PrepareDefaultContext(wallet_balance);
    ctx_data.experiments.uservices_routestats_configs =
        MockConfigs3(skip_tariffs_with_plus_promo);
    const auto plugin_ctx = test::full::MakeTopLevelContext(ctx_data);

    plugin.OnOfferCreated(plugin_ctx, "some_offer", service_levels,
                          alternatives);

    AssertBrandings(plugin, "econom", ExpectedValue("111"));
    AssertBrandings(plugin, "business", ExpectedValue("1000"));
    AssertBrandings(plugin, "comfortplus", ExpectedValue("2000"));
  }
}

TEST(TestCompositePaymentAmountBranding, MinPaymentRule) {
  auto levels = PrepareServiceLevels();
  const std::vector<core::ServiceLevel> service_levels{levels["econom"],
                                                       levels["business"]};

  struct Expected {
    std::optional<std::string> econom_value;
    std::optional<std::string> business_value;
  };

  std::unordered_map<std::string, Expected> tests{
      {"0", Expected{std::nullopt, std::nullopt}},
      {"100", Expected{"100", "100"}},
      {"200", Expected{"110.9", "200"}},
      {"1000", Expected{"110.9", "999.9"}},
  };
  for (const auto& [wallet_balance, expected] : tests) {
    SCOPED_TRACE(testing::Message() << "wallet_balance = " << wallet_balance);

    auto ctx_data = PrepareDefaultContext(wallet_balance);
    ctx_data.user_wallets = MockWallets({{"BYN", wallet_balance}});
    ctx_data.zone->country.currency_code = "BYN";
    ctx_data.experiments.uservices_routestats_exps = MockExperiments();
    const auto plugin_ctx = test::full::MakeTopLevelContext(ctx_data);

    CompositePaymentAmountPlugin plugin;
    plugin.OnOfferCreated(plugin_ctx, "some_offer", service_levels, {});

    AssertBrandings(plugin, "unknown_service", std::nullopt);
    AssertBrandings(plugin, "econom", ExpectedValue(expected.econom_value));
    AssertBrandings(plugin, "business", ExpectedValue(expected.business_value));
  }
}

}  // namespace routestats::full::brandings
