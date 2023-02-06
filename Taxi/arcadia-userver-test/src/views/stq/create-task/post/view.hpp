#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/stq/create-task/post/request.hpp>
#include <handlers/stq/create-task/post/response.hpp>

namespace handlers::stq_create_task::post {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::stq_create_task::post
