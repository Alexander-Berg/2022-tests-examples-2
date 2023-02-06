#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/testing/test/post/request.hpp>
#include <handlers/v1/testing/test/post/response.hpp>

namespace handlers::v1_testing_test::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_testing_test::post
