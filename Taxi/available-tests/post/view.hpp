#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/internal/v1/available-tests/post/request.hpp>
#include <handlers/internal/v1/available-tests/post/response.hpp>

namespace handlers::internal_v1_available_tests::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::internal_v1_available_tests::post
