#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/superapp/test/post/request.hpp>
#include <handlers/superapp/test/post/response.hpp>

namespace handlers::superapp_test::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static Response HandleNonAuthorized(Request&& request,
                                      Dependencies&& dependencies);
};

}  // namespace handlers::superapp_test::post
