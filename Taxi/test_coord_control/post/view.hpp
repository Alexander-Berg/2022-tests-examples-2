#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/test_coord_control/post/request.hpp>
#include <handlers/test_coord_control/post/response.hpp>

namespace handlers::test_coord_control::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::test_coord_control::post
