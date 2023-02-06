#include <gtest/gtest.h>

#include "internal/subscription/subscription.hpp"

#include "tests/core/models_test.hpp"
#include "tests/internal/models_test.hpp"
#include "tests/mocks/subscription_service.hpp"

namespace sweet_home::subscription {

namespace {

const std::string kDefaultYandexUid = "default_yandex_uid";

mocks::AcceptCashbackOfferHandler accept_cashback_offer_handler_default =
    [](const std::string& yandex_uid) {
      ASSERT_EQ(yandex_uid, kDefaultYandexUid);
    };

SubscriptionDeps PrepareDeps(
    const mocks::AcceptCashbackOfferHandler& accept_cashback_offer_handler =
        accept_cashback_offer_handler_default) {
  auto get_subscriptions_handler = nullptr;
  auto get_subscription_price_handler = nullptr;

  SubscriptionDeps deps{
      std::make_shared<mocks::SubscriptionServiceMock>(
          get_subscriptions_handler, get_subscription_price_handler,
          accept_cashback_offer_handler),
      tests::MakeExperiments()};

  return deps;
}

}  // namespace

TEST(TestUpgradeSubscription, CouldUpgrade) {
  const auto deps = PrepareDeps();
  const auto subscription =
      tests::MakePlusSubscription("", PurchaseStatus::kActive, false);
  const auto experiments =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpEnabled}});
  const auto wallet = tests::MakeWallet("wallet_id", "100");

  const SubscriptionContext context{experiments, wallet};

  UpgradePlusSubscriptionToCashback(deps, context, subscription,
                                    kDefaultYandexUid);
}

TEST(TestUpgradeSubscription, UpgradeSubscriptionError) {
  mocks::AcceptCashbackOfferHandler get_subscription_price_handler =
      [](const std::string&) { throw core::MediabillingError(""); };
  const auto deps = PrepareDeps(get_subscription_price_handler);

  const auto subscription =
      tests::MakePlusSubscription("", PurchaseStatus::kActive, false);
  const auto experiments =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpEnabled}});
  const auto wallet = tests::MakeWallet("wallet_id", "100");

  const SubscriptionContext context{experiments, wallet};

  ASSERT_THROW(UpgradePlusSubscriptionToCashback(deps, context, subscription,
                                                 kDefaultYandexUid),
               UpgradeSubscriptionError);
}

TEST(TestUpgradeSubscription, ExperimentsDisabled) {
  const auto deps = PrepareDeps();
  const auto subscription =
      tests::MakePlusSubscription("", PurchaseStatus::kActive, false);
  const auto wallet = tests::MakeWallet("wallet_id", "100");

  const auto experiments1 =
      tests::MakeExperiments({{"could_upgrade_plus_enabled", kExpEnabled}});

  const SubscriptionContext context_1{experiments1, wallet};
  ASSERT_THROW(UpgradePlusSubscriptionToCashback(deps, context_1, subscription,
                                                 kDefaultYandexUid),
               CanNotUpgradeSubscription);

  const auto experiments2 = tests::MakeExperiments(
      {{"plus_sdk_cashback_flow_available", kExpEnabled}});
  const SubscriptionContext context_2{experiments2, wallet};
  ASSERT_THROW(UpgradePlusSubscriptionToCashback(deps, context_2, subscription,
                                                 kDefaultYandexUid),
               CanNotUpgradeSubscription);

  const auto experiments3 = tests::MakeExperiments();
  const SubscriptionContext context_3{experiments2, wallet};
  ASSERT_THROW(UpgradePlusSubscriptionToCashback(deps, context_3, subscription,
                                                 kDefaultYandexUid),
               CanNotUpgradeSubscription);
}

TEST(TestUpgradeSubscription, AlreadyUpgraded) {
  const auto deps = PrepareDeps();
  const auto subscription =
      tests::MakePlusSubscription("", PurchaseStatus::kActive, true);
  const auto experiments =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpEnabled}});
  const auto wallet = tests::MakeWallet("wallet_id", "100");

  const SubscriptionContext context{experiments, wallet};
  ASSERT_THROW(UpgradePlusSubscriptionToCashback(deps, context, subscription,
                                                 kDefaultYandexUid),
               CanNotUpgradeSubscription);
}

TEST(TestUpgradeSubscription, BadSubscriptionPurchaseStatus) {
  const auto deps = PrepareDeps();
  const auto experiments =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpEnabled}});
  const auto wallet = tests::MakeWallet("wallet_id", "100");
  const SubscriptionContext context{experiments, wallet};

  auto subscription =
      tests::MakePlusSubscription("", PurchaseStatus::kAvailable, false);
  ASSERT_THROW(UpgradePlusSubscriptionToCashback(deps, context, subscription,
                                                 kDefaultYandexUid),
               CanNotUpgradeSubscription);

  subscription.status = PurchaseStatus::kNotAvailable;
  ASSERT_THROW(UpgradePlusSubscriptionToCashback(deps, context, subscription,
                                                 kDefaultYandexUid),
               CanNotUpgradeSubscription);

  subscription.status = PurchaseStatus::kPurchasing;
  ASSERT_THROW(UpgradePlusSubscriptionToCashback(deps, context, subscription,
                                                 kDefaultYandexUid),
               CanNotUpgradeSubscription);
}

TEST(TestUpgradeSubscription, ZeroWalletBalance) {
  const auto deps = PrepareDeps();
  const auto subscription =
      tests::MakePlusSubscription("", PurchaseStatus::kActive, false);
  const auto experiments =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpEnabled},
                              {"check_balance_on_upgrade", kExpEnabled}});

  const auto wallet_zero = tests::MakeWallet("wallet_id", "0");
  const SubscriptionContext context_1{experiments, wallet_zero};
  ASSERT_THROW(UpgradePlusSubscriptionToCashback(deps, context_1, subscription,
                                                 kDefaultYandexUid),
               CanNotUpgradeSubscription);

  const auto wallet_empty = std::nullopt;
  const SubscriptionContext context_2{experiments, wallet_empty};
  ASSERT_THROW(UpgradePlusSubscriptionToCashback(deps, context_2, subscription,
                                                 kDefaultYandexUid),
               CanNotUpgradeSubscription);
}

}  // namespace sweet_home::subscription
