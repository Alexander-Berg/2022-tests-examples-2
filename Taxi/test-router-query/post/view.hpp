#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/test-router-query/post/request.hpp>
#include <handlers/test-router-query/post/response.hpp>

namespace handlers::test_router_query::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

// clang-format off
} // namespace handlers::test_router_query::post
// clang-format on
