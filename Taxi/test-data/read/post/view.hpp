#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test-data/read/post/request.hpp>
#include <handlers/v1/test-data/read/post/response.hpp>

namespace handlers::v1_test_data_read::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_data_read::post
