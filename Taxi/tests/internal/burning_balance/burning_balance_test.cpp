#include <gtest/gtest.h>

#include "internal/burning_balance/burning_balance.hpp"

#include "tests/core/models_test.hpp"
#include "tests/mocks/burning_balance_service.hpp"

namespace sweet_home::burning_balance {

namespace {

// Aug 26 17:46:40 2021
const auto kBurningTime = std::chrono::system_clock::from_time_t(1630000000);
const auto kDay = std::chrono::hours{24};
const auto kMonth = 30 * kDay;
const auto kCurrentTime = kBurningTime - 2 * kDay;
const auto kWalletId = "wallet_id";
const auto kBalanceToBurn = decimal64::Decimal<4>{10};
const auto kBurnCurrency = "RUB";
const auto kSeenContent = seen_content::SeenContent{};
const auto kBurnIntervals = std::vector<NotificationInterval>{
    {30 * kDay, 15 * kDay}, {15 * kDay, 0 * kDay}};
const auto kBurnScreens =
    std::unordered_set<std::string>{"burn_screen1", "burn_screen2"};

core::BurningBalance MakeBurningBalance(
    const std::string& wallet_id = kWalletId,
    const std::chrono::system_clock::time_point& burn_date = kBurningTime) {
  core::BurningBalance result;
  result.wallet_id = wallet_id;
  result.burn_date = burn_date;
  result.currency = kBurnCurrency;
  result.balance_to_burn = kBalanceToBurn;

  return result;
}

burning_balance::BurnConfiguration MakeBurnConfig(
    std::chrono::milliseconds duration = kMonth) {
  burning_balance::BurnConfiguration config;
  config.burn_duration = duration;
  config.burn_typed_screens = kBurnScreens;
  return config;
}

const auto kBurningBalance = MakeBurningBalance();

const mocks::GetBurnsOfUserBalancesHandler kDefaultGetBurnsHandler =
    [](const std::string&) -> std::vector<core::BurningBalance> {
  return {kBurningBalance};
};

formats::json::Value MakeBurningBalanceExp(bool enabled) {
  formats::json::ValueBuilder builder(formats::common::Type::kObject);
  builder["enabled"] = enabled;
  builder["burning_flow_duration"] = "30d";
  return builder.ExtractValue();
}

BurningBalanceDeps PrepareDeps(
    bool burning_enabled = true,
    mocks::GetBurnsOfUserBalancesHandler handler = kDefaultGetBurnsHandler) {
  auto experiments = tests::MakeExperiments(
      {{"sweet-home:burning_balance", MakeBurningBalanceExp(burning_enabled)}});
  auto burning_balance_service =
      std::make_shared<mocks::BurningBalanceServiceMock>(handler);
  return BurningBalanceDeps{std::move(experiments),
                            std::move(burning_balance_service)};
}

}  // namespace

TEST(TestGetBurnsOfUserBalances, HappyPath) {
  const auto deps = PrepareDeps();

  const auto burns = GetBurnsOfUserBalances(deps, "yandex_uid");
  ASSERT_TRUE(burns.has_value());
  ASSERT_EQ(burns->burning_balances.size(), 1);
}

TEST(TestGetBurnsOfUserBalances, DisabledByExp) {
  auto deps = PrepareDeps(false);  // burning balance exp disabled

  const auto burns = GetBurnsOfUserBalances(deps, "yandex_uid");
  ASSERT_TRUE(!burns.has_value());
}

TEST(TestMakeBurnEvent, HappyPath) {
  const auto burns = std::vector{kBurningBalance};
  const auto burn_config = MakeBurnConfig();
  const auto wallet = tests::MakeWallet(kWalletId, "10");
  const auto picked_burn =
      MakeBurnEvent({burn_config, burns}, wallet, kSeenContent, kCurrentTime);
  ASSERT_TRUE(picked_burn.has_value());
}

TEST(TestMakeBurnEvent, DifferentWalletId) {
  const auto burns = std::vector{kBurningBalance};
  const auto burn_config = MakeBurnConfig();
  const auto wallet = tests::MakeWallet("another-wallet-id", "10");
  const auto picked_burn =
      MakeBurnEvent({burn_config, burns}, wallet, kSeenContent, kCurrentTime);
  ASSERT_FALSE(picked_burn.has_value());
}

TEST(TestMakeBurnEvent, TakesEarlier) {
  const auto first_burn = MakeBurningBalance(kWalletId, kBurningTime);
  const auto burn_config = MakeBurnConfig();
  const auto second_burn = MakeBurningBalance(kWalletId, kBurningTime + kDay);
  const auto wallet = tests::MakeWallet(kWalletId, "10");

  auto picked_burn = MakeBurnEvent({burn_config, {first_burn, second_burn}},
                                   wallet, kSeenContent, kCurrentTime);
  ASSERT_TRUE(picked_burn.has_value());
  ASSERT_EQ(picked_burn->burn_date, first_burn.burn_date);

  // another ordering
  picked_burn = MakeBurnEvent({burn_config, {second_burn, first_burn}}, wallet,
                              kSeenContent, kCurrentTime);
  ASSERT_TRUE(picked_burn.has_value());
  ASSERT_EQ(picked_burn->burn_date, first_burn.burn_date);
}

TEST(TestMakeBurnEvent, FilterByTime) {
  const auto wallet = tests::MakeWallet(kWalletId, "10");

  const auto burns = std::vector{kBurningBalance};
  const auto burn_config = MakeBurnConfig(kMonth - 5 * kDay);
  const auto current_time = kBurningBalance.burn_date - kMonth;

  const auto picked_burn =
      MakeBurnEvent({burn_config, burns}, wallet, kSeenContent, current_time);
  ASSERT_FALSE(picked_burn.has_value());
}

TEST(TestMakeBurnEvent, TestBesyachest) {
  const auto burns = std::vector{kBurningBalance};
  const auto burn_date = kBurningBalance.burn_date;
  const auto wallet = tests::MakeWallet(kWalletId, "10");
  const auto burn_intervals = std::vector<NotificationInterval>{
      {30 * kDay, 15 * kDay}, {15 * kDay, 0 * kDay}};
  auto burn_config = MakeBurnConfig();
  burn_config.notification_intervals = burn_intervals;

  {
    // Never seen before
    auto seen_content = seen_content::SeenContent{};
    const auto current_time = burn_date - 20 * kDay;
    const auto event =
        MakeBurnEvent({burn_config, burns}, wallet, seen_content, current_time);
    ASSERT_TRUE(event.has_value());
    ASSERT_TRUE(!event->user_saw_burn_warnings);
    ASSERT_EQ(event->burn_typed_screens, kBurnScreens);
  }

  {
    // Seen out of range
    auto seen_content = seen_content::SeenContent{};
    seen_content.typed_screens = {{"burn_screen1", {burn_date - 31 * kDay}}};
    const auto current_time = burn_date - 20 * kDay;
    const auto event =
        MakeBurnEvent({burn_config, burns}, wallet, seen_content, current_time);
    ASSERT_TRUE(event.has_value());
    ASSERT_TRUE(!event->user_saw_burn_warnings);
  }

  {
    // Seen in another period
    auto seen_content = seen_content::SeenContent{};
    seen_content.typed_screens = {{"burn_screen1", {burn_date - 20 * kDay}}};
    const auto current_time = burn_date - 10 * kDay;
    const auto event =
        MakeBurnEvent({burn_config, burns}, wallet, seen_content, current_time);
    ASSERT_TRUE(event.has_value());
    ASSERT_TRUE(!event->user_saw_burn_warnings);
  }

  {
    // Seen in current period
    auto seen_content = seen_content::SeenContent{};
    seen_content.typed_screens = {{"burn_screen1", {burn_date - 20 * kDay}}};
    const auto current_time = burn_date - 19 * kDay;
    const auto event =
        MakeBurnEvent({burn_config, burns}, wallet, seen_content, current_time);
    ASSERT_TRUE(event.has_value());
    ASSERT_TRUE(event->user_saw_burn_warnings);
  }

  {
    // Seen one in current period one in another
    auto seen_content = seen_content::SeenContent{};
    seen_content.typed_screens = {{"burn_screen1", {burn_date - 10 * kDay}},
                                  {"burn_screen2", {burn_date - 20 * kDay}}};
    const auto current_time = burn_date - 5 * kDay;
    const auto event =
        MakeBurnEvent({burn_config, burns}, wallet, seen_content, current_time);
    ASSERT_TRUE(event.has_value());
    ASSERT_TRUE(event->user_saw_burn_warnings);
  }

  {
    // Seen two in current period one in another
    auto seen_content = seen_content::SeenContent{};
    seen_content.typed_screens = {{"burn_screen1", {burn_date - 20 * kDay}},
                                  {"burn_screen2", {burn_date - 20 * kDay}}};
    const auto current_time = burn_date - 5 * kDay;
    const auto event =
        MakeBurnEvent({burn_config, burns}, wallet, seen_content, current_time);
    ASSERT_TRUE(event.has_value());
    ASSERT_TRUE(!event->user_saw_burn_warnings);
  }
}

}  // namespace sweet_home::burning_balance
