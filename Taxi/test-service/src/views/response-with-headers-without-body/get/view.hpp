#pragma once

#include <handlers/dependencies.hpp>
#include <handlers/response-with-headers-without-body/get/request.hpp>
#include <handlers/response-with-headers-without-body/get/response.hpp>

namespace handlers::response_with_headers_without_body::get {

class View {
 public:
  static Response Handle(Request&& request, Dependencies&& dependencies);
};

}  // namespace handlers::response_with_headers_without_body::get
