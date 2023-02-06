#pragma once

#include <memory>

#include <helpers/payment_info/payment_info.hpp>

namespace plus {

class PaymentInfoServiceMock : public PaymentInfoService {
 public:
  PaymentInfoServiceMock(const PaymentInfo& payment_info = PaymentInfo())
      : payment_info_(payment_info){};
  PaymentInfo GetPaymentInfoByOrderId(const std::string&) const override {
    return payment_info_;
  }

 private:
  PaymentInfo payment_info_;
};

std::shared_ptr<PaymentInfoService> MockPaymentInfoService();

}  // namespace plus
