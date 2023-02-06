#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/v1/test/cargo-order/features/post/request.hpp>
#include <handlers/v1/test/cargo-order/features/post/response.hpp>

namespace handlers::v1_test_cargo_order_features::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_cargo_order_features::post
