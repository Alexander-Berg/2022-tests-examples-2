#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/v1/test-delivery-price-surge/get/request.hpp>
#include <handlers/v1/test-delivery-price-surge/get/response.hpp>

namespace handlers::v1_test_delivery_price_surge::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_delivery_price_surge::get
