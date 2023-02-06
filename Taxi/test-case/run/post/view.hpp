#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test-case/run/post/request.hpp>
#include <handlers/v1/test-case/run/post/response.hpp>

namespace handlers::v1_test_case_run::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_case_run::post
