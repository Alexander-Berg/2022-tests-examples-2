#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/eats/v1/test/post/request.hpp>
#include <handlers/eats/v1/test/post/response.hpp>

namespace handlers::eats_v1_test::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);

  static Response HandleNonAuthorized(Request&& request,
                                      Dependencies&& dependencies);
};

// clang-format off
} // namespace handlers::eats_v1_test::post
// clang-format on
