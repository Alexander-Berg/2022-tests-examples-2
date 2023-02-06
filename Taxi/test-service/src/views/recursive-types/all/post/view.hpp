#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/recursive-types/all/post/request.hpp>
#include <handlers/recursive-types/all/post/response.hpp>

namespace handlers::recursive_types_all::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::recursive_types_all::post
