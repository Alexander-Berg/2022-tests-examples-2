#pragma once

#include "core/subscriptions.hpp"

#include <functional>

namespace sweet_home::mocks {

using GetAvailableSubscriptionsForUserHandler =
    std::function<std::vector<core::MediabillingSubscription>(
        const std::string&, const core::PurchaseContext&, bool)>;

using GetSubscriptionPriceHandler =
    std::function<std::optional<core::Price>(const std::string&)>;

using AcceptCashbackOfferHandler = std::function<void(const std::string&)>;

using GetSubscriptionInfoHandler =
    std::function<std::optional<core::SubscriptionInfo>(const std::string&)>;

class SubscriptionServiceMock : public core::SubscriptionService {
 private:
  GetAvailableSubscriptionsForUserHandler handler_get_subscriptions_;
  GetSubscriptionPriceHandler handler_get_subscription_price_;
  AcceptCashbackOfferHandler handler_accept_cashback_offer_;
  GetSubscriptionInfoHandler handler_get_subscription_info_;

 public:
  SubscriptionServiceMock(
      const GetAvailableSubscriptionsForUserHandler& handler_get_subscriptions,
      const GetSubscriptionPriceHandler& handler_get_subscription_price,
      const AcceptCashbackOfferHandler& handler_accept_cashback_offer = nullptr,
      const GetSubscriptionInfoHandler& handler_get_subscription_info = nullptr)
      : handler_get_subscriptions_(handler_get_subscriptions),
        handler_get_subscription_price_(handler_get_subscription_price),
        handler_accept_cashback_offer_(handler_accept_cashback_offer),
        handler_get_subscription_info_(handler_get_subscription_info){};

  std::vector<core::MediabillingSubscription> GetAvailableSubscriptionsForUser(
      const std::string& yandex_uid,
      const core::PurchaseContext& purchase_context,
      bool ignore_trial) const override {
    return handler_get_subscriptions_(yandex_uid, purchase_context,
                                      ignore_trial);
  }

  std::optional<core::Price> GetSubscriptionPrice(
      const std::string& subscription_id) const override {
    return handler_get_subscription_price_(subscription_id);
  }

  void AcceptCashbackOfferForUser(
      const std::string& yandex_uid) const override {
    if (handler_accept_cashback_offer_) {
      handler_accept_cashback_offer_(yandex_uid);
    }
    return;
  }

  virtual std::optional<core::SubscriptionInfo> GetSubscriptionInfo(
      const std::string& yandex_uid) const override {
    if (handler_get_subscription_info_) {
      return handler_get_subscription_info_(yandex_uid);
    }
    return std::nullopt;
  }
};

}  // namespace sweet_home::mocks
