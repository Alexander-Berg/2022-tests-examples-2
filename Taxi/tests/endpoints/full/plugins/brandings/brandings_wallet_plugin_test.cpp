#include <endpoints/full/builders/input_builder.hpp>
#include <endpoints/full/core/input.hpp>
#include <endpoints/full/plugins/brandings/subplugins/brandings_wallet.hpp>

#include <userver/utest/utest.hpp>

#include <experiments3/wallet_cost_coverage_branding.hpp>
#include <tests/context/wallets_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

namespace routestats::full::brandings {

namespace {

formats::json::Value MakeWalletSuggestExp(
    bool enabled, const std::vector<std::string>& classes) {
  using formats::json::ValueBuilder;

  ValueBuilder wallet_suggest{};
  wallet_suggest["enabled"] = enabled;

  wallet_suggest["service_levels"] =
      ValueBuilder(formats::common::Type::kArray);
  for (const auto& class_ : classes) {
    wallet_suggest["service_levels"].PushBack(class_);
  }

  return wallet_suggest.ExtractValue();
}

full::RoutestatsInput MockInput(
    const std::unordered_map<std::string, std::string>& complements) {
  full::RoutestatsRequest request;

  request.payment = handlers::RequestPayment{};
  request.payment->complements =
      std::vector<handlers::RequestPaymentComplement>{};
  for (const auto& [type, id] : complements) {
    request.payment->complements->push_back({type, id});
  }
  return full::BuildRoutestatsInput(request, {}, {});
}

core::Experiments MockExperiments(
    const std::vector<std::string>& branding_classes) {
  core::ExpMappedData experiments;
  using BrandingExp = experiments3::WalletCostCoverageBranding;

  experiments[BrandingExp::kName] = {
      BrandingExp::kName, MakeWalletSuggestExp(true, branding_classes), {}};

  return {std::move(experiments)};
}

core::WalletsPtr MockWallets(
    const std::unordered_map<std::string, int>& currency2balance) {
  return std::make_shared<test::WalletsMock>(
      [currency2balance](
          const std::string& currency) -> std::optional<core::Wallet> {
        if (!currency2balance.count(currency)) return std::nullopt;
        return core::Wallet{
            "w/123", decimal64::Decimal<4>(currency2balance.at(currency)),
            currency};
      });
}

full::User MockUser(bool ya_plus, bool cashback_plus) {
  full::AuthContext auth_context{};
  auth_context.flags.has_ya_plus = ya_plus;
  auth_context.flags.has_plus_cashback = cashback_plus;
  return {std::move(auth_context), std::nullopt};
}

core::Zone MockZone(const std::string& currency) {
  models::Country country;
  country.currency_code = currency;
  return {{}, {}, std::move(country), {}};
}

full::ContextData PrepareDefaultContext() {
  full::ContextData context = test::full::GetDefaultContext();
  context.input = MockInput({{"personal_wallet", "w/123"}});
  context.experiments.uservices_routestats_exps =
      MockExperiments({"econom", "business"});
  context.user = MockUser(true, true);
  context.zone = MockZone("RUB");
  context.user_wallets = MockWallets({{"RUB", 100}});
  return context;
}

std::vector<core::ServiceLevel> PrepareServiceLevels(bool fixed_price = true) {
  // econom final_price is zero, because it is already reduced by
  // wallet balance
  return {
      test::MockDefaultServiceLevel("econom",
                                    [fixed_price](core::ServiceLevel& level) {
                                      level.final_price = core::Decimal{0};
                                      level.is_fixed_price = fixed_price;
                                    }),
      test::MockDefaultServiceLevel("business",
                                    [fixed_price](core::ServiceLevel& level) {
                                      level.final_price = core::Decimal{1000};
                                      level.is_fixed_price = fixed_price;
                                    })};
}

}  // namespace

TEST(TestWalletPlugin, HappyPath) {
  BrandingsWalletPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = PrepareDefaultContext();

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  ASSERT_EQ(plugin.GetBrandings("unknown_service").size(), 0);

  const auto& econom_brandings = plugin.GetBrandings("econom");
  ASSERT_EQ(econom_brandings.size(), 1);

  const auto& branding = econom_brandings.front();
  ASSERT_EQ(branding.type, "complement_wallet_full_cost_coverage");
}

TEST(TestWalletPlugin, NotFixedPrice) {
  BrandingsWalletPlugin plugin;
  auto service_levels = PrepareServiceLevels(false);
  auto plugin_ctx = PrepareDefaultContext();

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
}

TEST(TestWalletPlugin, NotEnoughMoney) {
  BrandingsWalletPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = PrepareDefaultContext();

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  ASSERT_EQ(plugin.GetBrandings("business").size(), 0);
}

TEST(TestWalletPlugin, ClassesInExperimentDisabled) {
  BrandingsWalletPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = PrepareDefaultContext();
  plugin_ctx.experiments.uservices_routestats_exps = MockExperiments({});

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
}

TEST(TestWalletPlugin, UserHasNoCashbackPlus) {
  BrandingsWalletPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = PrepareDefaultContext();
  plugin_ctx.user = MockUser(false, false);

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
}

TEST(TestWalletPlugin, NoZone) {
  BrandingsWalletPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = PrepareDefaultContext();
  plugin_ctx.zone = std::nullopt;

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
}

TEST(TestWalletPlugin, NoWallet) {
  BrandingsWalletPlugin plugin;
  auto service_levels = PrepareServiceLevels();
  auto plugin_ctx = PrepareDefaultContext();
  plugin_ctx.user_wallets = MockWallets({});

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
}

TEST(TestWalletPlugin, ComplementsNotInRequest) {
  BrandingsWalletPlugin plugin;
  auto service_levels = PrepareServiceLevels(false);
  auto plugin_ctx = PrepareDefaultContext();
  plugin_ctx.input = MockInput({});

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
}

TEST(TestWalletPlugin, NotEqualWalletId) {
  BrandingsWalletPlugin plugin;
  auto service_levels = PrepareServiceLevels(false);
  auto plugin_ctx = PrepareDefaultContext();
  plugin_ctx.input = MockInput({{"personal_wallet", "w/321"}});

  plugin.OnServiceLevelsReady(test::full::MakeTopLevelContext(plugin_ctx),
                              service_levels);

  ASSERT_EQ(plugin.GetBrandings("econom").size(), 0);
}

}  // namespace routestats::full::brandings
