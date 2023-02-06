#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/internal/v1/tests/price/get/request.hpp>
#include <handlers/internal/v1/tests/price/get/response.hpp>

namespace handlers::internal_v1_tests_price::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::internal_v1_tests_price::get
