#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/tests/v1/handle-event/scope/queue/post/request.hpp>
#include <handlers/tests/v1/handle-event/scope/queue/post/response.hpp>

namespace handlers::tests_v1_handle_event_scope_queue::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::tests_v1_handle_event_scope_queue::post
