#pragma once

#include <handlers/dependencies_fwd.hpp>
#include <handlers/v1/config/get/request.hpp>
#include <handlers/v1/config/get/response.hpp>

namespace handlers::v1_config::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_config::get
