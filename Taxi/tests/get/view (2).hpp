#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v2/admin/scripts/tests/get/request.hpp>
#include <handlers/v2/admin/scripts/tests/get/response.hpp>

namespace handlers::v2_admin_scripts_tests::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v2_admin_scripts_tests::get
