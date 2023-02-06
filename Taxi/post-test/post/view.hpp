#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/logbroker/post-test/post/request.hpp>
#include <handlers/logbroker/post-test/post/response.hpp>

namespace handlers::logbroker_post_test::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::logbroker_post_test::post
