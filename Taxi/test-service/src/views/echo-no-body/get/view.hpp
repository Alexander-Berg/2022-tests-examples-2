#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/echo-no-body/get/request.hpp>
#include <handlers/echo-no-body/get/response.hpp>

namespace handlers::echo_no_body::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::echo_no_body::get
