#include <userver/utest/utest.hpp>

#include <handlers/4.0/sweet-home/v1/sdk-state/post/response.hpp>

#include "presenters/sdk-state/user_state.hpp"

#include "tests/use_cases/user_state/output_models_test.hpp"

namespace sweet_home::tests::handlers {

::handlers::Subscription MakeSubscription(
    const std::optional<::std::string>& subscription_id,
    const ::handlers::SubscriptionStatus status, bool need_upgrade,
    const std::optional<std::string>& webview_url) {
  ::handlers::Subscription result;
  result.subscription_id = subscription_id;
  result.status = status;
  if (webview_url) {
    result.webview =
        ::handlers::SubscriptionWebviewPurchaseParams{*webview_url};
  }
  result.need_upgrade = need_upgrade;
  return result;
}

::handlers::Setting MakeSetting(const std::string& setting_id,
                                const std::string& value, bool enabled,
                                bool is_local) {
  return {setting_id, ::handlers::SettingType::kString, value, is_local,
          enabled,    setting_id + "_metrica_name"};
}

::handlers::Wallet MakeWallet(const std::string& wallet_id,
                              const std::string& balance,
                              const std::string& currency) {
  return {wallet_id, currency, balance};
}

::handlers::Notifications MakeNotifications(int unread_count) {
  return {unread_count};
}

}  // namespace sweet_home::tests::handlers

namespace handlers {

bool operator==(const Subscription& left, const Subscription& right) {
  return left.subscription_id == right.subscription_id &&
         left.status == right.status && left.need_upgrade == right.need_upgrade;
}

void AssertSetting(const Setting& left, const Setting& right) {
  ASSERT_EQ(left.setting_id, right.setting_id);
  ASSERT_EQ(left.value, right.value);
  ASSERT_EQ(left.type, right.type);
  ASSERT_EQ(left.is_local, right.is_local);
  if (left.metrica_name) {
    ASSERT_TRUE(right.metrica_name) << "left is " << *left.metrica_name;
    ASSERT_EQ(*left.metrica_name, *right.metrica_name);
  } else {
    ASSERT_FALSE(right.metrica_name) << "right is " << *right.metrica_name;
  }
}

bool operator==(const Wallet& left, const Wallet& right) {
  return left.wallet_id == right.wallet_id && left.currency == right.currency &&
         left.balance == right.balance;
}

bool operator==(const Notifications& left, const Notifications& right) {
  return left.unread_count == right.unread_count;
}

}  // namespace handlers

namespace sweet_home::presenters {

namespace {

user_state::output_models::UserStateData PrepareModel() {
  user_state::output_models::UserStateData model;
  model.subscription = tests::output_models::MakeSubscription(
      "ya_plus", subscription::PurchaseStatus::kAvailable, false,
      "expected_webview_url");

  std::vector<user_state::output_models::Setting> settings = {
      tests::output_models::MakeSetting("service_setting_id", "some_value"),
      // this setting must be added in result
      tests::output_models::MakeSetting("global_setting_id",
                                        "global_default_value", true, true),
  };
  model.settings = {settings, "some_version"};
  model.wallets = {tests::output_models::MakeWallet("RUB_wallet", "120")};
  model.notifications = tests::output_models::MakeNotifications(1);
  return model;
}

}  // namespace

TEST(TestUserStatePresenter, HappyPath) {
  // prepare
  auto model = PrepareModel();

  // call
  auto result = BuildUserState(model);

  // assertions
  auto expected_subscription = tests::handlers::MakeSubscription(
      "ya_plus", handlers::SubscriptionStatus::kAvailable, false,
      "expected_webview_url");
  ASSERT_EQ(result.subscription, expected_subscription);

  ASSERT_EQ(result.settings.version, "some_version");
  ASSERT_EQ(result.settings.settings.size(), 2);

  handlers::AssertSetting(  //
      result.settings.settings[0],
      tests::handlers::MakeSetting("service_setting_id", "some_value", true,
                                   false));

  handlers::AssertSetting(
      result.settings.settings[1],
      tests::handlers::MakeSetting("global_setting_id", "global_default_value",
                                   true, true));

  std::vector<handlers::Wallet> expected_wallets = {
      tests::handlers::MakeWallet("RUB_wallet", "120", "RUB")};
  ASSERT_EQ(result.wallets, expected_wallets);

  ASSERT_EQ(result.notifications, tests::handlers::MakeNotifications(1));
}

}  // namespace sweet_home::presenters
