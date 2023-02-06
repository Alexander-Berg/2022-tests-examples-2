#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/testing/run/post/request.hpp>
#include <handlers/v1/testing/run/post/response.hpp>

namespace handlers::v1_testing_run::post {

class View {
 public:
  static Response Handle(const Request& request, const Dependencies& deps);
};

}  // namespace handlers::v1_testing_run::post
