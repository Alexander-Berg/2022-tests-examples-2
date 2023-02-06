#include <gtest/gtest.h>

#include <experiments3/sweet_home_balance_badge.hpp>

#include "internal/balance_badge/balance_badge.hpp"
#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"

namespace sweet_home::balance_badge {

namespace {
static const std::string kTankerKeyPlaceholderPlus =
    "plus_sweet_home.menu.placeholder.plus";
static const std::string kTankerKeySubtitleHasBalance =
    "plus_sweet_home.menu.subtitle.has_balance";
static const std::string kTankerKeySubtitleZeroBalance =
    "plus_sweet_home.menu.subtitle.zero_balance";
}  // namespace

namespace {
using BalanceBadgeExp = experiments3::SweetHomeBalanceBadge::Value;

template <typename Exp>
formats::json::Value Serialize(const Exp& exp) {
  using formats::json::ValueBuilder;

  ValueBuilder value{};
  value["enabled"] = exp.enabled;
  value["menu_badge"]["show_glyph"] = exp.menu_badge->show_glyph;
  value["menu_badge"]["placeholder_key"] = exp.menu_badge->placeholder_key;
  value["menu_badge"]["subtitle_key"] = exp.menu_badge->subtitle_key;

  return value.ExtractValue();
}

core::Experiments PrepareExperiments(const BalanceBadgeExp& balance_badge_exp) {
  return tests::MakeExperiments({{experiments3::SweetHomeBalanceBadge::kName,
                                  Serialize(balance_badge_exp)}});
}

const core::Experiments kDefaultExperiments = PrepareExperiments(
    {false, experiments3::sweet_home_balance_badge::MenuBadge{false}});
}  // namespace

TEST(TestGetBalanceBadge, WalletWithBalance) {
  const auto wallet = tests::MakeWallet("some_id", "100");
  const BalanceBadgeContext context{kDefaultExperiments, wallet};
  const auto result = GetBalanceBadge(context);

  const BalanceBadge expected = {
      true, tests::MakeTranslationData(kTankerKeySubtitleHasBalance),
      std::nullopt};
  ASSERT_EQ(result, expected);
}

TEST(TestGetBalanceBadge, WalletWithZeroBalance) {
  const auto wallet = tests::MakeWallet("some_id", "0");
  const BalanceBadgeContext context{kDefaultExperiments, wallet};
  const auto result = GetBalanceBadge(context);

  const BalanceBadge expected{
      false, tests::MakeTranslationData(kTankerKeySubtitleZeroBalance),
      tests::MakeTranslationData(kTankerKeyPlaceholderPlus)};
  ASSERT_EQ(expected, result);
}

TEST(TestGetBalanceBadge, NoWallet) {
  const BalanceBadgeContext context{kDefaultExperiments, std::nullopt};
  const auto result = GetBalanceBadge(context);

  const BalanceBadge expected{
      false, tests::MakeTranslationData(kTankerKeySubtitleZeroBalance),
      tests::MakeTranslationData(kTankerKeyPlaceholderPlus)};
  ASSERT_EQ(expected, result);
}

TEST(TestGetBalanceBadge, ForceGlyph) {
  auto wallet = tests::MakeWallet("some_id", "0");

  {
    SCOPED_TRACE("force_glyph = false");

    bool show_glyph = false;
    BalanceBadgeExp exp_value{
        true, experiments3::sweet_home_balance_badge::MenuBadge{show_glyph}};
    BalanceBadgeContext context{PrepareExperiments(exp_value), wallet};
    auto result = GetBalanceBadge(context);
    ASSERT_EQ(result.show_glyph, false);
  }

  {
    SCOPED_TRACE("force_glyph = true");

    bool show_glyph = true;
    BalanceBadgeExp exp_value{
        true, experiments3::sweet_home_balance_badge::MenuBadge{show_glyph}};
    BalanceBadgeContext context{PrepareExperiments(exp_value), wallet};
    auto result = GetBalanceBadge(context);
    ASSERT_EQ(result.show_glyph, true);
  }
}

TEST(TestGetBalanceBadge, TextOverrides) {
  auto wallet = tests::MakeWallet("some_id", "0");

  BalanceBadgeExp exp_value{true,
                            experiments3::sweet_home_balance_badge::MenuBadge{
                                true, "placeholder", "subtitle"}};

  BalanceBadgeContext context{PrepareExperiments(exp_value), wallet};
  auto result = GetBalanceBadge(context);

  ASSERT_TRUE(result.placeholder);
  ASSERT_EQ(result.placeholder->main_key->key, "placeholder");

  ASSERT_TRUE(result.subtitle);
  ASSERT_EQ(result.subtitle->main_key->key, "subtitle");
}

TEST(TestGetBalanceBadge, SubtitleHidden) {
  auto wallet = tests::MakeWallet("some_id", "0");

  // empty string hides subtitle
  const std::string subtitle_key = "";
  BalanceBadgeExp exp_value{true,
                            experiments3::sweet_home_balance_badge::MenuBadge{
                                true, "placeholder", subtitle_key}};

  BalanceBadgeContext context{PrepareExperiments(exp_value), wallet};
  auto result = GetBalanceBadge(context);

  ASSERT_FALSE(result.subtitle);
}

}  // namespace sweet_home::balance_badge
