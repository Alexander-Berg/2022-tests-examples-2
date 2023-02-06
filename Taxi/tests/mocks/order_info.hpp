#pragma once

#include "core/order_info.hpp"

#include <functional>

namespace sweet_home::mocks {

using RetrieveOrderHandler = std::function<core::OrderInfo(const std::string&)>;
using UpdateCashbackInfoForOrderHandler =
    std::function<void(const core::NewOrderFields&, const std::string&,
                       const std::string&, const std::string&)>;

class OrderInfoServiceMock : public core::OrderInfoService {
 private:
  RetrieveOrderHandler handler_retrieve_order_;
  UpdateCashbackInfoForOrderHandler handler_update_cashback_info_for_order_;

 public:
  OrderInfoServiceMock(const RetrieveOrderHandler& handler_retrieve_order,
                       const UpdateCashbackInfoForOrderHandler&
                           handler_update_cashback_info_for_order)
      : handler_retrieve_order_(handler_retrieve_order),
        handler_update_cashback_info_for_order_(
            handler_update_cashback_info_for_order){};

  core::OrderInfo RetrieveOrder(const std::string& order_id) const override {
    return handler_retrieve_order_(order_id);
  }

  void UpdateCashbackInfoForOrder(const core::NewOrderFields& new_order_fields,
                                  const std::string& order_id,
                                  const std::string& user_id,
                                  const std::string& version) const override {
    return handler_update_cashback_info_for_order_(new_order_fields, order_id,
                                                   user_id, version);
  }
};

}  // namespace sweet_home::mocks
