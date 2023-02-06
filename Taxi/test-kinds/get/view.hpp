#pragma once

#include <handlers/admin/v1/test-kinds/get/request.hpp>
#include <handlers/admin/v1/test-kinds/get/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::admin_v1_test_kinds::get {

class View {
 public:
  static Response Handle(Request&&, Dependencies&& dependencies);
};

}  // namespace handlers::admin_v1_test_kinds::get
