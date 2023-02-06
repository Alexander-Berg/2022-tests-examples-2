#include "output_models_test.hpp"

#include <userver/utest/utest.hpp>

namespace sweet_home::tests::output_models {

user_state::output_models::Subscription MakeSubscription(
    const std::string& subscription_id, subscription::PurchaseStatus status,
    bool need_upgrade, const std::optional<std::string>& webview_url) {
  user_state::output_models::Subscription result;
  result.subscription_id = subscription_id;
  result.status = status;
  if (webview_url) {
    result.webview_purchase_params =
        user_state::output_models::WebviewPurchaseParams{*webview_url};
  }
  result.need_upgrade = need_upgrade;
  return result;
}

user_state::output_models::Setting MakeSetting(const std::string& setting_id,
                                               const std::string& value,
                                               bool enabled, bool is_local) {
  return {setting_id, value,    setting::SettingType::kString,
          enabled,    is_local, setting_id + "_metrica_name"};
}

user_state::output_models::Wallet MakeWallet(const std::string& wallet_id,
                                             const std::string& balance,
                                             const std::string& currency) {
  return {wallet_id, currency,
          decimal64::Decimal<4>::FromStringPermissive(balance)};
}

user_state::output_models::Notifications MakeNotifications(int unread_count) {
  return {unread_count};
}

}  // namespace sweet_home::tests::output_models

namespace sweet_home::user_state::output_models {

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

void AssertWallet(const std::optional<Wallet>& left,
                  const std::optional<Wallet>& right) {
  if (!left && !right) {
    SUCCEED();
    return;
  }

  if (!left || !right) {
    FAIL();
    return;
  }

  ASSERT_EQ(left->wallet_id, right->wallet_id);
  ASSERT_EQ(left->balance, right->balance);
  ASSERT_EQ(left->currency, right->currency);
}

bool operator==(const Notifications& left, const Notifications& right) {
  return left.unread_count == right.unread_count;
}

}  // namespace sweet_home::user_state::output_models
