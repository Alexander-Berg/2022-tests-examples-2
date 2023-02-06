#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/debug/run-test-case/post/request.hpp>
#include <handlers/v1/debug/run-test-case/post/response.hpp>

namespace handlers::v1_debug_run_test_case::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_debug_run_test_case::post
