#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/eats/v1/test_superapp_to_eats_auth/post/request.hpp>
#include <handlers/eats/v1/test_superapp_to_eats_auth/post/response.hpp>

namespace handlers::eats_v1_test_superapp_to_eats_auth::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static Response HandleNonAuthorized(Request&& request,
                                      Dependencies&& dependencies);
};

}  // namespace handlers::eats_v1_test_superapp_to_eats_auth::post
