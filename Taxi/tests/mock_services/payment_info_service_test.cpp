#include "payment_info_service_test.hpp"

namespace plus {

std::shared_ptr<PaymentInfoService> MockPaymentInfoService() {
  return std::make_shared<PaymentInfoServiceMock>();
}

}  // namespace plus
