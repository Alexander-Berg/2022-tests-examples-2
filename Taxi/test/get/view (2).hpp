#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/v1/client_cache_projection/test/get/request.hpp>
#include <handlers/v1/client_cache_projection/test/get/response.hpp>

namespace handlers::v1_client_cache_projection_test::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::v1_client_cache_projection_test::get
