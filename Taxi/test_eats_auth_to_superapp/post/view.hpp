#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/eats/v1/test_eats_auth_to_superapp/post/request.hpp>
#include <handlers/eats/v1/test_eats_auth_to_superapp/post/response.hpp>

namespace handlers::eats_v1_test_eats_auth_to_superapp::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static Response HandleNonAuthorized(Request&& request,
                                      Dependencies&& dependencies);
};

}  // namespace handlers::eats_v1_test_eats_auth_to_superapp::post
