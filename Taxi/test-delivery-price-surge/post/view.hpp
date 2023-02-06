#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/v1/test-delivery-price-surge/post/request.hpp>
#include <handlers/v1/test-delivery-price-surge/post/response.hpp>

namespace handlers::v1_test_delivery_price_surge::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static Response HandleNonAuthorized(Request&& request,
                                      Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_delivery_price_surge::post
