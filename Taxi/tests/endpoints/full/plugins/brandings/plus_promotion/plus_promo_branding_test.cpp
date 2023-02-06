#include <endpoints/full/plugins/brandings/plus_promotion/plus_promotion_branding.hpp>

#include <tests/context/taxi_config_mock_test.hpp>
#include <tests/context/translator_mock_test.hpp>
#include <tests/context/wallets_mock_test.hpp>
#include <tests/context_mock_test.hpp>
#include <tests/endpoints/common/service_level_mock_test.hpp>

#include <set>

#include <userver/utest/utest.hpp>

#include <taxi_config/variables/PLUS_SUMMARY_PROMOTION_SETTING.hpp>

namespace routestats::full::brandings {

namespace {
using taxi_config::plus_summary_promotion_setting::PlusSummaryPromotionSetting;

PlusSummaryPromotionSetting MockPromotions(
    const std::string& country, double min_price,
    const std::set<std::string> categories) {
  PlusSummaryPromotionSetting result;
  result.extra[country] = {min_price, 0.1, categories, 50};
  return result;
}

full::ContextData PrepareContext() {
  auto context = test::full::GetDefaultContext();
  context.user.auth_context.flags.has_ya_plus = false;
  context.user.auth_context.locale = "ru";

  context.zone->country.id = "rus";
  context.zone->country.currency_code = "RUB";

  auto config_storage = dynamic_config::MakeDefaultStorage({
      {taxi_config::PLUS_SUMMARY_PROMOTION_SETTING,
       MockPromotions("rus", 100, {"econom"})},
  });

  context.taxi_configs =
      std::make_shared<test::TaxiConfigsMock>(std::move(config_storage));

  return context;
}

core::ServiceLevel MockServiceLevel(std::string class_,
                                    std::optional<core::Decimal> price,
                                    bool is_fixed_price) {
  auto result = test::MockDefaultServiceLevel(class_);
  result.final_price = std::move(price);
  result.is_fixed_price = is_fixed_price;
  return result;
}

}  // namespace

TEST(TestPlusPromotionBranding, PrepareHappyPath) {
  auto context = PrepareContext();
  const auto& result = PreparePlusPromoContext(CreateContext(
      context, plugins::contexts::To<BrandingsPlusPromoContext>{}));

  ASSERT_TRUE(result != std::nullopt);
  ASSERT_EQ(result->currency, "RUB");
  ASSERT_EQ(result->settings.discount, 0.1);
  ASSERT_EQ(result->settings.min_price, 100);
  ASSERT_EQ(result->settings.categories, std::set<std::string>{"econom"});
}

TEST(TestPlusPromotionBranding, PrepareNoOk) {
  {
    auto context = PrepareContext();
    context.user.auth_context.flags.has_ya_plus = true;
    const auto& result = PreparePlusPromoContext(CreateContext(
        context, plugins::contexts::To<BrandingsPlusPromoContext>{}));
    ASSERT_TRUE(result == std::nullopt);
  }
  {
    auto context = PrepareContext();
    context.zone = std::nullopt;
    const auto& result = PreparePlusPromoContext(CreateContext(
        context, plugins::contexts::To<BrandingsPlusPromoContext>{}));
    ASSERT_TRUE(result == std::nullopt);
  }
  {
    auto context = PrepareContext();
    context.zone->country.id = "blr";
    const auto& result = PreparePlusPromoContext(CreateContext(
        context, plugins::contexts::To<BrandingsPlusPromoContext>{}));
    ASSERT_TRUE(result == std::nullopt);
  }
}

TEST(TestPlusPromotionBranding, ShouldAdd) {
  auto context = PrepareContext();
  auto brandings_ctx = CreateContext(
      context, plugins::contexts::To<BrandingsPlusPromoContext>{});

  {
    auto level = MockServiceLevel("vip", core::Decimal(500), false);
    const auto& promo_ctx = PreparePlusPromoContext(brandings_ctx);
    const auto& should_add = ShouldAddBranding(level, *promo_ctx);
    ASSERT_FALSE(should_add);
  }
  {
    auto level = MockServiceLevel("econom", std::nullopt, false);
    const auto& promo_ctx = PreparePlusPromoContext(brandings_ctx);
    const auto& should_add = ShouldAddBranding(level, *promo_ctx);
    ASSERT_FALSE(should_add);
  }
  {
    auto level = MockServiceLevel("econom", core::Decimal(500), false);
    const auto& promo_ctx = PreparePlusPromoContext(brandings_ctx);
    const auto& should_add = ShouldAddBranding(level, *promo_ctx);
    ASSERT_FALSE(should_add);
  }
  {
    auto level = MockServiceLevel("econom", core::Decimal(500), true);
    const auto& promo_ctx = PreparePlusPromoContext(brandings_ctx);
    const auto& should_add = ShouldAddBranding(level, *promo_ctx);
    ASSERT_TRUE(should_add);
  }
}

UTEST(TestPlusPromotionBranding, BrandingData) {
  auto context = PrepareContext();
  context.zone->country.currency_code = "GEL";

  auto brandings_ctx = CreateContext(
      context, plugins::contexts::To<BrandingsPlusPromoContext>{});

  const auto& promo_ctx = PreparePlusPromoContext(CreateContext(
      context, plugins::contexts::To<BrandingsPlusPromoContext>{}));
  auto level = test::MockDefaultServiceLevel("econom");
  level.final_price = core::Decimal("144.43");

  const auto& result =
      BuildPlusPromoBrandingData(level, *promo_ctx, brandings_ctx);
  ASSERT_EQ(result->type, "plus_promotion");
  ASSERT_EQ(result->image_tag, "plus_promo_big_cashback");
  ASSERT_EQ(result->subtitle, std::nullopt);

  auto title_key = result->title->main_key;
  ASSERT_EQ(title_key.key, "routestats.brandings.plus_promo_v2.title");
  ASSERT_EQ(title_key.count, 14);
  auto args = l10n::ArgsList{{"value", "14,4"}};
  ASSERT_EQ(title_key.args, args);
}

UTEST(TestPlusPromotionBranding, BrandingDataWallet) {
  auto context = PrepareContext();
  context.user_wallets =
      std::make_shared<test::WalletsMock>([](const std::string&) {
        return core::Wallet{"wallet_id", core::Decimal{150}, "RUB"};
      });
  context.zone->country.currency_code = "GEL";

  auto brandings_ctx = CreateContext(
      context, plugins::contexts::To<BrandingsPlusPromoContext>{});

  const auto& promo_ctx = PreparePlusPromoContext(CreateContext(
      context, plugins::contexts::To<BrandingsPlusPromoContext>{}));
  auto level = test::MockDefaultServiceLevel("econom");

  auto result = BuildPlusPromoBrandingData(level, *promo_ctx, brandings_ctx);
  ASSERT_EQ(result->type, "plus_promotion");
  ASSERT_EQ(result->image_tag, std::nullopt);
  ASSERT_EQ(result->title->main_key.key,
            "routestats.brandings.plus_promo_v2.wallet.free.title");
  ASSERT_EQ(result->subtitle->get()->main_key.key,
            "routestats.brandings.plus_promo_v2.wallet.subtitle");

  level.final_price = core::Decimal("244.43");
  result = BuildPlusPromoBrandingData(level, *promo_ctx, brandings_ctx);
  ASSERT_EQ(result->title->main_key.key,
            "routestats.brandings.plus_promo_v2.wallet.title");
  auto args = l10n::ArgsList{{"value", "150 $SIGN$$CURRENCY$"}};
  ASSERT_EQ(result->title->main_key.args, args);
}

}  // namespace routestats::full::brandings
