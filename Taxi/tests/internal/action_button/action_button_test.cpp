#include <gtest/gtest.h>

#include "internal/action_button/action_button.hpp"
#include "internal/subscription/models.hpp"

#include "tests/core/models_test.hpp"
#include "tests/internal/defaults.hpp"
#include "tests/internal/models_test.hpp"
#include "tests/mocks/action_button_repository.hpp"

namespace sweet_home::action_button {

TEST(TestGetActionButton, BuyPlus) {
  auto action_button_mock = mocks::ActionButtonRepositoryMock();
  ActionButtonDeps deps{
      std::make_shared<mocks::ActionButtonRepositoryMock>(action_button_mock)};

  auto experiments =
      tests::MakeExperiments({{"check_balance_on_upgrade", kExpEnabled}});

  auto sdk_client = tests::MakeSDKClient();
  ActionButtonContext context{
      tests::MakePlusSubscription(
          "sub_id", subscription::PurchaseStatus::kAvailable, false),
      experiments, std::nullopt, sdk_client};

  auto result = GetActionButtonForSubscription(deps, context);

  ASSERT_EQ(result->action, Action::kPlusBuy);

  // sub is kPurchasing -> Action BuyPlus
  auto plus_sub1 = tests::MakePlusSubscription(
      "sub_id", subscription::PurchaseStatus::kPurchasing, false);
  ActionButtonContext contex1{plus_sub1, experiments, std::nullopt, sdk_client};
  result = GetActionButtonForSubscription(deps, contex1);
  ASSERT_EQ(result->action, Action::kPlusBuy);
}

TEST(TestGetActionButton, NoBuyPlus) {
  auto action_button_mock = mocks::ActionButtonRepositoryMock();
  ActionButtonDeps deps{
      std::make_shared<mocks::ActionButtonRepositoryMock>(action_button_mock)};

  auto experiments = tests::MakeExperiments();

  // already bought
  ActionButtonContext context1{kActiveSubscription, experiments, std::nullopt,
                               tests::MakeSDKClient()};

  auto result1 = GetActionButtonForSubscription(deps, context1);
  ASSERT_FALSE(result1);

  // purchase disabled
  core::SDKClientConfig client_config2;
  client_config2.purchase_type = core::SDKPurchaseType::kDisabled;

  ActionButtonContext context2{kAvailableSubscription, experiments,
                               std::nullopt,
                               tests::MakeSDKClient(client_config2)};

  auto result2 = GetActionButtonForSubscription(deps, context2);
  ASSERT_FALSE(result2);
}

TEST(TestGetActionButton, UpgradePlus) {
  auto action_button_mock = mocks::ActionButtonRepositoryMock();
  ActionButtonDeps deps{
      std::make_shared<mocks::ActionButtonRepositoryMock>(action_button_mock)};

  auto experiments =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpEnabled}});

  auto sdk_client = tests::MakeSDKClient();
  ActionButtonContext context{
      tests::MakePlusSubscription("sub_id",
                                  subscription::PurchaseStatus::kActive, false),
      experiments, tests::MakeWallet("wallet_id", "100"), sdk_client};

  const auto result = GetActionButtonForSubscription(deps, context);

  ASSERT_EQ(result->action, Action::kPlusUpgrade);
}

