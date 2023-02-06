#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/internal/v1/test-cart-delivery-price-surge/post/request.hpp>
#include <handlers/internal/v1/test-cart-delivery-price-surge/post/response.hpp>

namespace handlers::internal_v1_test_cart_delivery_price_surge::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static Response HandleNonAuthorized(Request&& request,
                                      Dependencies&& dependencies);
};

}  // namespace handlers::internal_v1_test_cart_delivery_price_surge::post
