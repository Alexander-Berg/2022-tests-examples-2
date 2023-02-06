#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test-data/create/post/request.hpp>
#include <handlers/v1/test-data/create/post/response.hpp>

namespace handlers::v1_test_data_create::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_data_create::post