TEST(TestGetActionButton, NoUpgradePlus) {
  auto action_button_mock = mocks::ActionButtonRepositoryMock();
  ActionButtonDeps deps{
      std::make_shared<mocks::ActionButtonRepositoryMock>(action_button_mock)};

  auto plus_sub = tests::MakePlusSubscription(
      "sub_id", subscription::PurchaseStatus::kActive, false);
  auto experiments =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpEnabled},
                              {"check_balance_on_upgrade", kExpEnabled}});
  auto wallet = tests::MakeWallet("wallet_id", "0");
  auto sdk_client = tests::MakeSDKClient();

  // zero wallet -> no upgrade
  ActionButtonContext context1{plus_sub, experiments, wallet, sdk_client};
  auto result = GetActionButtonForSubscription(deps, context1);
  ASSERT_FALSE(result);

  // upgrade disabled -> no upgrade
  core::SDKClientConfig client_config;
  client_config.purchase_type = core::SDKPurchaseType::kNative;
  client_config.upgrade_enabled = false;
  ActionButtonContext context_disabled_upgrade{
      plus_sub, experiments, wallet, tests::MakeSDKClient(client_config)};
  result = GetActionButtonForSubscription(deps, context_disabled_upgrade);
  ASSERT_FALSE(result);

  // plus_sdk_plus_sdk_cashback_flow_available disabled -> no upgrade
  auto exps1 = tests::MakeExperiments(
      {{"plus_sdk_cashback_flow_available", kExpDisabled},
       {"could_upgrade_plus_enabled", kExpEnabled}});
  ActionButtonContext context2{plus_sub, exps1, wallet, sdk_client};
  result = GetActionButtonForSubscription(deps, context2);
  ASSERT_FALSE(result);

  // could_upgrade_plus_enabled disabled -> no upgrade
  auto exps2 =
      tests::MakeExperiments({{"plus_sdk_cashback_flow_available", kExpEnabled},
                              {"could_upgrade_plus_enabled", kExpDisabled}});
  ActionButtonContext context3{plus_sub, exps2, wallet, sdk_client};
  result = GetActionButtonForSubscription(deps, context3);
  ASSERT_FALSE(result);

  // sub is cashback -> no upgrade
  ActionButtonContext context4{kActiveSubscription, experiments, wallet,
                               sdk_client};
  result = GetActionButtonForSubscription(deps, context4);
  ASSERT_FALSE(result);

  // sub status is kNotAvailable -> no upgrade
  auto plus_sub2 = tests::MakePlusSubscription(
      "sub_id", subscription::PurchaseStatus::kNotAvailable, false);
  ActionButtonContext context5{plus_sub2, experiments, wallet, sdk_client};
  result = GetActionButtonForSubscription(deps, context5);
  ASSERT_FALSE(result);
}

TEST(TestGetActionButton, Webview) {
  auto action_button_mock = mocks::ActionButtonRepositoryMock();
  ActionButtonDeps deps{
      std::make_shared<mocks::ActionButtonRepositoryMock>(action_button_mock)};

  // webview params exist -> Webview Button
  core::SDKClientConfig client_config;
  client_config.purchase_type = core::SDKPurchaseType::kWebview;
  client_config.webview_params = core::WebviewParams{};

  ActionButtonContext context{kAvailableSubscription, tests::MakeExperiments(),
                              std::nullopt,
                              tests::MakeSDKClient(client_config)};

  const auto result1 = GetActionButtonForSubscription(deps, context);
  ASSERT_EQ(result1->action, Action::kPlusBuyWebview);

  // webview params absent -> No Button
  context.sdk_client.config.webview_params = std::nullopt;
  const auto result2 = GetActionButtonForSubscription(deps, context);
  ASSERT_FALSE(result2);
}

TEST(TestGetActionButton, Inapp) {
  auto action_button_mock = mocks::ActionButtonRepositoryMock();
  ActionButtonDeps deps{
      std::make_shared<mocks::ActionButtonRepositoryMock>(action_button_mock)};

  core::SDKClientConfig client_config;
  client_config.purchase_type = core::SDKPurchaseType::kInapp;

  auto subscription = kAvailableSubscription;
  subscription.subscription_id = "inapp";

  ActionButtonContext context{subscription, tests::MakeExperiments(),
                              std::nullopt,
                              tests::MakeSDKClient(client_config)};

  const auto result = GetActionButtonForSubscription(deps, context);
  ASSERT_EQ(result->action, Action::kPlusBuyInapp);
}

}  // namespace sweet_home::action_button
