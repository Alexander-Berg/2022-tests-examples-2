#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/invalid-names/schemas-defs/post/request.hpp>
#include <handlers/invalid-names/schemas-defs/post/response.hpp>

namespace handlers::invalid_names_schemas_defs::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::invalid_names_schemas_defs::post
