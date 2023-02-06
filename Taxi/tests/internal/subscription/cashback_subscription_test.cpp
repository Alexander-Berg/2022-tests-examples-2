#include <gtest/gtest.h>

#include "internal/subscription/subscription.hpp"

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"

namespace sweet_home::subscription {

namespace {
const std::string kSubscriptionId = "some_id";
}

TEST(TestCouldUpgradeSubscription, CouldUpgrade) {
  const auto subscription = tests::MakePlusSubscription(
      kSubscriptionId, PurchaseStatus::kActive, false);
  const auto experiments =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpEnabled}});
  const auto wallet = tests::MakeWallet("wallet_id", "100");
  ASSERT_TRUE(CouldUpgradePlus(subscription, experiments, wallet));
}

TEST(TestCouldUpgradeSubscription, ExperimentsDisabled) {
  const auto subscription = tests::MakePlusSubscription(
      kSubscriptionId, PurchaseStatus::kActive, false);
  const auto wallet = tests::MakeWallet("wallet_id", "100");

  const auto experiments1 =
      tests::MakeExperiments({{"could_upgrade_plus_enabled", kExpEnabled}});
  ASSERT_FALSE(CouldUpgradePlus(subscription, experiments1, wallet));

  const auto experiments2 = tests::MakeExperiments(
      {{"plus_sdk_cashback_flow_available", kExpEnabled}});
  ASSERT_FALSE(CouldUpgradePlus(subscription, experiments2, wallet));

  const auto experiments3 = tests::MakeExperiments();
  ASSERT_FALSE(CouldUpgradePlus(subscription, experiments3, wallet));
}

TEST(TestCouldUpgradeSubscription, AlreadyUpgraded) {
  const auto subscription = tests::MakePlusSubscription(
      kSubscriptionId, PurchaseStatus::kActive, true);
  const auto experiments =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpEnabled}});
  const auto wallet = tests::MakeWallet("wallet_id", "100");
  ASSERT_FALSE(CouldUpgradePlus(subscription, experiments, wallet));
}

TEST(TestCouldUpgradeSubscription, CannotUpgrade) {
  const auto experiments =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpEnabled}});
  const auto wallet = tests::MakeWallet("wallet_id", "100");

  auto subscription = tests::MakePlusSubscription(
      kSubscriptionId, PurchaseStatus::kAvailable, false);
  ASSERT_FALSE(CouldUpgradePlus(subscription, experiments, wallet));

  subscription.status = PurchaseStatus::kNotAvailable;
  ASSERT_FALSE(CouldUpgradePlus(subscription, experiments, wallet));

  subscription.status = PurchaseStatus::kPurchasing;
  ASSERT_FALSE(CouldUpgradePlus(subscription, experiments, wallet));
}

TEST(TestCouldUpgradeSubscription, ZeroWalletBalance) {
  const auto subscription = tests::MakePlusSubscription(
      kSubscriptionId, PurchaseStatus::kActive, false);
  const auto experiments =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpEnabled},
                              {"check_balance_on_upgrade", kExpEnabled}});

  const auto wallet_zero = tests::MakeWallet("wallet_id", "0");
  ASSERT_FALSE(CouldUpgradePlus(subscription, experiments, wallet_zero));

  const auto wallet_empty = std::nullopt;
  ASSERT_FALSE(CouldUpgradePlus(subscription, experiments, wallet_empty));
}

TEST(TestCouldUpgradeSubscription, ExpCheckBalanceOnUpgradeDisabled) {
  const auto subscription = tests::MakePlusSubscription(
      kSubscriptionId, PurchaseStatus::kActive, false);
  const auto experiments = tests::MakeExperiments({
      {"plus_sdk_cashback_flow_available", kExpEnabled},
      {"could_upgrade_plus_enabled", kExpEnabled},
      {"check_balance_on_upgrade", kExpDisabled},
  });

  const auto wallet_zero = tests::MakeWallet("wallet_id", "0");
  ASSERT_TRUE(CouldUpgradePlus(subscription, experiments, wallet_zero));

  const auto wallet_empty = std::nullopt;
  ASSERT_TRUE(CouldUpgradePlus(subscription, experiments, wallet_empty));
}

}  // namespace sweet_home::subscription
