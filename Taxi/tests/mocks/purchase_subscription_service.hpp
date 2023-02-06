#pragma once

#include "core/purchase_subscription.hpp"

// FIXME: remove or use it anywhere

#include <functional>

namespace sweet_home::mocks {

using PurchaseSubscriptionHandler = std::function<std::string(
    const std::string&, const core::UserInfo&, const std::string&)>;

class PurchaseSubscriptionServiceMock
    : public core::PurchaseSubscriptionService {
 private:
  PurchaseSubscriptionHandler handler_purchase_subscription_;

 public:
  SubscriptionServiceMock(const PurchaseSubscriptionHandler&
                              handler_purchase_subscription = nullptr)
      : handler_purchase_subscription_(handler_purchase_subscription){};

  std::string PurchasePlusSubscriptionForUser(
      const std::string& subscription_id, const core::UserInfo& user_info,
      const std::string& country_code) const override {
    if (handler_purchase_subscription_) {
      return handler_purchase_subscription_(subscription_id, user_info,
                                            country_code);
    }
    return "order_id";
  }
};

}  // namespace sweet_home::mocks
