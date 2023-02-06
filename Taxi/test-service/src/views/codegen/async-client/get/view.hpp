#pragma once

#include <handlers/codegen/async-client/get/request.hpp>
#include <handlers/codegen/async-client/get/response.hpp>
#include <handlers/dependencies.hpp>

namespace handlers::codegen_async_client::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::codegen_async_client::get
