#pragma once

#include "core/cashback_info.hpp"

#include <functional>

namespace cashback_int_api::mocks {

namespace {

core::OrderCashbackInfo DefaultGetCashbackInfoForOrderHandler(
    const std::string& order_id, const std::string& /*service_id*/) {
  core::OrderCashbackInfo order_cashback_info;
  order_cashback_info.order_id = order_id;
  order_cashback_info.amount = core::Decimal{0};
  order_cashback_info.version = "1";

  return order_cashback_info;
}

}  // namespace

using GetCashbackInfoForOrderHandler = std::function<core::OrderCashbackInfo(
    const std::string&, const std::string&)>;

class CashbackInfoServiceMock : public core::CashbackInfoService {
 private:
  GetCashbackInfoForOrderHandler handler_get_cashback_info_for_order_;

 public:
  CashbackInfoServiceMock(const GetCashbackInfoForOrderHandler&
                              handler_get_cashback_info_for_order = nullptr)
      : handler_get_cashback_info_for_order_(
            handler_get_cashback_info_for_order){};

  core::OrderCashbackInfo GetCashbackInfoForOrder(
      const std::string& order_id,
      const std::string& service_id) const override {
    if (!handler_get_cashback_info_for_order_) {
      return DefaultGetCashbackInfoForOrderHandler(order_id, service_id);
    }
    return handler_get_cashback_info_for_order_(order_id, service_id);
  }
};

}  // namespace cashback_int_api::mocks
