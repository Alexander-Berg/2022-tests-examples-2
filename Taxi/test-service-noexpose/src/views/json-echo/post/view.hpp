#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/json-echo/post/request.hpp>
#include <handlers/json-echo/post/response.hpp>

namespace handlers::json_echo::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::json_echo::post
