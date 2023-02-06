#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/tests/v1/cleanup/scope/queue/post/request.hpp>
#include <handlers/tests/v1/cleanup/scope/queue/post/response.hpp>

namespace handlers::tests_v1_cleanup_scope_queue::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::tests_v1_cleanup_scope_queue::post
