#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/sample/v1/action/put/request.hpp>
#include <handlers/sample/v1/action/put/response.hpp>

namespace handlers::sample_v1_action::put {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::sample_v1_action::put
