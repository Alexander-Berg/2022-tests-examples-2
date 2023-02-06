#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test-case/activate/post/request.hpp>
#include <handlers/v1/test-case/activate/post/response.hpp>

namespace handlers::v1_test_case_activate::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_case_activate::post
