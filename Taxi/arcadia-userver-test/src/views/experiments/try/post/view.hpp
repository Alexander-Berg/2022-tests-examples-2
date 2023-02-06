#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/experiments/try/post/request.hpp>
#include <handlers/experiments/try/post/response.hpp>

namespace handlers::experiments_try::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::experiments_try::post
