#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/tests/v1/validate/post/request.hpp>
#include <handlers/tests/v1/validate/post/response.hpp>

namespace handlers::tests_v1_validate::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::tests_v1_validate::post
