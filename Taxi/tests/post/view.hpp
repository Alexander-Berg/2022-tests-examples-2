#pragma once

#include <handlers/admin/v1/endpoints/tests/post/request.hpp>
#include <handlers/admin/v1/endpoints/tests/post/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::admin_v1_endpoints_tests::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::admin_v1_endpoints_tests::post
