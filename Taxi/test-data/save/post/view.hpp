#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/test-data/save/post/request.hpp>
#include <handlers/v1/test-data/save/post/response.hpp>

namespace handlers::v1_test_data_save::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_test_data_save::post
