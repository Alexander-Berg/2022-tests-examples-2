#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/testonly/calldeleteprocedure/post/request.hpp>
#include <handlers/testonly/calldeleteprocedure/post/response.hpp>

namespace handlers::testonly_calldeleteprocedure::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::testonly_calldeleteprocedure::post
