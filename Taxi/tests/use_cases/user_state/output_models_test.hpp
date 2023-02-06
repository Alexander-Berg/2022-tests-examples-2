#pragma once

#include "use_cases/user_state/output_models.hpp"

namespace sweet_home::tests::output_models {

namespace defaults {
const std::string kDefaultCurrency = "RUB";
}

user_state::output_models::Subscription MakeSubscription(
    const std::string& subscription_id, subscription::PurchaseStatus status,
    bool need_upgrade,
    const std::optional<std::string>& webview_url = std::nullopt);

user_state::output_models::Setting MakeSetting(const std::string& setting_id,
                                               const std::string& value,
                                               bool enabled = true,
                                               bool is_local = false);

user_state::output_models::Wallet MakeWallet(
    const std::string& wallet_id, const std::string& balance,
    const std::string& currency = defaults::kDefaultCurrency);

user_state::output_models::Notifications MakeNotifications(int unread_count);

}  // namespace sweet_home::tests::output_models

namespace sweet_home::user_state::output_models {

bool operator==(const Subscription& left, const Subscription& right);
void AssertSetting(const Setting& left, const Setting& right);
bool operator==(const Wallet& left, const Wallet& right);
void AssertWallet(const std::optional<Wallet>& left,
                  const std::optional<Wallet>& right);
bool operator==(const Notifications& left, const Notifications& right);

}  // namespace sweet_home::user_state::output_models
