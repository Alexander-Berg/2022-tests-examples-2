#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test/get-fields/post/request.hpp>
#include <handlers/v1/test/get-fields/post/response.hpp>

namespace handlers::v1_test_get_fields::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_get_fields::post
