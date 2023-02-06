#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test-case/list/post/request.hpp>
#include <handlers/v1/test-case/list/post/response.hpp>

namespace handlers::v1_test_case_list::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_case_list::post
