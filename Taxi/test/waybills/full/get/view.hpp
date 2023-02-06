#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test/waybills/full/get/request.hpp>
#include <handlers/v1/test/waybills/full/get/response.hpp>

namespace handlers::v1_test_waybills_full::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_waybills_full::get
