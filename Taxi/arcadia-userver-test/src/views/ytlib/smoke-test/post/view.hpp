#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/ytlib/smoke-test/post/request.hpp>
#include <handlers/ytlib/smoke-test/post/response.hpp>

namespace handlers::ytlib_smoke_test::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::ytlib_smoke_test::post
